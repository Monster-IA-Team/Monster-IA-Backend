import uuid
from typing import Literal

from fastapi import APIRouter, Depends, Query, Path, status

from dto.request.create_admin_req import CreateAdminRequest
from dto.response.user_res import UserRes
from helpers.result import Result
from helpers.pageable import Pageable

from services.admin_services import AdminService

from dependencies.auth import auth_handler
from models.user import User

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"]
)

@router.get(
    "/users",
    summary="Get all users",
    response_description="Returns a paginated list of users.",
    status_code=status.HTTP_200_OK
)
async def get_users(
    page: int = Query(1, ge=1, description="Page number (starting from 1)"),
    size: int = Query(10, ge=1, le=100, description="Number of items per page (max 100)"),
    admin_service: AdminService = Depends(),
    current_admin: User = Depends(auth_handler.get_user_in_role_admin),
) -> Result[Pageable[UserRes]]:
    return admin_service.get_users(page=page, size=size)

@router.put(
    "/users/{id}/block",
    summary="Block a user",
    response_description="Success message upon blocking.",
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "User not found."}
    }
)
async def block_user(
    id: uuid.UUID = Path(..., description="Unique identifier (UUID) of the User to block"),
    admin_service: AdminService = Depends(),
    current_admin: User = Depends(auth_handler.get_user_in_role_admin),
):
    return admin_service.block_user(id)

@router.put(
    "/users/{id}/unblock",
    summary="Unblock a user",
    response_description="Success message upon unblocking.",
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "User not found."}
    }
)
async def unblock_user(
    id: uuid.UUID = Path(..., description="Unique identifier (UUID) of the User to unblock"),
    admin_service: AdminService = Depends(),
    current_admin: User = Depends(auth_handler.get_user_in_role_admin),
):
    return admin_service.unblock_user(id)

@router.post(
    "/admins/create",
    summary="Create a new admin account",
    response_description="Success message upon creation.",
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Invalid input data or email/username already in use."},
        500: {"description": "Internal server error."}
    }
)
async def create_admin(
    req: CreateAdminRequest,
    admin_service: AdminService = Depends(),
    current_admin: User = Depends(auth_handler.get_user_in_role_admin),
):
    return admin_service.create_admin(req)

@router.get(
    "/admins",
    summary="Get all admin accounts",
    response_description="Returns a list of admin accounts.",
    status_code=status.HTTP_200_OK
)
async def get_admins(
    admin_service: AdminService = Depends(),
    current_admin: User = Depends(auth_handler.get_user_in_role_admin),
) -> Result[list[UserRes]]:
    return admin_service.get_admins()

@router.delete(
    "/admins/{id}",
    summary="Delete an admin account",
    response_description="Success message upon deletion.",
    status_code=status.HTTP_200_OK,
    responses={
        403: {"description": "Cannot delete own account or last admin."},
        404: {"description": "User not found."}
    }
)
async def delete_admin(
    id: uuid.UUID = Path(..., description="Unique identifier (UUID) of the Admin to delete"),
    admin_service: AdminService = Depends(),
    current_admin: User = Depends(auth_handler.get_user_in_role_admin),
):
    return admin_service.delete_admin(id, current_admin.id)
