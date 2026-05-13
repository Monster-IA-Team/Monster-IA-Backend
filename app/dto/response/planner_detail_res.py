from pydantic import BaseModel
from uuid import UUID
from datetime import time, datetime
from typing import List, Any, Optional
from dto.response.task_detail_res import TaskDetailRes

class PlannerDetailRes(BaseModel):
    id: UUID
    wake_time: time
    sleep_time: time
    desired_count: Optional[int]
    created_at: Optional[datetime]
    planner: Any
    tasks: List[TaskDetailRes]