from pydantic import BaseModel
from datetime import time

class DrinkSessionResponse(BaseModel):
    start: time
    end: int