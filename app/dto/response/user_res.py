from uuid import UUID
from pydantic import BaseModel
from typing import List

class UserRes(BaseModel):
    id: UUID
    username: str
    email: str
    is_active: bool
    roles: List[str]
    created_at: str
    updated_at: str
