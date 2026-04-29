from pydantic import BaseModel
import uuid
from datetime import datetime, time
from typing import Optional

class PlannerTableRes(BaseModel):
    id: uuid.UUID
    wake_time: time
    sleep_time: time
    desired_count: Optional[int]
    created_at: datetime
    sessions_count: int