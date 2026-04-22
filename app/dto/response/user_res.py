import uuid
from datetime import datetime
from sqlmodel import SQLModel

class UserPublicRes(SQLModel):
    id: uuid.UUID
    username: str
    email: str
    is_active: bool
    created_at: datetime
    # Brak pola password!