import uuid
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import Enum
from .is_sugar_free_enum import IsSugarFreeEnum

if TYPE_CHECKING:
    from .user import User

class TastePreference(SQLModel, table=True):
    __tablename__ = "taste_preferences"
    
    user_id: uuid.UUID = Field(foreign_key="users.id", primary_key=True)
    
    is_sweet: Optional[bool] = Field(default=None)
    is_sour: Optional[bool] = Field(default=None)
    is_moderate: Optional[bool] = Field(default=None)
    is_sugar_free: Optional[IsSugarFreeEnum] = Field(sa_column=Column(Enum(IsSugarFreeEnum)))

    user: "User" = Relationship(back_populates="taste_preferences")