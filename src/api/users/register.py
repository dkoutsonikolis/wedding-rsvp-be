from fastapi import Depends, HTTPException, Request, status

from api.users.schemas import UserPublic, UserRegister
from config import settings
from domains.users.dependencies import get_users_service
from domains.users.exceptions import UserAlreadyExistsError
from domains.users.service import UsersService
from middleware.limiter import limiter


@limiter.limit(settings.RATE_LIMIT_AUTH_REGISTER)
async def register_user(
    request: Request,
    body: UserRegister,
    service: UsersService = Depends(get_users_service),
) -> UserPublic:
    try:
        user = await service.register(email=body.email, password=body.password)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    return UserPublic.model_validate(user)
