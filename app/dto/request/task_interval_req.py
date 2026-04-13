from pydantic import BaseModel, Field
from datetime import time

class TaskIntervalRequest(BaseModel):
    start: time
    end: time