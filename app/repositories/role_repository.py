from typing import Optional
from sqlmodel import Session, select
from fastapi import Depends

from models.role import Role
from configuration.database import get_session

class RoleRepository:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session
    
    def get_by_name(self, name: str) -> Optional[Role]:
        return self.session.exec(
            select(Role).where(Role.name.ilike(name))
        ).first()