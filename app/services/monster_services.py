from fastapi import Depends
from typing import Literal
import uuid

from models.monster_type import MonsterType
from repositories.monsters_repository import MonsterRepository
from dto.response.monster_list_res import MonsterListRes
from helpers.result import Result
from helpers.pageable import Pageable
from services.s3_services import S3Service

class MonsterService:
    def __init__(self, monser_repository: MonsterRepository = Depends(), s3_service: S3Service = Depends()):
        self.monster_repository = monser_repository
        self.s3_service = s3_service

    async def get_list(
        self,
        page: int,
        size: int,
        sort_by: str,
        sort_order: Literal["asc", "desc"]
        ) -> Result[Pageable[MonsterListRes]]:
               skip = (page - 1) * size
               
               monsters = self.monster_repository.get_all(
                   skip=skip,
                   limit=size,
                   sort_by=sort_by,
                   sort_order=sort_order
               )
               
               total_elements = self.monster_repository.count_all()
               
               
               monster_list = [
                     MonsterListRes(
                            id=monster.id, 
                            name=monster.name, 
                            description=monster.description,
                            caffeine_mg=monster.caffeine_mg,
                            sugar_free=monster.sugar_free,
                            taste_profile=monster.taste_profile,
                            available_online=monster.available_online,
                            available_zabka=monster.available_zabka,
                            available_store=monster.available_store,
                            premium_line=monster.premium_line,
                            image_url=monster.image_url,
                            created_at=monster.created_at.isoformat() if monster.created_at else None,
                            updated_at=monster.updated_at.isoformat() if monster.updated_at else None
                     )
                     for monster in monsters
               ]
               
               page_data = Pageable.create(
                   items=monster_list,
                   total_elements=total_elements,
                   page=page,
                   size=size
               )

               return Result.success(
                   data=page_data,
                   message="Monsters retrieved successfully",
                   status_code=200
               )
               
    async def delete(self, id: uuid.UUID) -> Result[None]:
        monster = self.monster_repository.get_by_id(id)
        
        if not monster:
            return Result.failure(
                message="Monster not found",
                status_code=404
            )
        
        image_to_delete = monster.image_url
        
        self.monster_repository.delete(monster)
        
        if image_to_delete:
            await self.s3_service.delete_file(image_to_delete)
        
        return Result.success(
            message="Monster deleted successfully",
            status_code=200
        )