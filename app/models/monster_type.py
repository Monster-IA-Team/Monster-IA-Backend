import uuid
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import String, Text
from models.taste_profile_enum import TasteProfileEnum
from models.is_sugar_free_enum import IsSugarFreeEnum

if TYPE_CHECKING:
    from .user_monster_entry import UserMonsterEntry

class MonsterType(SQLModel, table=True):
    __tablename__ = "monster_type"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(sa_column=Column(String(120), unique=True, nullable=False))
    description: Optional[str] = Field(sa_column=Column(Text))
    caffeine_mg: int = Field(default=160)
    taste_profile: Optional[TasteProfileEnum] = Field(default=None)
    image_url: Optional[str] = Field(max_length=255)

    entries: List["UserMonsterEntry"] = Relationship(back_populates="monster")