from uuid import UUID

from jwt.exceptions import PyJWTError

from domains.anonymous_agent_sessions.exceptions import (
    AnonymousSessionExpiredError,
    AnonymousSessionNotFoundError,
)
from domains.anonymous_agent_sessions.service import AnonymousAgentSessionsService
from domains.users.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from domains.users.jwt import decode_access_token, decode_refresh_token
from domains.users.models import User
from domains.users.password import hash_password, verify_password
from domains.users.repository import UsersRepository
from domains.wedding_sites.service import WeddingSitesService
from utils.logging import get_logger

logger = get_logger(__name__)


class UsersService:
    def __init__(
        self,
        users_repository: UsersRepository,
        anonymous_sessions_service: AnonymousAgentSessionsService,
        wedding_sites_service: WeddingSitesService,
    ):
        self.users_repository = users_repository
        self._anonymous_sessions_service = anonymous_sessions_service
        self._wedding_sites_service = wedding_sites_service

    async def _copy_anonymous_site_to_user(
        self, user_id: UUID, anonymous_session_token: str
    ) -> None:
        try:
            anonymous_session = (
                await self._anonymous_sessions_service.get_active_by_plaintext_token_for_update(
                    anonymous_session_token
                )
            )
        except (AnonymousSessionNotFoundError, AnonymousSessionExpiredError):
            logger.info("Skipping draft import for user %s due to invalid session token", user_id)
            return
        await self._wedding_sites_service.create(
            owner_user_id=user_id,
            config=dict(anonymous_session.config),
        )
        await self._anonymous_sessions_service.expire_session(anonymous_session)

    async def register(
        self,
        email: str,
        password: str,
        anonymous_session_token: str | None = None,
    ) -> User:
        normalized_email = email.lower().strip()
        if await self.users_repository.get_by_email(normalized_email):
            raise UserAlreadyExistsError(f"Email '{normalized_email}' is already registered")
        password_hash = hash_password(password)
        try:
            user = await self.users_repository.create(
                email=normalized_email, password_hash=password_hash
            )
        except Exception as e:
            logger.error(f"Failed to create user: {e}", exc_info=True)
            raise
        if anonymous_session_token is not None:
            await self._copy_anonymous_site_to_user(user.id, anonymous_session_token)
        return user

    async def authenticate(self, email: str, password: str) -> User:
        normalized_email = email.lower().strip()
        user = await self.users_repository.get_by_email(normalized_email)
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

        user = await self.users_repository.get_by_id(user_id)
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

        user = await self.users_repository.get_by_id(user_id)
        if user is None:
            raise InvalidCredentialsError("Invalid refresh token")
        return user
