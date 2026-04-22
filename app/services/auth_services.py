from fastapi import Depends
from models.user import User
from repositories.user_repository import UserRepository
from datetime import timedelta

from helpers.result import Result
from configuration.security import (
    get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
)
from dto.response.login_res import UserLoginRes

class AuthService:
    # 2. ZMIEŃ TĘ LINIJKĘ (dodaj = Depends())
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
        
        return Result.success(
            message="Login successful.",
            status_code=200,
            data=UserLoginRes(
                token=access_token,
                user_id=user.id,
                email=user.email,
                username=user.username,
                roles=roles_list
            )
        )