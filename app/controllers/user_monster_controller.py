import uuid
from typing import Literal
from fastapi import APIRouter, Depends, Query, status

from dto.request.user_monster_list_req import UserMonsterEntryReq
from dto.response.user_monster_list_res import UserMonsterListRes
from services.user_monster_service import UserMonsterService
from dependencies.auth import auth_handler
from models.user import User
from helpers.result import Result
from helpers.pageable import Pageable

router = APIRouter(
    prefix="/api/user-monsters",
    tags=["User Interactions"]
)

@router.get(
    "/list",
    summary="Get monsters with my status",
    status_code=status.HTTP_200_OK
)
async def get_monsters_for_user(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    sort_by: str = Query("name"),
    sort_order: Literal["asc", "desc"] = Query("asc"),
    user_service: UserMonsterService = Depends(),
    current_user: User = Depends(auth_handler.get_current_user),
) -> Result[Pageable[UserMonsterListRes]]:
    return await user_service.get_user_list(
        user_id=current_user.id,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_order=sort_order
    )

@router.post(
    "/interaction",
    summary="Rate or mark monster as drunk",
    status_code=status.HTTP_200_OK
)
async def update_interaction(
    request: UserMonsterEntryReq,
    user_service: UserMonsterService = Depends(),
    current_user: User = Depends(auth_handler.get_current_user),
):
    return await user_service.update_interaction(current_user.id, request)