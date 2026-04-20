from api.public.schemas import PublicClientConfigResponse
from config import settings


async def get_public_client_config() -> PublicClientConfigResponse:
    return PublicClientConfigResponse(
        agent_anon_message_max_chars=settings.AGENT_ANON_MESSAGE_MAX_CHARS,
        agent_user_message_max_chars=settings.AGENT_USER_MESSAGE_MAX_CHARS,
    )
