from pydantic import BaseModel
from datetime import time
from typing import Optional
from uuid import UUID

class TaskDetailRes(BaseModel):
    id: UUID
    title: Optional[str]
    start_time: time
    end_time: time