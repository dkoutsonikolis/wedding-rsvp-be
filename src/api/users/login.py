from fastapi import Depends, HTTPException, Request, status

from api.users.schemas import LoginRequest, LoginResponse, UserPublic
from config import settings
from domains.users.dependencies import get_users_service
from domains.users.exceptions import InvalidCredentialsError
from domains.users.jwt import create_access_token, create_refresh_token
from domains.users.service import UsersService
from middleware.limiter import limiter


@limiter.limit(settings.RATE_LIMIT_AUTH_LOGIN)
async def login(
    request: Request,
    body: LoginRequest,
    service: UsersService = Depends(get_users_service),
) -> LoginResponse:
    try:
        user = await service.authenticate(email=body.email, password=body.password)
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    access_token = create_access_token(user_id=user.id, email=user.email)
    refresh_token = create_refresh_token(user_id=user.id, email=user.email)
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_expires_in=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        user=UserPublic.model_validate(user),
    )
