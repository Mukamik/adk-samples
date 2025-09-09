"""Pricing Predictor Agent that orchestrates a sequential workflow."""

from google.adk.agents import SequentialAgent
from .callbacks import add_final_summary
from .sub_agents.video_agent import video_agent
from .sub_agents.audio_agent import audio_agent

# The root_agent is a SequentialAgent. The pricing logic for each step is
# handled by the `after_model_callback` on the individual sub-agents.
# The final summary is handled by the `after_agent_callback` on the
# SequentialAgent itself.
root_agent = SequentialAgent(
    name="pricing_predictor",
    description=(
        "Analyzes a video to answer a user's prompt, then provides a cost"
        " estimate for each step in the workflow."
    ),
    sub_agents=[video_agent, audio_agent],
    after_agent_callback=add_final_summary,
)
