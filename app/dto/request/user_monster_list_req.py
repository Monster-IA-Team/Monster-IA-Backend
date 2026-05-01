import uuid
from typing import Optional
from pydantic import BaseModel, Field

class UserMonsterEntryReq(BaseModel):
    monster_id: uuid.UUID
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating from 1 to 5")
    is_drunk: bool = Field(default=False, description="Does the user have this can")