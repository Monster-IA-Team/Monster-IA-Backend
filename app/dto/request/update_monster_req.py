import uuid
from pydantic import BaseModel
from typing import Optional
from models.taste_profile_enum import TasteProfileEnum

class UpdateMonsterReq(BaseModel):
    id: uuid.UUID
    name: Optional[str] = None
    description: Optional[str] = None
    caffeine_mg: Optional[int] = None # Poprawione na int
    is_sugar_free: Optional[bool] = None
    taste_profile: Optional[TasteProfileEnum] = None
    is_available_online: Optional[bool] = None
    is_available_zabka: Optional[bool] = None
    is_available_store: Optional[bool] = None
    is_premium_line: Optional[bool] = None