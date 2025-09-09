import json
from typing import Any, Dict, List

class PricingEngine:
    def __init__(self, models_file: str):
        with open(models_file, 'r') as f:
            self.pricing_models = json.load(f)

    def _get_price_for_tokens(self, tiers: List[Dict[str, Any]], tokens: int) -> (float, float):
        """
        Calculates the cost for a set of tokens and returns the cost and the
        effective price per million tokens used.
        """
        if not tiers: return 0.0, 0.0
        
        price_per_million = 0.0
        tier_key = None
        if "up_to_tokens" in tiers[0]:
            tier_key = "up_to_tokens"
        elif "context_window_tokens" in tiers[0]:
            tier_key = "context_window_tokens"

        if tier_key:
            sorted_tiers = sorted(tiers, key=lambda x: x[tier_key] if isinstance(x[tier_key], int) else float('inf'))
            for tier in sorted_tiers:
                tier_limit = tier[tier_key]
                if isinstance(tier_limit, str) and tier_limit == 'inf': tier_limit = float('inf')
                if tokens <= tier_limit:
                    price_per_million = tier.get("price_per_million", 0)
                    break
        else:
            price_per_million = tiers[0].get("price_per_million", 0)
        
        cost = (tokens / 1_000_000) * price_per_million
        return cost, price_per_million

    def calculate_cost(self, usage_metadata_list: List[Any], model_name: str, input_type: str = 'text', discount_rate: float = 0.0) -> Dict[str, Any]:
        total_input_tokens, total_output_tokens = 0, 0
        
        model_pricing = self.pricing_models.get(model_name, {})
        unit = model_pricing.get("unit", "token")

        if unit == "token":
            input_tiers = model_pricing.get("input", [])
            if isinstance(input_tiers, dict):
                input_tiers = input_tiers.get(input_type, [])
            output_tiers = model_pricing.get("output", [])

            for metadata in usage_metadata_list:
                if isinstance(metadata, dict):
                    total_input_tokens += metadata.get('prompt_token_count', 0)
                    total_output_tokens += metadata.get('candidates_token_count', 0)
                else:
                    total_input_tokens += metadata.prompt_token_count
                    total_output_tokens += metadata.candidates_token_count
            
            input_cost, effective_input_price = self._get_price_for_tokens(input_tiers, total_input_tokens)
            output_cost, effective_output_price = self._get_price_for_tokens(output_tiers, total_output_tokens)
            
            subtotal = input_cost + output_cost
            discount_amount = subtotal * discount_rate
            total_cost = subtotal - discount_amount

            return {
                "model_used": model_name,
                "total_input_tokens": total_input_tokens,
                "total_output_tokens": total_output_tokens,
                "total_tokens": total_input_tokens + total_output_tokens,
                "subtotal": subtotal,
                "discount_rate": discount_rate,
                "discount_amount": discount_amount,
                "total_cost": total_cost,
                "input_price_per_million": effective_input_price,
                "output_price_per_million": effective_output_price,
            }
        elif unit == "image":
            # This is a placeholder for image pricing logic
            return {"total_cost": 0}
        elif unit == "second":
            # This is a placeholder for audio/video pricing logic
            return {"total_cost": 0}
        
        return {"total_cost": 0}
