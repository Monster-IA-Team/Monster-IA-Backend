from fastapi import APIRouter

from services.schedule_services import ScheduleService

from dto.request.schedule_req import ScheduleRequest
from dto.response.schedule_res import ScheduleResponse

router = APIRouter(
    prefix="/api/schedule",
    tags=["Schedule Calculation"]
)

schedule_service = ScheduleService()

@router.post("", response_model=ScheduleResponse)
async def calculate_schedule(req: ScheduleRequest):
    return schedule_service.calculate_schedule(req)