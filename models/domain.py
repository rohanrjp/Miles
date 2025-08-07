from dataclasses import dataclass,field
from pydantic import EmailStr


@dataclass
class User:
    name: str
    email: EmailStr
    interests: list[str]

@dataclass
class State:
    user: User
    input_request: str
    team_leader_decision: str = ""
    strava_response: dict = field(default_factory=dict)
    weather_response: str = ""
    general_response: str = ""
    telegram_output:str = ""
