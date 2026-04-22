import uuid, jwt

from fastapi import Depends
from models.user import User
from repositories.user_repository import UserRepository
from datetime import timedelta

from helpers.result import Result
from configuration.security import (
    verify_password, create_access_token, create_refresh_token, 
    ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
)

from dto.response.login_res import UserLoginRes

class AuthService:
    def __init__(self, user_repository: UserRepository = Depends()):
        self.user_repository = user_repository

    def login(self, email: str, password: str) -> Result[UserLoginRes]:
        user = self.user_repository.get_by_email(email)
        
        if not user:
            return Result.failure("Invalid email or password", 404)
        
        if not user.is_active:
            return Result.failure("Account is inactive", 403)
        
        if not verify_password(password, user.password):
            return Result.failure("Invalid email or password", 401)
        
        roles_list = [role.name for role in user.roles]
        
        access_token = create_access_token(
            data={"sub": str(user.id), "roles": roles_list},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return Result.success(
            message="Login successful.",
            status_code=200,
            data=UserLoginRes(
                access_token=access_token,
                refresh_token=refresh_token,
                user_id=user.id,
                email=user.email,
                username=user.username,
                roles=roles_list
            )
        )
    
    def refresh(self, refresh_token: str) -> Result[UserLoginRes]:
        try:
            payload = jwt.decode(req.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            
            if payload.get("type") != "refresh":
                return Result.failure("Invalid token type", 400)

            user_id_str = payload.get("sub")
            if not user_id_str:
                return Result.failure("Invalid token payload", 400)
            
        except jwt.InvalidTokenError:
            return Result.failure("Invalid refresh token", 401)

        user = self.user_repository.get_by_id(uuid.UUID(user_id_str))
        
        if not user or not user.is_active:
            return Result.failure("User not found", 404)
        
        roles_list = [role.name for role in user.roles]
        
        new_access = create_access_token(
            data={"sub": str(user.id), "roles": roles_list},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        new_refresh = create_refresh_token(data={"sub": str(user.id)})
        
          
        return Result.success(
            message="Login successful.",
            status_code=200,
            data=UserLoginRes(
                access_token=new_access,
                refresh_token=new_refresh,
                user_id=user.id,
                email=user.email,
                username=user.username,
                roles=roles_list
            )
        )
            