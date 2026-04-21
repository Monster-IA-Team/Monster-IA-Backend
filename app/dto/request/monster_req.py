import uuid
from typing import Optional
from sqlmodel import SQLModel, Field
from app.models.enums import TasteProfileEnum

class MonsterTypeCreateReq(SQLModel):
    name: str = Field(max_length=120)
    description: Optional[str] = None
    caffeine_mg: int = Field(default=160)
    taste_profile: Optional[TasteProfileEnum] = None
    image_url: Optional[str] = None

class MonsterEntryCreateReq(SQLModel):
    monster_id: uuid.UUID
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = Field(default=None, max_length=500)