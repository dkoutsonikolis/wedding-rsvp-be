from fastapi import APIRouter, status

from api.agent.schemas import (
    AgentSessionStateResponse,
    AgentTurnResponse,
    PublicAgentSessionCreateResponse,
)
from api.common import get_error_response
from api.public.schemas import PublicClientConfigResponse

from .client_config import get_public_client_config
from .contact import submit_contact_message
from .create_session import create_public_agent_session
from .session import get_public_agent_session_state
from .turn import public_agent_turn

public_agent_router = APIRouter(prefix="/public/agent", tags=["public-agent"])
public_router = APIRouter(prefix="/public", tags=["public"])

public_agent_router.add_api_route(
    "/sessions",
    create_public_agent_session,
    methods=["POST"],
    response_model=PublicAgentSessionCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_429_TOO_MANY_REQUESTS: get_error_response(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "Too many requests",
        ),
    },
    summary="Start an anonymous agent trial session",
)

public_agent_router.add_api_route(
    "/turn",
    public_agent_turn,
    methods=["POST"],
    response_model=AgentTurnResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: get_error_response(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid or expired session",
        ),
        status.HTTP_403_FORBIDDEN: get_error_response(
            status.HTTP_403_FORBIDDEN,
            "Trial limit reached",
        ),
        status.HTTP_422_UNPROCESSABLE_CONTENT: get_error_response(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "Validation error",
        ),
        status.HTTP_429_TOO_MANY_REQUESTS: get_error_response(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "Too many requests",
        ),
    },
    summary="Anonymous agent turn (3 interactions per session)",
)

public_agent_router.add_api_route(
    "/session",
    get_public_agent_session_state,
    methods=["GET"],
    response_model=AgentSessionStateResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: get_error_response(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid or expired session",
        ),
        status.HTTP_422_UNPROCESSABLE_CONTENT: get_error_response(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "Validation error",
        ),
        status.HTTP_429_TOO_MANY_REQUESTS: get_error_response(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "Too many requests",
        ),
    },
    summary="Get anonymous session state and full chat history",
)

public_router.add_api_route(
    "/client-config",
    get_public_client_config,
    methods=["GET"],
    response_model=PublicClientConfigResponse,
    summary="Get FE-visible public config (limits, etc.)",
)

public_router.add_api_route(
    "/contact",
    submit_contact_message,
    methods=["POST"],
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: get_error_response(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid authentication credentials",
        ),
        status.HTTP_422_UNPROCESSABLE_CONTENT: get_error_response(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "Validation error",
        ),
        status.HTTP_429_TOO_MANY_REQUESTS: get_error_response(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "Too many requests",
        ),
    },
    summary="Submit a public contact form message",
)
