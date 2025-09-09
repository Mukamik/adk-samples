from google.adk import Agent
from ..callbacks import add_step_pricing_summary

audio_agent = Agent(
    name="audio_analyzer",
    description="Analyzes the audio based on the video analysis and the user's prompt.",
    instruction=(
        "You are an expert audio analyst. You will receive the output of a prior video analysis as your prompt. "
        "Your task is to analyze the audio of the same video to provide additional details that complement the video analysis."
    ),
    model="gemini-2.5-pro",
    after_model_callback=add_step_pricing_summary,
)
