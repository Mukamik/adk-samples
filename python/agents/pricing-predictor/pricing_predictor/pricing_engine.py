import json
from typing import Any, Dict, List

class PricingEngine:
    def __init__(self, models_file: str):
        with open(models_file, 'r') as f:
            self.pricing_models = json.load(f)

    def _get_tiered_price(self, tiers: List[Dict[str, Any]], tokens: int) -> float:
        if not tiers: return 0.0
        if "up_to_tokens" not in tiers[0]:
            price_per_million = tiers[0].get("price_per_million", 0)
            return (tokens / 1_000_000) * price_per_million
        sorted_tiers = sorted(tiers, key=lambda x: x['up_to_tokens'] if isinstance(x['up_to_tokens'], int) else float('inf'))
        for tier in sorted_tiers:
            tier_limit = tier['up_to_tokens']
            if isinstance(tier_limit, str) and tier_limit == 'inf': tier_limit = float('inf')
            if tokens <= tier_limit:
                price_per_million = tier.get("price_per_million", 0)
                return (tokens / 1_000_000) * price_per_million
        return 0.0

    def calculate_cost(self, usage_metadata_list: List[Any]) -> Dict[str, Any]:
        total_input_tokens, total_output_tokens, total_cost = 0, 0, 0.0
        model_name = "gemini-2.5-pro"
        model_pricing = self.pricing_models.get(model_name, {})
        input_tiers, output_tiers = model_pricing.get("input", []), model_pricing.get("output", [])
        for metadata in usage_metadata_list:
            input_tokens, output_tokens = metadata.prompt_token_count, metadata.candidates_token_count
            total_input_tokens += input_tokens
            total_output_tokens += output_tokens
            total_cost += self._get_tiered_price(input_tiers, input_tokens)
            total_cost += self._get_tiered_price(output_tiers, output_tokens)
        return {
            "model_used": model_name, "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens, "total_tokens": total_input_tokens + total_output_tokens,
            "total_cost": f"${total_cost:.6f}"
        }
