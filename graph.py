from __future__ import annotations as _annotations

import asyncio
import datetime
from dataclasses import dataclass, field
from typing import Union

from pydantic import BaseModel, EmailStr

from pydantic_ai import Agent
from pydantic_graph import BaseNode, End, Graph, GraphRunContext

from agents import team_leader, general_assistant, weather_assistant, strava_coach , telegram_response_agent, recovery_agent, calendar_agent

from models.domain import User,State

from schemas import RecoveryAdvice

from mem0 import MemoryClient
from config.config import settings

memory_client=MemoryClient(api_key=settings.MEM0_API_KEY)

# --- Node Definitions ---

@dataclass
class MemoryNode(BaseNode[State]):
    """Handles long-term memory retrieval and storage with Mem0."""

    async def run(self, ctx: GraphRunContext[State]) -> Union[TeamLeader, End]:
        user_id = ctx.state.user.name

        if ctx.state.telegram_output:
            print("✅ Executing MemoryNode (Storage)...")
            
            messages_to_add = [
                {"role": "user", "content": ctx.state.input_request},
                {"role": "assistant", "content": ctx.state.telegram_output}
            ]
            
            memory_client.add(
                messages=messages_to_add,
                user_id=user_id,
                metadata={"source": "telegram", "query": ctx.state.input_request},
            )
            print("   -> Memory stored successfully.")
            return End(ctx.state.telegram_output)

        print("✅ Executing MemoryNode (Retrieval)...")
        if not ctx.state.memories:  
            past_memories = memory_client.search(
                query=ctx.state.input_request, user_id=user_id
            )

            if isinstance(past_memories, dict) and "results" in past_memories:
                ctx.state.memories = past_memories["results"]
            elif isinstance(past_memories, list):
                ctx.state.memories = past_memories
            else:
                ctx.state.memories = []

            print(f"   -> Retrieved {len(ctx.state.memories)} memories.")

        return TeamLeader()

@dataclass
class StravaCoach(BaseNode[State]):
    """Handles requests related to running and Strava data."""
    async def run(self, ctx: GraphRunContext[State]) -> Union[RecoveryNode, TelegramResponse]:
        print("✅ Executing StravaCoach Node...")
        today = datetime.date.today().isoformat()  
        
        prompt = (
            f"Today is {today}. "
            f"Request: {ctx.state.input_request}"
        )
        
        result = await strava_coach.run(prompt)
        ctx.state.strava_response = result.output
        print(f"   -> Fetched Strava Data: {ctx.state.strava_response}")
        
        if "RecoveryAnalysis" in ctx.state.team_leader_decision:
            print("   -> Handing off to RecoveryNode for analysis.")
            return RecoveryNode() 
        else:
            print("   -> Handing off to TelegramResponse for direct output.")
            return TelegramResponse()

@dataclass
class TelegramResponse(BaseNode[State]):
    """Formats Strava/Weather/Recovery results into a Telegram-friendly message."""
    
    async def run(self, ctx: GraphRunContext[State]) -> MemoryNode:
        print("✅ Executing TelegramResponse Node...")
        
        inputs = []
        if ctx.state.strava_response:
            inputs.append(f"Strava data: {ctx.state.strava_response}")
        if ctx.state.recovery_advice:
            inputs.append(f"Recovery advice: {ctx.state.recovery_advice}")
        if ctx.state.weather_response:
            inputs.append(f"Weather update: {ctx.state.weather_response}")
        if ctx.state.general_response:
            inputs.append(f"General response: {ctx.state.general_response}")
        if ctx.state.calendar_response:
            inputs.append(f"Calendar update: {ctx.state.calendar_response}")

        if not inputs:
            inputs.append("No data from assistants, just send a motivational nudge!")

        combined_input = "\n".join(inputs)
        result = await telegram_response_agent.run(combined_input)
        ctx.state.telegram_output = result.output
        
        print(f"   -> Telegram output prepared: {ctx.state.telegram_output}")
        
        return MemoryNode()



@dataclass
class WeatherAssistant(BaseNode[State]):
    """Handles requests about the weather."""
    async def run(self, ctx: GraphRunContext[State]) -> TelegramResponse:
        print("✅ Executing WeatherAssistant Node...")
        # In a real scenario, you'd call a weather API.
        result = await weather_assistant.run(ctx.state.input_request)
        ctx.state.weather_response = result.output
        print(f"   -> Generated Weather Response: {ctx.state.weather_response}")
        return TelegramResponse()


@dataclass
class  CalendarAssistant(BaseNode[State]):
    """Handles requests about the calendar."""
    async def run(self, ctx: GraphRunContext[State]) -> Union[End,TelegramResponse]:
        print("✅ Executing CalendarAssistant Node...")
        if ctx.state.calendar_prompt == '':
            result = await calendar_agent.run(ctx.state.input_request)
            ctx.state.calendar_response = result.output
            print(f"   -> Generated Calendar Response: {ctx.state.calendar_response}")
            return End(ctx.state.calendar_response)
        else:
            result = await calendar_agent.run(ctx.state.calendar_prompt) 
            ctx.state.calendar_response = result.output
            print(f"   -> Generated Calendar Response: {ctx.state.calendar_response}")
            return TelegramResponse()  
        

