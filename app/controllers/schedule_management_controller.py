from fastapi import APIRouter, Depends, Query, Path, status
from typing import Literal
import uuid
from dependencies.auth import auth_handler
from services.schedule_management_service import ScheduleManagementService
from services.schedule_services import ScheduleService
from dto.request.schedule_req import ScheduleRequest
from dto.response.planner_table_res import PlannerTableRes
from helpers.pageable import Pageable
from helpers.result import Result

router = APIRouter(
    prefix="/api/schedule-management",
    tags=["Schedule Management"],
    dependencies=[Depends(auth_handler.get_current_user)]
)

@router.post(
    "/calculate-and-save",
    summary="Calculate and save schedule",
    response_description="Returns the saved planner details after successful calculation.",
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Invalid input data for schedule calculation."},
        500: {"description": "Internal server error during calculation or database save."}
    }
)
async def calculate_and_save(
    req: ScheduleRequest,
    user=Depends(auth_handler.get_current_user),
    calc_service: ScheduleService = Depends(),
    mgmt_service: ScheduleManagementService = Depends()
):
    """
    ### Performs schedule calculation and persists it.
    
    This endpoint triggers the `ScheduleService` to process the input request.
    Once calculated, the result is automatically saved via `ScheduleManagementService` 
    under the context of the logged-in user.
    """
    calculation_result = calc_service.calculate_schedule(req)
    return await mgmt_service.save_calculated_planner(user.id, req, calculation_result)

@router.get(
    "/history", 
    response_model=Result[Pageable[PlannerTableRes]],
    summary="Get calculation history",
    response_description="Returns a paginated list of previously calculated schedules.",
    status_code=status.HTTP_200_OK
)
async def get_history(
    page: int = Query(1, ge=1, description="Page number (starting from 1)"),
    size: int = Query(10, ge=10, le=50, description="Number of items per page (range 10-50)"),
    sort_order: Literal["asc", "desc"] = Query("desc", description="Sort direction for the history entries"),
    user=Depends(auth_handler.get_current_user),
    mgmt_service: ScheduleManagementService = Depends()
):
    """
    ### Retrieves historical planners for the current user.
    
    The endpoint supports **pagination** and **sorting** by creation date.
    It returns a specialized `Result` object containing `Pageable` data of `PlannerTableRes`.
    """
    return await mgmt_service.get_paginated_history(user.id, page, size, sort_order)

@router.delete(
    "/{planner_id}",
    summary="Delete a specific planner",
    response_description="Success message upon deletion.",
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "Planner not found."},
        403: {"description": "Unauthorized to delete this planner."}
    }
)
async def delete_planner(
    planner_id: uuid.UUID = Path(..., description="Unique identifier (UUID) of the planner to remove"),
    user=Depends(auth_handler.get_current_user),
    mgmt_service: ScheduleManagementService = Depends()
):
    """
    ### Removes a planner from the database.
    
    Verifies if the `planner_id` belongs to the authenticated `user.id` before deletion.
    If the record does not exist or access is denied, appropriate error codes are returned.
    """
    return await mgmt_service.delete_planner(planner_id, user.id)