from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class UserMonsterListRes(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    image_url: Optional[str]
    
    average_rating: Optional[float] 
    is_drunk_by_user: bool 