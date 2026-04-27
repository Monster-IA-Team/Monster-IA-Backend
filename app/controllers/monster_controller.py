from typing import Literal
import uuid
from fastapi import APIRouter, Depends, Query, Path, status
from helpers.result import Result

from services.monster_services import MonsterService
from dto.response.monster_list_res import MonsterListRes
from helpers.pageable import Pageable

router = APIRouter(
    prefix="/api/monsters",
    tags=["Monsters"]
)

@router.get(
    "/list",
    summary="Get Monster list",
    response_description="Returns a paginated list of Monster Energy flavors along with metadata.",
    status_code=status.HTTP_200_OK
)
async def get_list(
    page: int = Query(1, ge=1, description="Page number (starting from 1)"),
    size: int = Query(10, ge=1, le=100, description="Number of items per page (max 100)"),
    sort_by: str = Query("id", description="Column name to sort the results by"),
    sort_order: Literal["asc", "desc"] = Query("asc", description="Sort direction: ascending ('asc') or descending ('desc')"),
    monster_service: MonsterService = Depends()
) -> Result[Pageable[MonsterListRes]]: 
    """
    ### Returns available Monster flavors from the database.
    The endpoint fully supports **pagination** and **dynamic sorting**.
    It ignores deleted entries (soft-delete mechanism).
    
    The response includes a pagination object with fields such as:
    - `total_elements` - total number of active records
    - `total_pages` - total number of pages calculated based on the `size` parameter
    """
    return await monster_service.get_list(
        page=page, 
        size=size, 
        sort_by=sort_by, 
        sort_order=sort_order
    )


@router.delete(
    "/{id}",
    summary="Delete a Monster",
    response_description="Success message upon deletion.",
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "Monster with the given ID not found or already deleted."},
        500: {"description": "Internal server error (e.g., S3/MinIO connection issue)."}
    }
)
async def delete_monster(
    id: uuid.UUID = Path(..., description="Unique identifier (UUID) of the Monster to delete"),
    monster_service: MonsterService = Depends()
):
    """
    ### Performs a Soft Delete of a Monster.
    
    For analytical purposes and to maintain structural integrity, the record is **not physically removed** from the database. Instead:
    - The date is recorded in the `deleted_at` field.
    - A `DELETED_` prefix is appended to the name.
    - Sensitive or unnecessary fields are cleared.
    - The associated **image in the S3/MinIO cloud is physically deleted**.
    """
    return await monster_service.delete(id)