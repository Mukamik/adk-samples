from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.genai import types
import os
from .pricing_engine import PricingEngine

def add_pricing_summary(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> LlmResponse:
    """
    An after_model_callback that calculates the cost for a single agent step
    and appends a labeled pricing summary to the response.
    """
    if not llm_response.usage_metadata:
        return llm_response

    # Calculate the cost for this specific step only.
    pricing_models_path = os.path.join(
        os.path.dirname(__file__), "pricing_models.json"
    )
    pricing_engine = PricingEngine(pricing_models_path)
    pricing_summary = pricing_engine.calculate_cost(
        [llm_response.usage_metadata], callback_context.agent_name
    )

    pricing_summary_str = (
        f"\n\n--- Pricing Summary for {callback_context.agent_name} ---\n"
        f"Model: {pricing_summary.get('model_used', 'N/A')}\n"
        f"Input Tokens: {pricing_summary.get('total_input_tokens', 0)}\n"
        f"Output Tokens: {pricing_summary.get('total_output_tokens', 0)}\n"
        f"Estimated Cost for this step: {pricing_summary.get('total_cost', '$0.00')}\n"
    )

    # Append the pricing summary as a new part to the final response.
    if llm_response.content and llm_response.content.parts:
        llm_response.content.parts.append(types.Part(text=pricing_summary_str))
    else:
        llm_response.content = types.Content(parts=[types.Part(text=pricing_summary_str)])

    return llm_response