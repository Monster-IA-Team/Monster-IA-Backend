import uuid
from datetime import datetime, timezone
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import String, DateTime
from .user_role_link import UserRoleLink

if TYPE_CHECKING:
    from .role import Role
    from .taste_preference import TastePreference
    from .user_monster_entry import UserMonsterEntry
    from .planner import Planner

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(sa_type=String(100), nullable=False)
    normalized_username: str = Field(sa_type=String(100), nullable=False)
    email: str = Field(sa_type=String(255), nullable=False)
    normalized_email: str = Field(sa_type=String(255), nullable=False)
    password: str = Field(sa_type=String(255), nullable=False)
    
    is_active: Optional[bool] = Field(default=None)
    prefers_sugar_free: Optional[bool] = Field(default=None)
    
    created_at: Optional[datetime] = Field(sa_type=DateTime(timezone=True), default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(sa_type=DateTime(timezone=True), default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = Field(sa_type=DateTime(timezone=True), default=None)

    roles: List["Role"] = Relationship(back_populates="users", link_model=UserRoleLink)
    taste_preferences: Optional["TastePreference"] = Relationship(back_populates="user")
    monster_entries: List["UserMonsterEntry"] = Relationship(back_populates="user")
    planners: List["Planner"] = Relationship(back_populates="user")