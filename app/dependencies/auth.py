import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
import jwt
from jwt.exceptions import InvalidTokenError

from configuration.security import SecurityConfig
from models.user import User
from configuration.database import get_session
from repositories.user_repository import UserRepository

aouth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

class Auth:
    def __init__(
            self, 
            security_config: SecurityConfig = Depends(), 
            db: Session = Depends(get_session),
            user_repo: UserRepository = Depends()
            ):
        self.security_config = security_config
        self.db = db
        self.user_repo = user_repo
    
    def get_current_user(self, token: str = Depends(aouth2_scheme), session: Session = Depends(get_session)) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not verify credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(token, self.security_config.SECERT_KEY, algorithms=[self.security_config.ALGORITHM])
            
            if payload.get("type") != "access":
                raise credentials_exception
            
            user_id_str: str = payload.get("sub")
            
            if user_id_str is None:
                raise credentials_exception
            
            user_id = uuid.UUID(user_id_str)
        except (InvalidTokenError, ValueError):
            raise credentials_exception
        
        user = self.user_repo.get_by_id(user_id)
            
        if user is None:
            raise credentials_exception
        
        return user