import uuid
from typing import Optional
from sqlmodel import Session, select
from fastapi import Depends

from models.user import User
from configuration.database import get_session

class UserRepository:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session
    
    def get_by_id(self, id: uuid.UUID) -> Optional[User]:
        return self.session.exec(select(User).where(User.id == id)).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        return self.session.exec(select(User).where(User.email == email)).first()