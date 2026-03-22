from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from domains.users.dependencies import get_users_service
from domains.users.exceptions import InvalidCredentialsError
from domains.users.models import User
from domains.users.service import UsersService

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    service: UsersService = Depends(get_users_service),
) -> User:
    try:
        return await service.authenticate_token(credentials.credentials)
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
