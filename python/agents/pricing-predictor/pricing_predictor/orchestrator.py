from google.adk.agents import SequentialAgent
from google.genai import types
import os
from .pricing_engine import PricingEngine

class PricingSequentialAgent(SequentialAgent):
    """A custom SequentialAgent that adds cost calculation to the workflow result."""

    def run(self, prompt: str, video_file_path: str, **kwargs) -> str:
        if not os.path.exists(video_file_path):
            return f"Error: Video file not found at {video_file_path}"

        video_part = types.Part.from_uri(uri=video_file_path, mime_type="video/mp4")
        
        # The SequentialAgent will run the sub-agents in order, passing the
        # output of one step as the `prompt` to the next.
        final_llm_response = super().run(
            prompt=prompt,
            media=[video_part]
        )

        all_usage_metadata = []
        if final_llm_response.usage_metadata:
            all_usage_metadata.append(final_llm_response.usage_metadata)
        
        pricing_models_path = os.path.join(os.path.dirname(__file__), "pricing_models.json")
        pricing_engine = PricingEngine(pricing_models_path)
        pricing_summary = pricing_engine.calculate_cost(all_usage_metadata)

        final_output_str = (
            f"{final_llm_response.text}\n\n"
            "--- Pricing Summary ---\n"
            f"Model: {pricing_summary.get('model_used', 'N/A')}\n"
            f"Total Input Tokens: {pricing_summary.get('total_input_tokens', 0)}\n"
            f"Total Output Tokens: {pricing_summary.get('total_output_tokens', 0)}\n"
            f"Total Tokens: {pricing_summary.get('total_tokens', 0)}\n"
            f"Total Estimated Cost: {pricing_summary.get('total_cost', '$0.00')}\n"
        )
        return final_output_str