@dataclass
class GeneralAssistant(BaseNode[State]):
    """Handles all other general queries."""
    async def run(self, ctx: GraphRunContext[State]) -> TelegramResponse:
        print("✅ Executing GeneralAssistant Node...")
        result = await general_assistant.run(ctx.state.input_request)
        ctx.state.general_response = result.output
        print(f"   -> Generated General Response: {ctx.state.general_response}")
        return TelegramResponse()

@dataclass
class TeamLeader(BaseNode[State]):
    """The first node that routes the request to the correct assistant."""
    async def run(
        self, ctx: GraphRunContext[State]
    ) -> Union[StravaCoach, WeatherAssistant, GeneralAssistant, CalendarAssistant]:
        print("Executing TeamLeader Node...")

        # Updated prompt to include the new analysis task
        prompt = (
            f"Given the user request: '{ctx.state.input_request}', "
            "which tool should I use? The options are: "
            "'StravaCoach' for retrieving running history/data, "
            "'RecoveryAnalysis' to analyze run history and decide if today is a good day to run, "
            "'WeatherAssistant' for weather queries, "
            "'CalendarAssistant' for calendar queries, or "
            "'GeneralAssistant' for anything else. "
            "Respond with only the name of the tool."
        )
        result = await team_leader.run(prompt)
        decision = str(result.output.appropriate_node)
        ctx.state.team_leader_decision = decision
        print(f"   -> TeamLeader Decision: '{decision}'")

        if "StravaCoach" in decision or "RecoveryAnalysis" in decision:
            return StravaCoach()
        elif "WeatherAssistant" in decision:
            return WeatherAssistant()
        elif "CalendarAssistant" in decision:
            return CalendarAssistant()
        else:
            return GeneralAssistant()


@dataclass
class RecoveryNode(BaseNode[State]):
    """Analyzes recent run data to provide recovery advice."""
    async def run(self, ctx: GraphRunContext[State]) -> CalendarAssistant:
        print("✅ Executing RecoveryNode...")
        if not ctx.state.strava_response:
            return End("⚠️ I need Strava data to provide recovery advice, but I couldn't find any.")

        result = await recovery_agent.run(ctx.state.strava_response)
        advice = result.output

        ctx.state.recovery_advice = advice
        print(f"   -> Generated Recovery Advice: {advice.is_good_day_to_run}, Reason: {advice.reasoning}")

        # Schedule event based on recovery advice
        today = datetime.date.today()
        start_time = datetime.datetime.combine(today, datetime.time(20, 0)).isoformat()
        end_time = datetime.datetime.combine(today, datetime.time(21, 0)).isoformat()

        event_summary = "Run" if advice.is_good_day_to_run else "Gym"

        today = datetime.date.today().strftime("%Y-%m-%d")

        ctx.state.calendar_prompt = (
            f"Create a calendar event with the following details:\n"
            f"- Summary: {event_summary}\n"
            f"- Start datetime: {today}T20:00:00+05:30\n"
            f"- End datetime: {today}T21:00:00+05:30\n"
            f"- Timezone: Asia/Kolkata\n"
            f"- Location: Chennai\n"
            f"- Description: {event_summary} (created automatically)\n"
            f"- Reminders: popup 60 minutes before\n"
            f"- Conference data: True\n"
            f"- Color ID: 5\n"
        )
        

        # Format the response for Telegram
        strava_summary = ctx.state.strava_response
        recovery_summary = (
            f"**Recommendation:** "
            f"{'A run sounds like a great idea! ✅' if advice.is_good_day_to_run else 'Today should be a rest day. 😴'}\n\n"
            f"**Reasoning:** {advice.reasoning}\n\n"
            f"**Suggested Activity:** {advice.suggested_activity}"
        )

        calendar_confirmation = f"I have scheduled a {event_summary.lower()} session for you today from 8 PM to 9 PM."

        formatted_message = (
            f"Here is your daily summary:\n\n"
            f"**Strava Summary:**\n{strava_summary}\n\n"
            f"**Recovery Advice:**\n{recovery_summary}\n\n"
            f"**Calendar:**\n{calendar_confirmation}"
        )

        ctx.state.strava_response = formatted_message

        return CalendarAssistant()
    
# --- Graph Execution ---

async def run_graph(input_request: str, user: User):
    print(f"--- Running Graph for: '{input_request}' ---")
    initial_state = State(user=user, input_request=input_request)

    assistant_graph = Graph(
        nodes=(MemoryNode, TeamLeader, StravaCoach, WeatherAssistant, GeneralAssistant, RecoveryNode, CalendarAssistant, TelegramResponse)
    )

    try:
        final_state = await assistant_graph.run(MemoryNode(), state=initial_state)
        print("\nFinal State Dump:")
        print(final_state)
        print("\n" + "="*60 + "\n")
        return final_state.output or "✅ Done! No output."
    except Exception as e:
        print("⚠️ Graph execution error:", e)
        return "⚠️ Sorry, something went wrong while processing your request."