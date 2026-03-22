from fastapi import Depends

from api.common.dependencies import get_current_user
from domains.users.models import User

from .schemas import UserPublic


async def get_user(user: User = Depends(get_current_user)) -> UserPublic:
    return UserPublic.model_validate(user)
