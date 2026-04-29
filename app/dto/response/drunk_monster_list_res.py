from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class DrunkMonsterListRes(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    image_url: Optional[str]
    
    user_rating: Optional[int]
    is_can_owned: bool
    comment: Optional[str]