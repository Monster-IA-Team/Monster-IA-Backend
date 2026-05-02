import uuid
from typing import Literal, List
from fastapi import Depends
from models.planner import Planner
from models.task import Task
from repositories.schedule_management_repository import PlannerRepository
from dto.response.planner_table_res import PlannerTableRes
from dto.request.schedule_req import ScheduleRequest
from dto.response.schedule_res import ScheduleResponse
from helpers.result import Result
from helpers.pageable import Pageable

class ScheduleManagementService:
    def __init__(self, planner_repo: PlannerRepository = Depends()):
        self.planner_repo = planner_repo

    async def save_calculated_planner(
        self, 
        user_id: uuid.UUID, 
        req: ScheduleRequest, 
        res: ScheduleResponse
    ) -> Result[uuid.UUID]:

        new_planner = Planner(
            user_id=user_id,
            wake_time=req.wake,
            sleep_time=req.sleep,
            desired_count=req.monster_count,
            planner=res.model_dump(mode="json")
        )

        tasks = [
            Task(title=t.title if hasattr(t, 'title') else "Task", 
                 start_time=t.start, 
                 end_time=t.end) 
            for t in req.tasks
        ]

        saved = self.planner_repo.save_planner(new_planner, tasks)
        return Result.success(status_code=201, data=saved.id, message="Schedule saved successfully")

    async def get_paginated_history(
        self,
        user_id: uuid.UUID,
        page: int,
        size: int,
        sort_order: Literal["asc", "desc"]
    ) -> Result[Pageable[PlannerTableRes]]:
        
        all_planners = self.planner_repo.get_all_by_user(user_id)
        is_reverse = (sort_order == "desc")
        all_planners.sort(key=lambda x: x.created_at, reverse=is_reverse)

        total = len(all_planners)
        skip = (page - 1) * size
        paged = all_planners[skip : skip + size]

        data = [
            PlannerTableRes(
                id=p.id,
                wake_time=p.wake_time,
                sleep_time=p.sleep_time,
                desired_count=p.desired_count,
                created_at=p.created_at,
                sessions_count=len(p.planner.get("drink_sessions", []))
            ) for p in paged
        ]

        return Result.success(
            status_code=200,
            data=Pageable.create(data, total, page, size),
            message="History retrieved successfully"
        )

    async def delete_planner(self, planner_id: uuid.UUID, user_id: uuid.UUID) -> Result[None]:
        planner = self.planner_repo.get_by_id(planner_id)
        if not planner or planner.user_id != user_id:
            return Result.failure("Planner not found", 404)
        
        self.planner_repo.delete(planner)
        return Result.success(status_code=200,message="Planner deleted successfully")