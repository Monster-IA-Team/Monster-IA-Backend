import uuid
from datetime import datetime, timezone, time
from typing import List, Optional, TYPE_CHECKING, Any
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import Time, SmallInteger, DateTime
from sqlalchemy.dialects.postgresql import JSONB

if TYPE_CHECKING:
    from .user import User
    from .task import Task

class Planner(SQLModel, table=True):
    __tablename__ = "planners"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    
    wake_time: time = Field(sa_type=Time, nullable=False)
    sleep_time: time = Field(sa_type=Time, nullable=False)
    desired_count: Optional[int] = Field(sa_type=SmallInteger)
    planner: Any = Field(sa_column=Column(JSONB, nullable=False))
    
    created_at: Optional[datetime] = Field(sa_type=DateTime(timezone=True), default_factory=lambda: datetime.now(timezone.utc))

    user: "User" = Relationship(back_populates="planners")
    tasks: List["Task"] = Relationship(back_populates="planner")