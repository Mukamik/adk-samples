from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.genai import types
import os
from typing import Optional
from .pricing_engine import PricingEngine

def add_step_pricing_summary(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> LlmResponse:
    """
    An after_model_callback that calculates the cost for a single agent step,
    appends a labeled pricing summary as a NEW PART, and writes data to the state.
    """
    if not llm_response.usage_metadata:
        return llm_response

    pricing_models_path = os.path.join(
        os.path.dirname(__file__), "pricing_models.json"
    )
    pricing_engine = PricingEngine(pricing_models_path)
    step_summary = pricing_engine.calculate_cost(
        [llm_response.usage_metadata], callback_context.agent_name
    )
    step_cost_float = step_summary.get('total_cost', 0.0)
    extrapolated_cost_1k = step_cost_float * 1000
    extrapolated_cost_1m = step_cost_float * 1_000_000

    step_summary_str = (
        f"\n\n--- Pricing Summary for {callback_context.agent_name} ---\n"
        f"Model: {step_summary.get('model_used', 'N/A')}\n"
        f"Input Tokens for this step: {step_summary.get('total_input_tokens', 0)}\n"
        f"Output Tokens for this step: {step_summary.get('total_output_tokens', 0)}\n"
        f"Estimated Cost for this step: ${step_cost_float:.6f}\n"
        f"Thousand-run cost: ${extrapolated_cost_1k:.6f}\n"
        f"Million-run cost: ${extrapolated_cost_1m:.6f}\n"
    )
    
    if llm_response.content and llm_response.content.parts:
        llm_response.content.parts.append(types.Part(text=step_summary_str))
    else:
        llm_response.content = types.Content(parts=[types.Part(text=step_summary_str)])

    if "total_tokens_in_workflow" not in callback_context.state:
        callback_context.state["total_tokens_in_workflow"] = []
    callback_context.state["total_tokens_in_workflow"].append(
        step_summary.get('total_tokens', 0)
    )

    return llm_response

def add_final_summary(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    An after_agent_callback that calculates the total cost of the entire
    workflow using data from the state, and returns new Content to replace
    the agent's original output with a final summary.
    """
    current_state = callback_context.state.to_dict()
    total_tokens_list = current_state.get("total_tokens_in_workflow", [])
    if not total_tokens_list:
        return None

    total_tokens = sum(total_tokens_list)

    pricing_models_path = os.path.join(
        os.path.dirname(__file__), "pricing_models.json"
    )
    pricing_engine = PricingEngine(pricing_models_path)
    
    model_pricing = pricing_engine.pricing_models.get(callback_context.agent_name, {})
    input_tiers = model_pricing.get("input", [])
    
    price_per_million = input_tiers[0].get("price_per_million", 0) if input_tiers else 0
    total_cost_float = (total_tokens / 1_000_000) * price_per_million
    extrapolated_cost_1k = total_cost_float * 1000
    extrapolated_cost_1m = total_cost_float * 1_000_000

    final_summary_str = (
        "\n\n--- Final Workflow Summary ---\n"
        f"Total Tokens for Workflow: {total_tokens}\n"
        f"Total Estimated Cost for Workflow: ${total_cost_float:.6f}\n"
        f"Thousand-run cost: ${extrapolated_cost_1k:.6f}\n"
        f"Million-run cost: ${extrapolated_cost_1m:.6f}\n"
    )
    
    original_output = current_state.get("output", "")
    
    new_output_text = original_output + final_summary_str
    
    return types.Content(
        parts=[types.Part(text=new_output_text)],
        role="model"
    )
