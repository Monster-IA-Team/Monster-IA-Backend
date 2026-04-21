import uuid
from datetime import datetime, time, timezone
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from sqlalchemy import String, Text, Time
from enum import Enum

class TasteProfileEnum(str, Enum):
    sweet = "sweet"
    sour = "sour"
    moderate = "moderate"

class IsSugarFreeEnum(str, Enum):
    yes = "yes"
    no = "no"
    no_preference = "no_preference"

class UserRoleLink(SQLModel, table=True):
    __tablename__ = "x_user_roles"
    user_id: uuid.UUID = Field(foreign_key="users.id", primary_key=True)
    role_id: uuid.UUID = Field(foreign_key="roles.id", primary_key=True)

class Role(SQLModel, table=True):
    __tablename__ = "roles"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(sa_column=Column(String(255), unique=True, nullable=False))
    
    users: List["User"] = Relationship(back_populates="roles", link_model=UserRoleLink)

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(sa_column=Column(String(100), unique=True, nullable=False))
    email: str = Field(sa_column=Column(String(255), unique=True, nullable=False))
    password: str = Field(nullable=False)
    is_active: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relacje
    roles: List[Role] = Relationship(back_populates="users", link_model=UserRoleLink)
    monster_entries: List["UserMonsterEntry"] = Relationship(back_populates="user")
    planners: List["Planner"] = Relationship(back_populates="user")

class MonsterType(SQLModel, table=True):
    __tablename__ = "monster_type"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(sa_column=Column(String(120), unique=True, nullable=False))
    description: Optional[str] = Field(sa_column=Column(Text))
    caffeine_mg: int = Field(default=160)
    taste_profile: Optional[TasteProfileEnum] = Field(default=None)
    image_url: Optional[str] = Field(max_length=255)

    entries: List["UserMonsterEntry"] = Relationship(back_populates="monster")

class UserMonsterEntry(SQLModel, table=True):
    __tablename__ = "user_monster_entries"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    monster_id: uuid.UUID = Field(foreign_key="monster_type.id")
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    comment: Optional[str] = Field(max_length=500)
    
    user: User = Relationship(back_populates="monster_entries")
    monster: MonsterType = Relationship(back_populates="entries")

class Planner(SQLModel, table=True):
    __tablename__ = "planners"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: Optional[uuid.UUID] = Field(foreign_key="users.id")
    wake_time: time = Field(sa_column=Column(Time, nullable=False))
    sleep_time: time = Field(sa_column=Column(Time, nullable=False))
    planner_data: dict = Field(default={}, sa_column=Column(JSON)) # Dla JSONB

    user: Optional[User] = Relationship(back_populates="planners")
    tasks: List["Task"] = Relationship(back_populates="planner")

class Task(SQLModel, table=True):
    __tablename__ = "tasks"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    planner_id: uuid.UUID = Field(foreign_key="planners.id")
    title: str = Field(max_length=255)
    start_time: time = Field(sa_column=Column(Time, nullable=False))
    
    planner: Planner = Relationship(back_populates="tasks")