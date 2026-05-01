import uuid
from typing import Optional
from pydantic import BaseModel, Field

class DrunkMonsterEntryReq(BaseModel):
    monster_id: uuid.UUID
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rate from 1 to 5")
    is_can_owned: bool = Field(default=False, description="Does the user have this can")
    comment: Optional[str] = Field(None, max_length=500, description="Private note/User comment")