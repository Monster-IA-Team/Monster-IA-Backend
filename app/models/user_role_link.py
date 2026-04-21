import uuid
from sqlmodel import SQLModel, Field

class UserRoleLink(SQLModel, table=True):
    __tablename__ = "x_user_roles"
    user_id: uuid.UUID = Field(foreign_key="users.id", primary_key=True)
    role_id: uuid.UUID = Field(foreign_key="roles.id", primary_key=True)