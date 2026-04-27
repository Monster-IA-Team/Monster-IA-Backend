from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from services.auth_services import AuthService
from helpers.result import Result

from dto.response.login_res import UserLoginRes
 
from dto.request.refresh_req import RefreshTokenReq
from dto.request.register_req import RegisterRequest
from dto.request.reset_password_req import ResetPasswordRequet

router = APIRouter(
    prefix="/api/auth",
    tags=["Auth"]
)

@router.post(
    "/login", 
    response_model=Result[UserLoginRes],
    summary="Authenticate user and obtain tokens",
    description="""
    Authenticates a user and returns a pair of Access and Refresh tokens.
    
    **Important:** In the Swagger UI authorization form, please enter your **email address** in the `username` field. 
    The fields `grant_type`, `scope`, `client_id`, and `client_secret` are ignored.

    **Test Accounts:**
    * **Admin:** `admin@example.com` / `Admin123!`
    * **User:** `user@example.com` / `User123!`
    """
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends()
) -> Result[UserLoginRes]:
    return auth_service.login(form_data.username, form_data.password)

@router.post(
    "/refresh", 
    response_model=Result[UserLoginRes],
    summary="Refresh access token",
    description="Generates a new pair of Access and Refresh tokens using a valid, unexpired Refresh token."
)
async def refresh_token(
    req: RefreshTokenReq,
    auth_service: AuthService = Depends()
) -> Result[UserLoginRes]:
    return auth_service.refresh(req)

@router.post(
    "/register", 
    response_model=Result[None], 
    summary="Register a new account",
    description="Creates a new user account with the default 'User' role." + 
    " The account is created as inactive, and an activation email is sent in the background." +
    " Field 'is_prefers_sugar_free' is optional and if set this filed to null taste progile set as no preference."
)
async def register(
    req: RegisterRequest,
    background_tasks: BackgroundTasks,
    auth_service: AuthService = Depends()
) -> Result[None]:
    return auth_service.register(req, background_tasks)

@router.get(
    "/activate", 
    response_model=Result[None], 
    summary="Activate user account",
    description="Activates a newly registered account using the JWT token sent via email. Once activated, the user can log in."
)
async def activate_account(
    token: str,
    auth_service: AuthService = Depends()
) -> Result[None]:
    return auth_service.activate_account(token)

@router.post(
    "/reset-password", 
    response_model=Result[None], 
    summary="Request a password reset email",
    description="Initiates the password reset process. If the provided email exists in the database, a secure reset link is sent. " + 
    "To prevent email enumeration attacks, this endpoint always returns a success response."
)
async def reset_password(
    email: str,
    background_tasks: BackgroundTasks,
    auth_service: AuthService = Depends()
) -> Result[None]:
    return auth_service.forget_password(email, background_tasks)

@router.post(
    "/reset-password/confirm", 
    response_model=Result[None], 
    summary="Confirm password reset and set new password",
    description="Completes the password reset process. Requires the JWT token from the reset email and the new password. " + 
    "The new password must meet the security requirements."
)
async def confirm_reset_password(
    req: ResetPasswordRequet,
    auth_service: AuthService = Depends()
) -> Result[None]:
    return auth_service.reset_password(req)


@router.post(
    "/swagger-token",
    include_in_schema=False
)
async def login_for_swagger(
        form_data: OAuth2PasswordRequestForm = Depends(),
        auth_service: AuthService = Depends()
):
    result = auth_service.login(form_data.username, form_data.password)

    if result.status_code != 200:
        raise HTTPException(status_code=result.status_code, detail=result.message)

    return {
        "access_token": result.data.access_token,
        "token_type": "bearer"
    }