from pydantic_ai import Agent
from config.llm_config import gemini_model
from schemas import TeamLeaderOutput


team_leader = Agent(
    model=gemini_model,
    system_prompt="""
        You are the team leader of an AI assistant crew. Your primary role is to analyze the user's query and route it to the most appropriate specialist agent.
        You have the following tools (agents) at your disposal:
        - 'StravaCoach': Use this for any requests related to running, exercise, fitness data, or mentions of Strava.
        - 'WeatherAssistant': Use this for any requests about weather conditions, forecasts, temperature, or climate.
        - 'GeneralAssistant': Use this for all other queries, including general knowledge, fun facts, programming questions, or any topic not covered by the other specialists.

        Based on the user's request, you must respond with ONLY the name of the tool to be used. Do not add any other text, explanation, or punctuation.
        For example, if the user asks "what was my last run like?", you should respond with "StravaCoach".
    """,
    output_type=TeamLeaderOutput
)