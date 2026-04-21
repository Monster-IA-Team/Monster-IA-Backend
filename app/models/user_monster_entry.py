import uuid
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .user import User
    from .monster_type import MonsterType

class UserMonsterEntry(SQLModel, table=True):
    __tablename__ = "user_monster_entries"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    monster_id: uuid.UUID = Field(foreign_key="monster_type.id")
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    comment: Optional[str] = Field(max_length=500)
    
    user: "User" = Relationship(back_populates="monster_entries")
    monster: "MonsterType" = Relationship(back_populates="entries")