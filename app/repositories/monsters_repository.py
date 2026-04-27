from typing import Optional
from sqlmodel import Session, select, func
from fastapi import Depends

from models.monster_type import MonsterType
from configuration.database import get_session

class MonsterRepository:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 10,
        sort_by: str = "id",
        sort_order: str = "asc"
        ) -> list[MonsterType]:
        stmt = select(MonsterType)
        
        sort_column = getattr(MonsterType, sort_by, None)
        
        if sort_column is not None:
            if sort_order == "desc":
                stmt = stmt.order_by(sort_column.desc())
            else:
                stmt = stmt.order_by(sort_column.asc())
        
        stmt = stmt.offset(skip).limit(limit)
        
        return self.session.exec(stmt).all()
    
    def count_all(self) -> int:
        return self.session.exec(select(func.count(MonsterType.id))).one()