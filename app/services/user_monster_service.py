import uuid
from typing import Literal
from fastapi import Depends

from dto.request.user_monster_list_req import UserMonsterEntryReq
from dto.response.user_monster_list_res import UserMonsterListRes
from models.user_monster_entry import UserMonsterEntry
from repositories.user_monster_repository import UserMonsterRepository
from repositories.monsters_repository import MonsterRepository
from helpers.result import Result
from helpers.pageable import Pageable

class UserMonsterService:
    def __init__(
        self, 
        user_monster_repo: UserMonsterRepository = Depends(),
        monster_repo: MonsterRepository = Depends()
    ):
        self.user_monster_repo = user_monster_repo
        self.monster_repo = monster_repo

    async def get_user_list(
        self,
        user_id: uuid.UUID,
        page: int,
        size: int,
        sort_by: str,
        sort_order: Literal["asc", "desc"]
    ) -> Result[Pageable[UserMonsterListRes]]:
        all_results = self.user_monster_repo.get_all_with_stats(user_id=user_id)
        
        is_reverse = (sort_order == "desc")
        
        try:
            all_results.sort(
                key=lambda x: getattr(x[0], sort_by, getattr(x[0], "name")), 
                reverse=is_reverse
            )
        except AttributeError:
            all_results.sort(key=lambda x: x[0].name, reverse=is_reverse)

        total_elements = len(all_results)
        skip = (page - 1) * size
        paged_results = all_results[skip : skip + size]

        monster_list = [
            UserMonsterListRes(
                id=m.id,
                name=m.name,
                description=m.description,
                image_url=m.image_url,
                average_rating=round(avg, 2) if avg else 0.0,
                is_drunk_by_user=is_drunk
            ) for m, avg, is_drunk in paged_results
        ]

        return Result.success(
            data=Pageable.create(monster_list, total_elements, page, size),
            message="User monster list retrieved successfully (sorted in service)",
            status_code=200
        )

    async def update_interaction(self, user_id: uuid.UUID, req: UserMonsterEntryReq) -> Result[None]:
        if not self.monster_repo.get_by_id(req.monster_id):
            return Result.failure("Monster not found", 404)

        entry = self.user_monster_repo.get_user_entry(user_id, req.monster_id)
        
        if not entry:
            entry = UserMonsterEntry(user_id=user_id, monster_id=req.monster_id)

        entry.rating = req.rating
        entry.is_drunk = req.is_drunk
        
        self.user_monster_repo.save_entry(entry)
        return Result.success(message="Interaction updated successfully", status_code=200)