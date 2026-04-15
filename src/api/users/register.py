from fastapi import Depends, HTTPException, Request, status

from api.users.schemas import LoginResponse, UserPublic, UserRegister
from config import settings
from domains.users.dependencies import get_users_service
from domains.users.exceptions import UserAlreadyExistsError
from domains.users.jwt import create_access_token, create_refresh_token
from domains.users.service import UsersService
from middleware.limiter import limiter


@limiter.limit(settings.RATE_LIMIT_AUTH_REGISTER)
async def register_user(
    request: Request,
    body: UserRegister,
    service: UsersService = Depends(get_users_service),
) -> LoginResponse:
    try:
        user = await service.register(
            email=body.email,
            password=body.password,
            anonymous_session_token=body.anonymous_session_token,
        )
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    access_token = create_access_token(user_id=user.id, email=user.email)
    refresh_token = create_refresh_token(user_id=user.id, email=user.email)
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_expires_in=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        user=UserPublic.model_validate(user),
    )
