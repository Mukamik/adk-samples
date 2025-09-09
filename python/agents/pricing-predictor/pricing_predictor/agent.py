"""Pricing Predictor Agent that orchestrates a sequential workflow."""

from google.adk.agents import SequentialAgent
from .sub_agents.video_agent import video_agent
from .sub_agents.audio_agent import audio_agent

# The root_agent is a simple SequentialAgent. The pricing logic is handled
# by the `after_model_callback` on each individual sub-agent.
root_agent = SequentialAgent(
    name="pricing_predictor",
    description=(
        "Analyzes a video to answer a user's prompt, then provides a cost"
        " estimate for each step in the workflow."
    ),
    sub_agents=[video_agent, audio_agent],
)