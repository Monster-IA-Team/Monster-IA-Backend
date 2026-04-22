import uuid, jwt

from fastapi import Depends, BackgroundTasks
from models.user import User
from datetime import timedelta
from helpers.result import Result

from repositories.user_repository import UserRepository
from repositories.role_repository import RoleRepository

from dto.response.login_res import UserLoginRes

from dto.request.refresh_req import RefreshTokenReq
from dto.request.register_req import RegisterRequset

from configuration.email_sender import EmailSender

from configuration.security import (
    verify_password, create_access_token, create_refresh_token, 
    ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM, get_password_hash, create_activation_token
)


class AuthService:
    def __init__(self, user_repository: UserRepository = Depends(), role_repository: RoleRepository = Depends()):
        self.user_repository = user_repository
        self.role_repository = role_repository

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
    
    def refresh(self, req: RefreshTokenReq) -> Result[UserLoginRes]:
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
    
    def register(self, req: RegisterRequset, background_tasks: BackgroundTasks) -> Result[None]:
        existing_user = self.user_repository.get_by_email(req.email)
        if existing_user:
            return Result.failure("Email already in use", 400)
        
        existing_user = self.user_repository.get_by_username(req.username)
        if existing_user:
            return Result.failure("Username already in use", 400)
        
        role = self.role_repository.get_by_name("user")
        
        user = User(
            email=req.email,
            username=req.username,
            password=get_password_hash(req.password),
            is_active=False,
            roles=[role] if role else []
        )
        
        self.user_repository.save(user)
        
        activation_token = create_activation_token(user.email, str(user.id))
        
        background_tasks.add_task(EmailSender.send_email, to_email=user.email, token=activation_token)
        
        return Result.success(
            message="Registration successful. Please check your email to activate your account.",
            status_code=201
        )
    
    def activate_account(self, token: str) -> Result[None]:
        try: 
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            if payload.get("type") != "activation":
                return Result.failure("Invalid token type", 400)

            email = payload.get("sub1")
            user_id_str = payload.get("sub2")
            
            if not email or not user_id_str:
                return Result.failure("Invalid token payload", 400)
            
            user = self.user_repository.get_by_id(uuid.UUID(user_id_str))
            if not user or user.email != email:
                return Result.failure("User not found", 404)
            
        except jwt.ExpiredSignatureError:
            return Result.failure("Activation token has expired", 400)

        if user.is_active:
            return Result.failure("Account is already active", 400)
        
        user.is_active = True
        self.user_repository.save(user)
        
        return Result.success(
            message="Account activated successfully. You can now log in.",
            status_code=200
        )