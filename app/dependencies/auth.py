import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError
from configuration.security import SECRET_KEY, ALGORITHM 
from models.user import User
from repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/swagger-token")

class Auth:    
    def get_current_user(
        self, 
        token: str = Depends(oauth2_scheme), 
        user_repo: UserRepository = Depends() 
    ) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not verify credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            if payload.get("type") != "access":
                raise credentials_exception
            
            user_id_str: str = payload.get("sub")
            if user_id_str is None:
                raise credentials_exception
            
            user_id = uuid.UUID(user_id_str)
        except (InvalidTokenError, ValueError):
            raise credentials_exception
        
        user = user_repo.get_by_id(user_id)
            
        if user is None:
            raise credentials_exception
        
        return user
    
    def get_user_in_role_admin(self, token: str = Depends(oauth2_scheme), user_repo: UserRepository = Depends()) -> User:
        current_user = self.get_current_user(token, user_repo)
        roles = [role.name.lower() for role in current_user.roles]
        if "admin" not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No permissions.")
        return current_user
    
    def get_user_in_role_user(self, token: str = Depends(oauth2_scheme), user_repo: UserRepository = Depends()) -> User:
        current_user = self.get_current_user(token, user_repo)
        roles = [role.name.lower() for role in current_user.roles]
        if "user" not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No permissions.")
        return current_user

auth_handler = Auth()