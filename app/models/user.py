import uuid
from datetime import datetime, timezone
from typing import List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import String
from .user_role_link import UserRoleLink

if TYPE_CHECKING:
    from .role import Role
    from .user_monster_entry import UserMonsterEntry
    from .planner import Planner

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(sa_column=Column(String(100), unique=True, nullable=False))
    email: str = Field(sa_column=Column(String(255), unique=True, nullable=False))
    password: str = Field(nullable=False)
    is_active: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    roles: List["Role"] = Relationship(back_populates="users", link_model=UserRoleLink)
    monster_entries: List["UserMonsterEntry"] = Relationship(back_populates="user")
    planners: List["Planner"] = Relationship(back_populates="user")