from pydantic_ai import Agent
from config.llm_config import gemini_model
from schemas import RecoveryAdvice

recovery_agent = Agent(
    model=gemini_model, 
    output_type=RecoveryAdvice,
    system_prompt="""
Given the following JSON data of runs from the past week:
{run_data}

Analyze the user's activity level (frequency, total distance/duration, intensity if available).
Based on standard recovery principles, determine if today is a good day for a run.
Provide clear reasoning and suggest an appropriate activity for today.
"""
)

