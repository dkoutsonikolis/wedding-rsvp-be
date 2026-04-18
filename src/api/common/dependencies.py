from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from domains.users.dependencies import get_users_service
from domains.users.exceptions import InvalidCredentialsError
from domains.users.models import User
from domains.users.service import UsersService

security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


async def _authenticate_credentials(
    credentials: HTTPAuthorizationCredentials,
    service: UsersService,
) -> User:
    try:
        return await service.authenticate_token(credentials.credentials)
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    service: UsersService = Depends(get_users_service),
) -> User:
    return await _authenticate_credentials(credentials, service)


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(optional_security),
    service: UsersService = Depends(get_users_service),
) -> User | None:
    if credentials is None:
        return None
    return await _authenticate_credentials(credentials, service)
