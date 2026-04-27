from pydantic import BaseModel
from typing import Optional
from models.taste_profile_enum import TasteProfileEnum

class AddMonserRequest(BaseModel):
    name: str
    description: str
    caffeine_mg: int
    is_sugar_free: Optional[bool]
    taste_profile: TasteProfileEnum
    is_available_online: Optional[bool]
    is_available_zabka: Optional[bool]
    is_available_store: Optional[bool]
    is_premium_line: Optional[bool]