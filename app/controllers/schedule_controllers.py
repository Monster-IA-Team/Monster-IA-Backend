from fastapi import APIRouter, Depends
from dependencies.auth import auth_handler

from services.schedule_services import ScheduleService

from dto.request.schedule_req import ScheduleRequest

from dto.response.schedule_res import ScheduleResponse

router = APIRouter(
    prefix="/api/schedule",
    tags=["Schedule Calculation"],
    dependencies=[Depends(auth_handler.get_current_user)]
)

schedule_service = ScheduleService()

@router.post("", response_model=ScheduleResponse)
async def calculate_schedule(req: ScheduleRequest):
    return schedule_service.calculate_schedule(req)