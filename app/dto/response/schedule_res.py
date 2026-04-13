from pydantic import BaseModel
from typing import List
from dto.response.drink_session_res import DrinkSessionResponse

class ScheduleResponse(BaseModel):
    drink_sessions: List[DrinkSessionResponse]
    covered_hours: int
    effectiveness: int