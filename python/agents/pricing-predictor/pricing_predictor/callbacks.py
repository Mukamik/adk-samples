from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.genai import types
import os
from typing import Optional, List, Any, Dict
from .pricing_engine import PricingEngine

def _calculate_and_format_summary(
    usage_metadata_list: List[Any], agent_name: str, is_final_summary: bool = False
) -> Dict[str, Any]:
    """A shared helper function to perform pricing calculations and formatting."""
    pricing_models_path = os.path.join(
        os.path.dirname(__file__), "pricing_models.json"
    )
    pricing_engine = PricingEngine(pricing_models_path)
    
    summary = pricing_engine.calculate_cost(usage_metadata_list, agent_name)
    
    cost = summary.get('total_cost', 0.0)
    in_ppm = summary.get('input_price_per_million', 0.0)
    out_ppm = summary.get('output_price_per_million', 0.0)
    in_tokens = summary.get('total_input_tokens', 0)
    out_tokens = summary.get('total_output_tokens', 0)
    total_tokens = in_tokens + out_tokens
    extrapolated_cost_1k = cost * 1000
    extrapolated_cost_1m = cost * 1_000_000

    calculation_str = (
        f"Calculation: (${in_ppm:,.2f}/1M) * {in_tokens} input + "
        f"(${out_ppm:,.2f}/1M) * {out_tokens} output"
    )

    if is_final_summary:
        title = "--- Final Workflow Summary ---"
        cost_label = "Total Estimated Cost for Workflow"
        token_label = "Total Tokens for Workflow"
    else:
        title = f"--- Pricing Summary for {agent_name} ---"
        cost_label = "Estimated Cost for this step"
        token_label = "Total Tokens for this step"

    summary_str = (
        f"\n\n{title}\n"
        f"{cost_label}: ${cost:.6f}\n"
        f"{calculation_str}\n"
        f"Thousand-run cost: ${extrapolated_cost_1k:.6f}\n"
        f"Million-run cost: ${extrapolated_cost_1m:.6f}\n"
    )
    
    return {"summary_str": summary_str, "total_tokens": total_tokens}

def add_step_pricing_summary(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> LlmResponse:
    """
    An after_model_callback that uses the shared helper to append a step summary.
    """
    if not llm_response.usage_metadata:
        return llm_response

    summary_data = _calculate_and_format_summary(
        [llm_response.usage_metadata], callback_context.agent_name
    )
    
    if llm_response.content and llm_response.content.parts:
        llm_response.content.parts.append(types.Part(text=summary_data["summary_str"]))
    else:
        llm_response.content = types.Content(parts=[types.Part(text=summary_data["summary_str"])])
    
    if "workflow_usage" not in callback_context.state:
        callback_context.state["workflow_usage"] = []
    callback_context.state["workflow_usage"].append({
        "agent_name": callback_context.agent_name,
        "usage_metadata": llm_response.usage_metadata
    })

    return llm_response

def add_final_summary(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    An after_agent_callback that uses the shared helper to create a final summary.
    """
    current_state = callback_context.state.to_dict()
    workflow_usage = current_state.get("workflow_usage", [])
    if not workflow_usage:
        return None

    all_usage_metadata = [step["usage_metadata"] for step in workflow_usage]

    summary_data = _calculate_and_format_summary(
        all_usage_metadata, callback_context.agent_name, is_final_summary=True
    )
    
    original_output = current_state.get("output", "")
    new_output_text = original_output + summary_data["summary_str"]
    
    return types.Content(
        parts=[types.Part(text=new_output_text)],
        role="model"
    )
