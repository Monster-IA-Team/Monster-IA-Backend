import uuid
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import String, Text, Integer, DateTime, Enum
from .taste_profile_enum import TasteProfileEnum

if TYPE_CHECKING:
    from .user_monster_entry import UserMonsterEntry

class MonsterType(SQLModel, table=True):
    __tablename__ = "monster_flavors"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(sa_type=String(120), nullable=False)
    description: Optional[str] = Field(sa_column=Column(Text))
    caffeine_mg: int = Field(sa_type=Integer, nullable=False)
    
    sugar_free: Optional[bool] = Field(default=None)
    taste_profile: Optional[TasteProfileEnum] = Field(sa_column=Column(Enum(TasteProfileEnum)))
    available_online: Optional[bool] = Field(default=None)
    available_zabka: Optional[bool] = Field(default=None)
    available_store: Optional[bool] = Field(default=None)
    premium_line: Optional[bool] = Field(default=None)
    
    image_url: Optional[str] = Field(sa_type=String(255))
    
    created_at: Optional[datetime] = Field(sa_type=DateTime(timezone=True), default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(sa_type=DateTime(timezone=True), default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = Field(sa_type=DateTime(timezone=True), default=None)

    entries: List["UserMonsterEntry"] = Relationship(back_populates="monster")