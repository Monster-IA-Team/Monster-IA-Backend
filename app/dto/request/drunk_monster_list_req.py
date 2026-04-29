import uuid
from typing import Optional
from pydantic import BaseModel, Field

class DrunkMonsterEntryReq(BaseModel):
    monster_id: uuid.UUID
    rating: Optional[int] = Field(None, ge=1, le=5, description="Ocena od 1 do 5")
    is_can_owned: bool = Field(default=False, description="Czy użytkownik posiada tę puszkę")
    comment: Optional[str] = Field(None, max_length=500, description="Prywatna notatka/komentarz użytkownika")