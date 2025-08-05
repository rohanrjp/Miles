from __future__ import annotations as _annotations

import asyncio
from dataclasses import dataclass, field
from typing import Union

from pydantic import BaseModel, EmailStr

from pydantic_ai import Agent
from pydantic_graph import BaseNode, End, Graph, GraphRunContext

from agents import team_leader, general_assistant, weather_assistant, strava_coach

from models.domain import User,State


# --- Node Definitions ---

@dataclass
class StravaCoach(BaseNode[State]):
    """Handles requests related to running and Strava data."""
    async def run(self, ctx: GraphRunContext[State]) -> End:
        print("✅ Executing StravaCoach Node...")
        result = await strava_coach.run(ctx.state.input_request)
        ctx.state.strava_response = result.output
        print(f"   -> Fetched Strava Data: {ctx.state.strava_response}")
        return End(ctx.state.strava_response)

@dataclass
class WeatherAssistant(BaseNode[State]):
    """Handles requests about the weather."""
    async def run(self, ctx: GraphRunContext[State]) -> End:
        print("✅ Executing WeatherAssistant Node...")
        # In a real scenario, you'd call a weather API.
        result = await weather_assistant.run(ctx.state.input_request)
        ctx.state.weather_response = result.output
        print(f"   -> Generated Weather Response: {ctx.state.weather_response}")
        return End(ctx.state.weather_response)

@dataclass
class GeneralAssistant(BaseNode[State]):
    """Handles all other general queries."""
    async def run(self, ctx: GraphRunContext[State]) -> End:
        print("✅ Executing GeneralAssistant Node...")
        result = await general_assistant.run(ctx.state.input_request)
        ctx.state.general_response = result.output
        print(f"   -> Generated General Response: {ctx.state.general_response}")
        return End(ctx.state.general_response)

@dataclass
class TeamLeader(BaseNode[State]):
    """The first node that routes the request to the correct assistant."""
    async def run(
        self, ctx: GraphRunContext[State]
    ) -> Union[StravaCoach, WeatherAssistant, GeneralAssistant]:
        print("Executing TeamLeader Node...")

        # Use the agent to decide which node to use next
        prompt = (
            f"Given the user request: '{ctx.state.input_request}', "
            "which tool should I use? The options are: "
            "'StravaCoach' for running data, "
            "'WeatherAssistant' for weather queries, or "
            "'GeneralAssistant' for anything else. "
            "Respond with only the name of the tool."
        )
        result = await team_leader.run(prompt)
        decision = str(result.output.appropriate_node)
        ctx.state.team_leader_decision = decision
        print(f"   -> TeamLeader Decision: '{decision}'")

        # Return an instance of the chosen node
        if "StravaCoach" in decision:
            return StravaCoach()
        elif "WeatherAssistant" in decision:
            return WeatherAssistant()
        else:
            return GeneralAssistant()

# --- Graph Execution ---

async def run_assistant(input_request: str, user: User):
    """Helper function to initialize and run the graph for a given request."""
    print(f"--- Running Graph for: '{input_request}' ---")
    initial_state = State(user=user, input_request=input_request)

    # The graph must be aware of all possible nodes it might need to execute.
    assistant_graph = Graph(
        nodes=(TeamLeader, StravaCoach, WeatherAssistant, GeneralAssistant)
    )

    # Start the graph execution with the TeamLeader node
    final_state = await assistant_graph.run(TeamLeader(), state=initial_state)

    print("\nFinal State Dump:")
    print(final_state)
    print("\n" + "="*60 + "\n")


async def main():
    rohan = User(
        name='Rohan Paul',
        email='rohan1007rjp@gmail.com',
        interests=['Python', 'Go'],
    )

    # Example 1: User asks for run data
    await run_assistant("I want my latest run data from Strava", user=rohan)

    # Example 2: User asks for specific activity details (replace with a real activity ID from your Strava)
    # await run_assistant("Tell me more about activity 123456789", user=rohan)

    # Example 3: User asks for athlete profile
    await run_assistant("What is my Strava profile information?", user=rohan)

    # Example 4: User asks for weekly summary
    await run_assistant("What is my weekly Strava summary?", user=rohan)

    # Example 5: User asks for progress trend
    await run_assistant("What is my progress trend for running?", user=rohan)

    # Example 6: User asks for the weather
    await run_assistant("What's the weather like in London tomorrow?", user=rohan)

    # Example 7: User asks a general question
    await run_assistant("Can you list the top five highest-grossing animated films of 2024?", user=rohan)


if __name__ == "__main__":
    asyncio.run(main())