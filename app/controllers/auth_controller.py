from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from services.auth_services import AuthService
from helpers.result import Result

from dto.response.login_res import UserLoginRes
 
from dto.request.refresh_req import RefreshTokenReq
from dto.request.register_req import RegisterRequset

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

@router.post("/register", response_model=Result[None], summary="Zarejestruj konto")
async def register(
    req: RegisterRequset,
    background_tasks: BackgroundTasks,
    auth_service: AuthService = Depends()
) -> Result[None]:
    return auth_service.register(req, background_tasks)

@router.get("/activate", response_model=Result[None], summary="Aktywuj konto z linku w mailu")
async def activate_account(
    token: str,
    auth_service: AuthService = Depends()
) -> Result[None]:
    return auth_service.activate_account(token)