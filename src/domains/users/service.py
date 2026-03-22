from uuid import UUID

from jwt.exceptions import PyJWTError

from domains.users.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from domains.users.jwt import decode_access_token, decode_refresh_token
from domains.users.models import User
from domains.users.password import hash_password, verify_password
from domains.users.repository import UsersRepository
from utils.logging import get_logger

logger = get_logger(__name__)


class UsersService:
    def __init__(self, repository: UsersRepository):
        self.repository = repository

    async def register(self, *, email: str, password: str) -> User:
        normalized_email = email.lower().strip()
        if await self.repository.get_by_email(normalized_email):
            raise UserAlreadyExistsError(f"Email '{normalized_email}' is already registered")
        password_hash = hash_password(password)
        try:
            return await self.repository.create(email=normalized_email, password_hash=password_hash)
        except Exception as e:
            logger.error(f"Failed to create user: {e}", exc_info=True)
            raise

    async def authenticate(self, *, email: str, password: str) -> User:
        normalized_email = email.lower().strip()
        user = await self.repository.get_by_email(normalized_email)
        if user is None or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Invalid email or password")
        return user

    async def authenticate_token(self, token: str) -> User:
        try:
            payload = decode_access_token(token)
        except PyJWTError as e:
            raise InvalidCredentialsError("Invalid authentication credentials") from e

        if not isinstance(payload, dict):
            raise InvalidCredentialsError("Invalid authentication credentials")
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise InvalidCredentialsError("Invalid authentication credentials")
        try:
            user_id = UUID(str(user_id_str))
        except ValueError as e:
            raise InvalidCredentialsError("Invalid authentication credentials") from e

        user = await self.repository.get_by_id(user_id)
        if user is None:
            raise InvalidCredentialsError("Invalid authentication credentials")
        return user

    async def authenticate_refresh_token(self, token: str) -> User:
        try:
            payload = decode_refresh_token(token)
        except PyJWTError as e:
            raise InvalidCredentialsError("Invalid refresh token") from e

        if not isinstance(payload, dict):
            raise InvalidCredentialsError("Invalid refresh token")
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise InvalidCredentialsError("Invalid refresh token")
        try:
            user_id = UUID(str(user_id_str))
        except ValueError as e:
            raise InvalidCredentialsError("Invalid refresh token") from e

        user = await self.repository.get_by_id(user_id)
        if user is None:
            raise InvalidCredentialsError("Invalid refresh token")
        return user
