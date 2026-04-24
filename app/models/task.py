import uuid
from datetime import time
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import String, Time

if TYPE_CHECKING:
    from .planner import Planner

class Task(SQLModel, table=True):
    __tablename__ = "tasks"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    planners_id: uuid.UUID = Field(foreign_key="planners.id")
    
    title: Optional[str] = Field(sa_type=String(255))
    start_time: time = Field(sa_type=Time, nullable=False)
    end_time: time = Field(sa_type=Time, nullable=False)

    planner: "Planner" = Relationship(back_populates="tasks")