import uuid
from typing import Optional
from sqlmodel import SQLModel
from app.models.enums import TasteProfileEnum

class MonsterTypeRes(SQLModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    caffeine_mg: int
    taste_profile: Optional[TasteProfileEnum]
    image_url: Optional[str]

class UserMonsterEntryRes(SQLModel):
    id: uuid.UUID
    monster_id: uuid.UUID
    rating: Optional[int]
    comment: Optional[str]