from typing import Optional

from pydantic import BaseModel, Field
from datetime import time

class TaskIntervalRequest(BaseModel):
    title: Optional[str]
    start: time
    end: time