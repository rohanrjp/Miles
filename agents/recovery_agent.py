from pydantic_ai import Agent
from config.llm_config import gemini_model
from schemas import RecoveryAdvice

recovery_agent = Agent(
    model=gemini_model, 
    output_type=RecoveryAdvice,
    system_prompt="""You are an expert running recovery coach.
Analyze the following JSON data which contains a user's runs from the past week.
Based on this data, determine if today is a good day for a run, provide clear reasoning, and suggest an appropriate activity.

The user's run data is:
{input}
"""
)

