from typing import Optional
from sqlmodel import Session, select, func
from fastapi import Depends
import uuid
from datetime import datetime, timezone

from models.monster_type import MonsterType
from configuration.database import get_session
from helpers.soft_delete import mark_as_deleted

class MonsterRepository:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session
    
    def get_by_id(self, monster_id: uuid.UUID) -> Optional[MonsterType]:
        stmt = select(MonsterType).where(
            MonsterType.id == monster_id, 
            MonsterType.deleted_at.is_(None)
            )
        return self.session.exec(stmt).first()
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 10,
        sort_by: str = "id",
        sort_order: str = "asc"
        ) -> list[MonsterType]:
        stmt = select(MonsterType).where(MonsterType.deleted_at.is_(None))
        
        sort_column = getattr(MonsterType, sort_by, None)
        
        if sort_column is not None:
            if sort_order == "desc":
                stmt = stmt.order_by(sort_column.desc())
            else:
                stmt = stmt.order_by(sort_column.asc())
        
        stmt = stmt.offset(skip).limit(limit)
        
        return self.session.exec(stmt).all()
    
    def count_all(self) -> int:
        stmt = select(func.count(MonsterType.id)).where(MonsterType.deleted_at.is_(None))
        return self.session.exec(stmt).one()
    
    def delete(self, monster: MonsterType):
        monster.deleted_at = datetime.now(timezone.utc)
        monster.name = mark_as_deleted(monster.name)
        monster.description = None
        monster.caffeine_mg = 0
        monster.sugar_free = None
        monster.taste_profile = None
        monster.available_online = None
        monster.available_zabka = None
        monster.available_store = None
        monster.premium_line = None
        monster.image_url = None
        
        self.session.add(monster)
        self.session.commit()
        self.session.refresh(monster)

    def save(self, monster: MonsterType) -> MonsterType:
        self.session.add(monster)
        self.session.commit()
        self.session.refresh(monster)
        return monster
