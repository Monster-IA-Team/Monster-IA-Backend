from uuid import UUID
from pydantic import BaseModel

class UserLoginRes(BaseModel):
    access_token: str
    refresh_token: str
    user_id: UUID
    email: str
    username: str
    roles : list[str]