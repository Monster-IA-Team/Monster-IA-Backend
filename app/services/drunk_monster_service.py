import uuid
from typing import Literal
from fastapi import Depends

from dto.request.drunk_monster_list_req import DrunkMonsterEntryReq 
from dto.response.drunk_monster_list_res import DrunkMonsterListRes
from models.user_monster_entry import UserMonsterEntry
from repositories.drunk_monster_repository import DrunkMonsterRepository
from repositories.monsters_repository import MonsterRepository
from helpers.result import Result
from helpers.pageable import Pageable

class DrunkMonsterService:
    def __init__(
        self, 
        drunk_monster_repo: DrunkMonsterRepository = Depends(),
        monster_repo: MonsterRepository = Depends()
    ):
        self.drunk_monster_repo = drunk_monster_repo
        self.monster_repo = monster_repo

    async def get_drunk_list(
        self,
        user_id: uuid.UUID,
        page: int,
        size: int,
        sort_by: str,
        sort_order: Literal["asc", "desc"]
    ) -> Result[Pageable[DrunkMonsterListRes]]:
        all_results = self.drunk_monster_repo.get_all_owned_stats(user_id=user_id)

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
            DrunkMonsterListRes(
                id=m.id,
                name=m.name,
                description=m.description,
                image_url=m.image_url,
                user_rating=rating,
                is_can_owned=is_owned,
                comment=comment
            ) for m, rating, is_owned, comment in paged_results
        ]

        return Result.success(
            data=Pageable.create(monster_list, total_elements, page, size),
            message="Drunk monster list retrieved and sorted in service",
            status_code=200
        )

    async def update_drunk_interaction(self, user_id: uuid.UUID, req: DrunkMonsterEntryReq) -> Result[None]:
        if not self.monster_repo.get_by_id(req.monster_id):
            return Result.failure("Monster not found", 404)

        entry = self.drunk_monster_repo.get_user_entry(user_id, req.monster_id)
        
        if not entry:
            entry = UserMonsterEntry(user_id=user_id, monster_id=req.monster_id)

        entry.rating = req.rating
        entry.is_can_owned = req.is_can_owned
        entry.comment = req.comment
        
        self.drunk_monster_repo.save_entry(entry)
        
        return Result.success(
            message="Ownership and private notes updated successfully",
            status_code=200
        )