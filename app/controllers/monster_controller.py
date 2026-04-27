from typing import Literal, Optional
import uuid
from fastapi import APIRouter, Depends, Query, Path, status, Form, File, UploadFile

from dto.request.add_monser_req import AddMonserRequest
from helpers.result import Result
from models.taste_profile_enum import TasteProfileEnum

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


@router.post(
    "/add",
    summary="Add a new Monster",
    response_description="Success message upon creation.",
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Invalid input data or missing image."},
        500: {"description": "Internal server error during S3 upload or database save."}
    }
)
async def create_monster(
        name: str = Form(..., description="Name of the new Monster flavor"),
        description: str = Form(..., description="Detailed description of the flavor"),
        caffeine_mg: int = Form(..., description="Amount of caffeine in mg"),
        taste_profile: TasteProfileEnum = Form(..., description="General taste profile category"),
        is_sugar_free: Optional[bool] = Form(None, description="Is it a zero-sugar variant?"),
        is_available_online: Optional[bool] = Form(None),
        is_available_zabka: Optional[bool] = Form(None),
        is_available_store: Optional[bool] = Form(None),
        is_premium_line: Optional[bool] = Form(None),
        image: UploadFile = File(..., description="Image file (JPG/PNG) of the Monster can"),
        monster_service: MonsterService = Depends()
):
    """
    ### Creates a new Monster Energy flavor in the database.

    This endpoint accepts `multipart/form-data` to handle both text fields and the image file upload simultaneously.
    - The image will be uploaded to the S3/MinIO bucket.
    - The record will be saved in the database with the generated image URL.
    """
    request_dto = AddMonserRequest(
        name=name,
        description=description,
        caffeine_mg=caffeine_mg,
        is_sugar_free=is_sugar_free,
        taste_profile=taste_profile,
        is_available_online=is_available_online,
        is_available_zabka=is_available_zabka,
        is_available_store=is_available_store,
        is_premium_line=is_premium_line
    )
    return await monster_service.create(request_dto, image)