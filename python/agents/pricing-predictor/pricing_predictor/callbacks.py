from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.genai import types
import os
from .pricing_engine import PricingEngine

def add_pricing_summary(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> LlmResponse:
    """
    An after_model_callback that calculates the cost of a single LLM call
    and appends a pricing summary to the response.
    """
    all_usage_metadata = []
    
    # Get the model name from the agent that was run.
    # Note: This assumes the agent name in the pricing model matches.
    # A more robust implementation might map agent names to model names.
    model_name = callback_context.agent_name

    # Get the usage metadata from the current LLM response.
    if llm_response.usage_metadata:
        all_usage_metadata.append(llm_response.usage_metadata)

    # Calculate the cost.
    pricing_models_path = os.path.join(
        os.path.dirname(__file__), "pricing_models.json"
    )
    pricing_engine = PricingEngine(pricing_models_path)
    pricing_summary = pricing_engine.calculate_cost(
        all_usage_metadata, model_name
    )

    pricing_summary_str = (
        "\n\n--- Pricing Summary ---"
        f"Model: {pricing_summary.get('model_used', 'N/A')}"
        f"Total Input Tokens: {pricing_summary.get('total_input_tokens', 0)}"
        f"Total Output Tokens: {pricing_summary.get('total_output_tokens', 0)}"
        f"Total Tokens: {pricing_summary.get('total_tokens', 0)}"
        f"Total Estimated Cost: {pricing_summary.get('total_cost', '$0.00')}"
    )

    # Append the pricing summary as a new part to the final response.
    if llm_response.content and llm_response.content.parts:
        llm_response.content.parts.append(types.Part(text=pricing_summary_str))
    else:
        llm_response.content = types.Content(parts=[types.Part(text=pricing_summary_str)])

    return llm_response