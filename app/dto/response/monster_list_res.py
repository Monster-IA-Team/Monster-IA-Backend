from pydantic import BaseModel
from uuid import UUID

class MonsterListRes(BaseModel):
    id: UUID
    name: str
    description: str | None
    caffeine_mg: int
    sugar_free: bool | None
    taste_profile: str | None
    available_online: bool | None
    available_zabka: bool | None
    available_store: bool | None
    premium_line: bool | None
    image_url: str | None
    created_at: str | None
    updated_at: str | None