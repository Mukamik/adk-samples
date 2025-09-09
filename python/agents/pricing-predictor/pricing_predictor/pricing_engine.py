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
        if "up_to_tokens" not in tiers[0]:
            price_per_million = tiers[0].get("price_per_million", 0)
        else:
            sorted_tiers = sorted(tiers, key=lambda x: x['up_to_tokens'] if isinstance(x['up_to_tokens'], int) else float('inf'))
            for tier in sorted_tiers:
                tier_limit = tier['up_to_tokens']
                if isinstance(tier_limit, str) and tier_limit == 'inf': tier_limit = float('inf')
                if tokens <= tier_limit:
                    price_per_million = tier.get("price_per_million", 0)
                    break
        
        cost = (tokens / 1_000_000) * price_per_million
        return cost, price_per_million

    def calculate_cost(self, usage_metadata_list: List[Any], agent_name: str) -> Dict[str, Any]:
        total_input_tokens, total_output_tokens = 0, 0
        
        agent_pricing = self.pricing_models.get(agent_name, {})
        model_name = agent_pricing.get("model", "N/A")
        input_tiers = agent_pricing.get("input", [])
        output_tiers = agent_pricing.get("output", [])
        discount_rate = agent_pricing.get("discount_rate", 0.0)

        for metadata in usage_metadata_list:
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
