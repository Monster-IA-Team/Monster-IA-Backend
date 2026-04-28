import uuid
from typing import List, Optional
from sqlmodel import Session, select, func
from fastapi import Depends

from models.user import User
from models.user_role_link import UserRoleLink
from configuration.database import get_session

class UserRepository:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session
    
    def get_by_id(self, id: uuid.UUID) -> Optional[User]:
        return self.session.exec(select(User).where(User.id == id)).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        return self.session.exec(
            select(User).where(User.email.ilike(email.strip()))
        ).first()
        
    def get_by_username(self, username: str) -> Optional[User]:
        return self.session.exec(
            select(User).where(User.username.ilike(username.strip()))
        ).first()
    
    def get_all(self, skip: int, limit: int) -> List[User]:
        return self.session.exec(
            select(User).offset(skip).limit(limit)
        ).all()
    
    def count_all(self) -> int:
        result = self.session.exec(select(func.count(User.id)))
        return result.one()
    
    def get_users_by_role(self, role_id: uuid.UUID) -> List[User]:
        return self.session.exec(
            select(User).join(UserRoleLink, UserRoleLink.user_id == User.id).where(UserRoleLink.role_id == role_id)
        ).all()
    
    def remove_role_from_user(self, user_id: uuid.UUID, role_id: uuid.UUID):
        self.session.execute(
            UserRoleLink.__table__.delete().where(
                UserRoleLink.user_id == user_id,
                UserRoleLink.role_id == role_id
            )
        )
        self.session.commit()
    
    def save(self, user: User):
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user) 