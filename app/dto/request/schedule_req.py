from pydantic import BaseModel
from typing import List
from datetime import time
from dto.request.task_interval_req import TaskIntervalRequest

class ScheduleRequest(BaseModel):
    wake: time
    sleep: time
    tasks: List[TaskIntervalRequest]
    monster_count: int