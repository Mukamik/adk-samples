import json
import os
from google.adk import Agent

class PricingInfoAgent(Agent):
    def run(self, **kwargs) -> str:
        """Loads and formats the pricing models from the JSON file."""
        try:
            pricing_models_path = os.path.join(
                os.path.dirname(__file__), "pricing_models.json"
            )
            with open(pricing_models_path, "r") as f:
                pricing_data = json.load(f)
            
            # Format the JSON data into a readable string.
            return json.dumps(pricing_data, indent=2)
        except Exception as e:
            return f"Error loading pricing information: {e}"

pricing_info_agent = PricingInfoAgent(
    name="pricing_info_viewer",
    description="Displays the current pricing models used by the Pricing Predictor."
)
