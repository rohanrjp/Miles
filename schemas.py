from pydantic import BaseModel,Field
    
class TeamLeaderOutput(BaseModel):
    appropriate_node:str
    
class RecoveryAdvice(BaseModel):
    """Model for providing recovery and running advice."""
    is_good_day_to_run: bool = Field(..., description="A boolean indicating if today is a good day for a run.")
    reasoning: str = Field(..., description="A detailed explanation for the recommendation.")
    suggested_activity: str = Field(..., description="A suggested activity for the day (e.g., 'Easy 3km run', 'Rest day', 'Stretching').")
