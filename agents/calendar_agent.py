import os
from pydantic import BaseModel
from sqlalchemy.orm import Session

from langchain_google_community import CalendarToolkit
from langchain_google_community.calendar.utils import build_resource_service
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from config.database import get_db
from models.google_calendar import GoogleCalendarToken
from pydantic_ai import Agent
from config.llm_config import gemini_model
from pydantic_ai.ext.langchain import tool_from_langchain


# --- SCOPES ---
SCOPES = ["https://www.googleapis.com/auth/calendar"]


# --- Schema for SearchEvents ---
class SearchEventsSchema(BaseModel):
    calendars_info: str
    min_datetime: str
    max_datetime: str
    max_results: int = 10
    order_by: str = "startTime"
    query: str | None = None
    single_events: bool = True


# --- DB Token Handling ---
def get_google_calendar_token(db: Session, user_id: str) -> GoogleCalendarToken:
    return db.query(GoogleCalendarToken).filter(GoogleCalendarToken.user_id == user_id).first()


def save_google_calendar_token(db: Session, user_id: str, creds: Credentials):
    db_token = get_google_calendar_token(db, user_id)
    if db_token:
        db_token.access_token = creds.token
        db_token.refresh_token = creds.refresh_token
        db_token.expires_at = creds.expiry
        db_token.token_uri = creds.token_uri
        db_token.client_id = creds.client_id
        db_token.client_secret = creds.client_secret
    else:
        db_token = GoogleCalendarToken(
            user_id=user_id,
            access_token=creds.token,
            refresh_token=creds.refresh_token,
            expires_at=creds.expiry,
            token_uri=creds.token_uri,
            client_id=creds.client_id,
            client_secret=creds.client_secret,
        )
        db.add(db_token)
    db.commit()


# --- Calendar Service Setup ---
def get_calendar_toolkit(user_id: str = "1") -> CalendarToolkit:
    with next(get_db()) as db:
        db_token = get_google_calendar_token(db, user_id)

        if not db_token:
            flow = InstalledAppFlow.from_client_secrets_file(
                os.getenv("GOOGLE_CREDENTIALS_JSON", "credentials.json"),
                scopes=SCOPES
            )
            creds = flow.run_local_server(port=0)
            save_google_calendar_token(db, user_id, creds)
        else:
            creds = Credentials(
                token=db_token.access_token,
                refresh_token=db_token.refresh_token,
                token_uri=db_token.token_uri,
                client_id=db_token.client_id,
                client_secret=db_token.client_secret,
                scopes=SCOPES,
            )

            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                save_google_calendar_token(db, user_id, creds)
    
    api_resource = build_resource_service(credentials=creds)
    return CalendarToolkit(api_resource=api_resource)


# --- Wrap into pydantic-ai agent ---
def get_calendar_tools(user_id: str = "1"):
    """Return all Google Calendar tools."""
    toolkit = get_calendar_toolkit(user_id)
    tools = toolkit.get_tools()
    return [tool_from_langchain(tool) for tool in tools]


calendar_agent = Agent(
    model=gemini_model,
    tools=get_calendar_tools(),
    system_prompt=(
        "You are a Google Calendar assistant. "
        "Use `CalendarSearchEvents` to check upcoming events. "
        "Use `CalendarCreateEvent` only when explicitly asked to schedule something. "
        "Use `CalendarUpdateEvent` when modifying existing events. "
        "Use `CalendarDeleteEvent` or `CalendarMoveEvent` when asked to remove or relocate events. "
        "Use `GetCalendarsInfo` to see available calendars. "
        "Use `GetCurrentDatetime` for scheduling context."
    ),
)