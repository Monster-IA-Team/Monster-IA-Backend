from typing import Literal
from fastapi import APIRouter, Depends, Query
from helpers.result import Result

from services.monster_services import MonsterService
from dto.response.monster_list_res import MonsterListRes
from helpers.pageable import Pageable

router = APIRouter(
    prefix="/api/monsters",
    tags=["Monsters"]
)

@router.get("/list")
async def get_list(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    sort_by: str = Query("id", description="Column to sort by"),
    sort_order: Literal["asc", "desc"] = Query("asc", description="Sort order: 'asc' or 'desc'"),
    monster_service: MonsterService = Depends()
) -> Result[Pageable[MonsterListRes]]: 
    
    return monster_service.get_list(
        page=page, 
        size=size, 
        sort_by=sort_by, 
        sort_order=sort_order
    )