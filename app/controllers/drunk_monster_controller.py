import uuid
from typing import Literal
from fastapi import APIRouter, Depends, Query, status

from dto.request.drunk_monster_list_req import DrunkMonsterEntryReq
from dto.response.drunk_monster_list_res import DrunkMonsterListRes
from services.drunk_monster_service import DrunkMonsterService
from dependencies.auth import auth_handler
from models.user import User
from helpers.result import Result
from helpers.pageable import Pageable

router = APIRouter(
    prefix="/api/drunk-monsters",
    tags=["Drunk Monsters / Ownership"]
)

@router.get(
    "/list",
    summary="Get monsters with user ownership status and private notes",
    status_code=status.HTTP_200_OK
)
async def get_drunk_monsters_for_user(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    sort_by: str = Query("name"),
    sort_order: Literal["asc", "desc"] = Query("asc"),
    drunk_service: DrunkMonsterService = Depends(),
    current_user: User = Depends(auth_handler.get_current_user),
) -> Result[Pageable[DrunkMonsterListRes]]:
    return await drunk_service.get_drunk_list(
        user_id=current_user.id,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_order=sort_order
    )

@router.post(
    "/interaction",
    summary="Update ownership status, rating, and private notes",
    status_code=status.HTTP_200_OK
)
async def update_drunk_interaction(
    request: DrunkMonsterEntryReq,
    drunk_service: DrunkMonsterService = Depends(),
    current_user: User = Depends(auth_handler.get_current_user),
):
    return await drunk_service.update_drunk_interaction(current_user.id, request)