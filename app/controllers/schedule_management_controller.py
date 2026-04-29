from fastapi import APIRouter, Depends, Query
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

@router.post("/calculate-and-save")
async def calculate_and_save(
    req: ScheduleRequest,
    user=Depends(auth_handler.get_current_user),
    calc_service: ScheduleService = Depends(),
    mgmt_service: ScheduleManagementService = Depends()
):
    calculation_result = calc_service.calculate_schedule(req)
    return await mgmt_service.save_calculated_planner(user.id, req, calculation_result)

@router.get("/history", response_model=Result[Pageable[PlannerTableRes]])
async def get_history(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=10, le=50),
    sort_order: Literal["asc", "desc"] = "desc",
    user=Depends(auth_handler.get_current_user),
    mgmt_service: ScheduleManagementService = Depends()
):
    return await mgmt_service.get_paginated_history(user.id, page, size, sort_order)

@router.delete("/{planner_id}")
async def delete_planner(
    planner_id: uuid.UUID,
    user=Depends(auth_handler.get_current_user),
    mgmt_service: ScheduleManagementService = Depends()
):
    return await mgmt_service.delete_planner(planner_id, user.id)