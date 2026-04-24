import uuid
from datetime import datetime, timezone
from typing import List, TYPE_CHECKING, Optional
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import String, DateTime
from .user_role_link import UserRoleLink

if TYPE_CHECKING:
    from .user import User

class Role(SQLModel, table=True):
    __tablename__ = "roles"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(sa_column=Column(String(255), nullable=False))
    
    created_at: Optional[datetime] = Field(sa_type=DateTime(timezone=True), default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(sa_type=DateTime(timezone=True), default_factory=lambda: datetime.now(timezone.utc))
    
    users: List["User"] = Relationship(back_populates="roles", link_model=UserRoleLink)