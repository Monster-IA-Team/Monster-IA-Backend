from typing import Optional, Tuple
from sqlmodel import Session, select, func, and_
from fastapi import Depends
import uuid

from configuration.database import get_session
from models.monster_type import MonsterType
from models.user_monster_entry import UserMonsterEntry

class DrunkMonsterRepository:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_all_owned_stats(
        self, 
        user_id: uuid.UUID
    ) -> list[Tuple[MonsterType, Optional[int], bool, Optional[str]]]:
        stmt = (
            select(
                MonsterType,
                UserMonsterEntry.rating.label("user_rating"),
                func.coalesce(UserMonsterEntry.is_can_owned, False).label("is_can_owned"),
                UserMonsterEntry.comment
            )
            .outerjoin(
                UserMonsterEntry, 
                and_(MonsterType.id == UserMonsterEntry.monster_id, UserMonsterEntry.user_id == user_id)
            )
            .where(MonsterType.deleted_at.is_(None))
        )
        
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