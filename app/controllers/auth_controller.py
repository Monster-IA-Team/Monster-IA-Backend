from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from services.auth_services import AuthService
from dto.response.login_res import UserLoginRes
from helpers.result import Result
from dto.request.refresh_req import RefreshTokenReq

router = APIRouter(
    prefix="/api/auth",
    tags=["Auth"]
)

@router.post(
    "/login", 
    response_model=Result[UserLoginRes],
    summary="Log in the user and get the token",
    description="The endpoint used by Swagger for authorization." + 
    "Enter your email address in the username field. The 'grant_type', 'scope', 'client_id', and 'client_secret' fields are ignored."
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends()
) -> Result[UserLoginRes]:
    return auth_service.login(form_data.username, form_data.password)

@router.post(
    "/refresh", 
    response_model=Result[UserLoginRes],
    summary="Odśwież token dostępu"
)
async def refresh_token(
    req: RefreshTokenReq,
    auth_service: AuthService = Depends()
) -> Result[UserLoginRes]:
    return auth_service.refresh(req)