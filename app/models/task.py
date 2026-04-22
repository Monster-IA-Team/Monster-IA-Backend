import uuid
from datetime import time
from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import Time

if TYPE_CHECKING:
    from .planner import Planner

class Task(SQLModel, table=True):
    __tablename__ = "tasks"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    planner_id: uuid.UUID = Field(foreign_key="planners.id")
    title: str = Field(max_length=255)
    start_time: time = Field(sa_column=Column(Time, nullable=False))
    
    planner: "Planner" = Relationship(back_populates="tasks")