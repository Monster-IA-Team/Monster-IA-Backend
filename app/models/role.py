import uuid
from typing import List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import String
from .user_role_link import UserRoleLink

if TYPE_CHECKING:
    from .user import User

class Role(SQLModel, table=True):
    __tablename__ = "roles"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(sa_column=Column(String(255), unique=True, nullable=False))
    
    users: List["User"] = Relationship(back_populates="roles", link_model=UserRoleLink)