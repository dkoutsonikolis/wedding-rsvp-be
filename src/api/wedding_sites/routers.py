from typing import Any

from fastapi import APIRouter, status

from api.agent.schemas import AgentTurnResponse
from api.common import get_error_response
from api.rsvp_responses.schemas import RsvpResponsesPageResponse, RsvpResponsesSummaryResponse

from .agent_turn import agent_turn_for_site
from .chat_history import get_wedding_site_chat_history
from .create import create_wedding_site
from .get_one import get_wedding_site
from .get_rsvp_responses_summary import get_wedding_site_rsvp_responses_summary
from .list import list_wedding_sites
from .list_rsvp_responses import list_wedding_site_rsvp_responses
from .patch import patch_wedding_site
from .schemas import AgentChatHistoryPageResponse, WeddingSiteRead

wedding_sites_router = APIRouter(prefix="/wedding-sites", tags=["wedding-sites"])

_auth_responses: dict[int | str, dict[str, Any]] = {
    status.HTTP_401_UNAUTHORIZED: get_error_response(
        status.HTTP_401_UNAUTHORIZED,
        "Invalid authentication credentials",
    ),
}

wedding_sites_router.add_api_route(
    "",
    list_wedding_sites,
    methods=["GET"],
    response_model=list[WeddingSiteRead],
    responses=_auth_responses,
    summary="List wedding sites for the current user",
)

wedding_sites_router.add_api_route(
    "",
    create_wedding_site,
    methods=["POST"],
    response_model=WeddingSiteRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        **_auth_responses,
        status.HTTP_409_CONFLICT: get_error_response(
            status.HTTP_409_CONFLICT,
            "Slug already in use or account already has a wedding site",
        ),
        status.HTTP_422_UNPROCESSABLE_CONTENT: get_error_response(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "Validation error",
        ),
    },
    summary="Create a wedding site",
)

wedding_sites_router.add_api_route(
    "/{site_id}/agent/turn",
    agent_turn_for_site,
    methods=["POST"],
    response_model=AgentTurnResponse,
    responses={
        **_auth_responses,
        status.HTTP_404_NOT_FOUND: get_error_response(
            status.HTTP_404_NOT_FOUND,
            "Wedding site not found",
        ),
        status.HTTP_422_UNPROCESSABLE_CONTENT: get_error_response(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "Validation error",
        ),
    },
    summary="Owner agent turn (persists WeddingSite.config; stub reply until LLM is wired)",
)

wedding_sites_router.add_api_route(
    "/{site_id}/chat-history",
    get_wedding_site_chat_history,
    methods=["GET"],
    response_model=AgentChatHistoryPageResponse,
    responses={
        **_auth_responses,
        status.HTTP_404_NOT_FOUND: get_error_response(
            status.HTTP_404_NOT_FOUND,
            "Wedding site not found",
        ),
        status.HTTP_422_UNPROCESSABLE_CONTENT: get_error_response(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "Validation error",
        ),
    },
    summary="Get paginated chat history for a wedding site",
)

wedding_sites_router.add_api_route(
    "/{site_id}/rsvp-responses/summary",
    get_wedding_site_rsvp_responses_summary,
    methods=["GET"],
    response_model=RsvpResponsesSummaryResponse,
    responses={
        **_auth_responses,
        status.HTTP_404_NOT_FOUND: get_error_response(
            status.HTTP_404_NOT_FOUND,
            "Wedding site not found",
        ),
    },
    summary="RSVP overview aggregates and preview rows for owner dashboard",
)

wedding_sites_router.add_api_route(
    "/{site_id}/rsvp-responses",
    list_wedding_site_rsvp_responses,
    methods=["GET"],
    response_model=RsvpResponsesPageResponse,
    responses={
        **_auth_responses,
        status.HTTP_404_NOT_FOUND: get_error_response(
            status.HTTP_404_NOT_FOUND,
            "Wedding site not found",
        ),
        status.HTTP_422_UNPROCESSABLE_CONTENT: get_error_response(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "Validation error",
        ),
    },
    summary="List RSVP responses for a wedding site (newest first, cursor pagination)",
)

wedding_sites_router.add_api_route(
    "/{site_id}",
    get_wedding_site,
    methods=["GET"],
    response_model=WeddingSiteRead,
    responses={
        **_auth_responses,
        status.HTTP_404_NOT_FOUND: get_error_response(
            status.HTTP_404_NOT_FOUND,
            "Wedding site not found",
        ),
    },
    summary="Get a wedding site by id",
)

wedding_sites_router.add_api_route(
    "/{site_id}",
    patch_wedding_site,
    methods=["PATCH"],
    response_model=WeddingSiteRead,
    responses={
        **_auth_responses,
        status.HTTP_404_NOT_FOUND: get_error_response(
            status.HTTP_404_NOT_FOUND,
            "Wedding site not found",
        ),
        status.HTTP_409_CONFLICT: get_error_response(
            status.HTTP_409_CONFLICT,
            "Slug already in use or account already has a wedding site",
        ),
        status.HTTP_422_UNPROCESSABLE_CONTENT: get_error_response(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "Validation error",
        ),
    },
    summary="Partially update a wedding site",
)
