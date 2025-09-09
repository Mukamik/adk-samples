"""Pricing Predictor Agent that orchestrates a sequential workflow."""

from google.adk.agents import SequentialAgent
from .sub_agents.video_agent import video_agent
from .sub_agents.audio_agent import audio_agent

# The root_agent is a simple SequentialAgent. The pricing logic will be
# attached as a callback on the final agent in the sequence.
root_agent = SequentialAgent(
    name="pricing_predictor",
    description=(
        "Analyzes a video to answer a user's prompt, then provides a cost"
        " estimate for the entire workflow."
    ),
    sub_agents=[video_agent, audio_agent],
)
