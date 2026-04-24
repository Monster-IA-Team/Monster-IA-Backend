import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import SmallInteger, String, DateTime

if TYPE_CHECKING:
    from .user import User
    from .monster_type import MonsterType

class UserMonsterEntry(SQLModel, table=True):
    __tablename__ = "user_monster_entries"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    monster_id: uuid.UUID = Field(foreign_key="monster_flavors.id")
    
    is_drunk: Optional[bool] = Field(default=None)
    is_can_owned: Optional[bool] = Field(default=None)
    rating: Optional[int] = Field(sa_type=SmallInteger)
    comment: Optional[str] = Field(sa_type=String(500))
    
    drunk_at: Optional[datetime] = Field(sa_type=DateTime(timezone=True), default=None)
    created_at: Optional[datetime] = Field(sa_type=DateTime(timezone=True), default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(sa_type=DateTime(timezone=True), default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = Field(sa_type=DateTime(timezone=True), default=None)

    user: "User" = Relationship(back_populates="monster_entries")
    monster: "MonsterType" = Relationship(back_populates="entries")