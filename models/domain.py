from dataclasses import dataclass,field
from pydantic import EmailStr
from schemas import RecoveryAdvice
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class User:
    name: str
    email: EmailStr
    interests: list[str]
    home_city:str

@dataclass
class Memory:
    id: str
    memory: str
    hash: str
    created_at: datetime
    updated_at: Optional[datetime]
    metadata: Dict[str, Any]
    user_id: str

@dataclass
class State:
    user: User
    input_request: str
    team_leader_decision: str = ""
    strava_response: dict = field(default_factory=dict)
    weather_response: str = ""
    general_response: str = ""
    calendar_response: str = ""
    telegram_output:str = ""
    recovery_advice: RecoveryAdvice | None = None
    calendar_prompt:str = ""
    memories:List[Memory] = field(default_factory=list)
