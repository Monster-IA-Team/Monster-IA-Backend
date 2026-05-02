import uuid
from typing import List

from fastapi import Depends

from models.user import User
from helpers.result import Result
from helpers.pageable import Pageable

from repositories.user_repository import UserRepository
from repositories.role_repository import RoleRepository

from dto.request.create_admin_req import CreateAdminRequest
from dto.response.user_res import UserRes

from configuration.security import get_password_hash

class AdminService:
    def __init__(
        self,
        user_repository: UserRepository = Depends(),
        role_repository: RoleRepository = Depends()
    ):
        self.user_repository = user_repository
        self.role_repository = role_repository
    
    def get_users(self, page: int, size: int) -> Result[Pageable[UserRes]]:
        skip = (page - 1) * size
        
        users = self.user_repository.get_all(skip, size)
        total = self.user_repository.count_all()
        
        user_res_list = [
            UserRes(
                id=user.id,
                username=user.username,
                email=user.email,
                is_active=user.is_active if user.is_active is not None else True,
                roles=[role.name for role in user.roles],
                created_at=user.created_at.isoformat() if user.created_at else "",
                updated_at=user.updated_at.isoformat() if user.updated_at else ""
            )
            for user in users
        ]
        
        pageable = Pageable.create(
            items=user_res_list,
            total_elements=total,
            page=page,
            size=size
        )
        
        return Result.success(
            message="Users retrieved successfully",
            status_code=200,
            data=pageable
        )
    
    def block_user(self, user_id: uuid.UUID) -> Result[None]:
        user = self.user_repository.get_by_id(user_id)
        
        if not user:
            return Result.failure("User not found", 404)
        
        user.is_active = False
        self.user_repository.save(user)
        
        return Result.success(
            message="User blocked successfully",
            status_code=200
        )
    
    def unblock_user(self, user_id: uuid.UUID) -> Result[None]:
        user = self.user_repository.get_by_id(user_id)
        
        if not user:
            return Result.failure("User not found", 404)
        
        user.is_active = True
        self.user_repository.save(user)
        
        return Result.success(
            message="User unblocked successfully",
            status_code=200
        )
    
    def create_admin(self, req: CreateAdminRequest) -> Result[None]:
        existing_user = self.user_repository.get_by_email(req.email)
        if existing_user:
            return Result.failure("Email already in use", 400)
        
        existing_user = self.user_repository.get_by_username(req.username)
        if existing_user:
            return Result.failure("Username already in use", 400)
        
        role = self.role_repository.get_by_name("admin")
        
        if not role:
            return Result.failure("Admin role not found", 500)
        
        user = User(
            email=req.email,
            normalized_email=req.email.upper(),
            username=req.username,
            normalized_username=req.username.upper(),
            password=get_password_hash(req.password),
            is_active=True,
            roles=[role]
        )
        
        self.user_repository.save(user)
        
        return Result.success(
            message="Admin account created successfully",
            status_code=201
        )
    
    def get_admins(self) -> Result[List[UserRes]]:
        admin_role = self.role_repository.get_by_name("admin")
        
        if not admin_role:
            return Result.failure("Admin role not found", 500)
        
        admin_users = self.user_repository.get_users_by_role(admin_role.id)
        
        admin_res_list = [
            UserRes(
                id=user.id,
                username=user.username,
                email=user.email,
                is_active=user.is_active if user.is_active is not None else True,
                roles=[role.name for role in user.roles],
                created_at=user.created_at.isoformat() if user.created_at else "",
                updated_at=user.updated_at.isoformat() if user.updated_at else ""
            )
            for user in admin_users
        ]
        
        return Result.success(
            message="Admins retrieved successfully",
            status_code=200,
            data=admin_res_list
        )
    
    def delete_admin(self, admin_id: uuid.UUID, current_admin_id: uuid.UUID) -> Result[None]:
        if admin_id == current_admin_id:
            return Result.failure("Cannot delete your own admin account", 403)
        
        admin_role = self.role_repository.get_by_name("admin")
        
        if not admin_role:
            return Result.failure("Admin role not found", 500)
        
        admin_users = self.user_repository.get_users_by_role(admin_role.id)
        
        if len(admin_users) <= 1:
            return Result.failure("Cannot delete the last admin account", 403)
        
        user = self.user_repository.get_by_id(admin_id)
        
        if not user:
            return Result.failure("User not found", 404)
        
        self.user_repository.remove_role_from_user(user.id, admin_role.id)
        
        return Result.success(
            message="Admin role removed successfully",
            status_code=200
        )
