"""Pricing Predictor Agent that wraps a sequential workflow to add cost estimation."""

from .orchestrator import PricingSequentialAgent
from .sub_agents.video_agent import video_agent
from .sub_agents.audio_agent import audio_agent

# Define the sequential workflow for detecting a cat in a video.
animal_detector_workflow = PricingSequentialAgent(
    name="pricing_predictor",
    description=(
        "Analyzes a video to detect a cat and its meow, then provides a cost"
        " estimate for the entire workflow."
    ),
    sub_agents=[video_agent, audio_agent],
)
