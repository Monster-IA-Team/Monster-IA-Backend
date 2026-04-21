import uuid
from datetime import time
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from sqlalchemy import Time

if TYPE_CHECKING:
    from .user import User
    from .task import Task

class Planner(SQLModel, table=True):
    __tablename__ = "planners"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: Optional[uuid.UUID] = Field(foreign_key="users.id")
    wake_time: time = Field(sa_column=Column(Time, nullable=False))
    sleep_time: time = Field(sa_column=Column(Time, nullable=False))
    planner_data: dict = Field(default={}, sa_column=Column(JSON))

    user: Optional["User"] = Relationship(back_populates="planners")
    tasks: List["Task"] = Relationship(back_populates="planner")