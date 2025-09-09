from google.adk import Agent

video_agent = Agent(
    name="video_analyzer",
    description="Analyzes a video file based on the user's prompt.",
    instruction="You are an expert video analyst. Your task is to analyze the provided video file and answer the user's query about its contents.",
    model="gemini-2.5-pro",
)
