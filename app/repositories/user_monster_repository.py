from typing import Optional, Tuple
from sqlmodel import Session, select, func, and_
from fastapi import Depends
import uuid

from configuration.database import get_session
from models.monster_type import MonsterType
from models.user_monster_entry import UserMonsterEntry

class UserMonsterRepository:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_all_with_stats(
        self, 
        user_id: uuid.UUID, 
        skip: int, 
        limit: int, 
        sort_by: str, 
        sort_order: str
    ) -> list[Tuple[MonsterType, float, bool]]:
        avg_rating_stmt = (
            select(
                UserMonsterEntry.monster_id,
                func.avg(UserMonsterEntry.rating).label("avg_rating")
            )
            .group_by(UserMonsterEntry.monster_id)
            .subquery()
        )

        stmt = (
            select(
                MonsterType,
                func.coalesce(avg_rating_stmt.c.avg_rating, 0).label("average"),
                func.coalesce(UserMonsterEntry.is_drunk, False).label("is_drunk")
            )
            .outerjoin(avg_rating_stmt, MonsterType.id == avg_rating_stmt.c.monster_id)
            .outerjoin(
                UserMonsterEntry, 
                and_(MonsterType.id == UserMonsterEntry.monster_id, UserMonsterEntry.user_id == user_id)
            )
            .where(MonsterType.deleted_at.is_(None))
        )

        sort_column = getattr(MonsterType, sort_by, MonsterType.name)
        if sort_order == "desc":
            stmt = stmt.order_by(sort_column.desc())
        else:
            stmt = stmt.order_by(sort_column.asc())

        stmt = stmt.offset(skip).limit(limit)
        
        return self.session.exec(stmt).all()

    def get_user_entry(self, user_id: uuid.UUID, monster_id: uuid.UUID) -> Optional[UserMonsterEntry]:
        stmt = select(UserMonsterEntry).where(
            UserMonsterEntry.user_id == user_id,
            UserMonsterEntry.monster_id == monster_id
        )
        return self.session.exec(stmt).first()

    def save_entry(self, entry: UserMonsterEntry):
        self.session.add(entry)
        self.session.commit()
        self.session.refresh(entry)