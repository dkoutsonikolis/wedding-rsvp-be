from typing import Any

from fastapi import APIRouter, status

from api.agent.schemas import AgentTurnResponse
from api.common import get_error_response

from .agent_turn import agent_turn_for_site
from .create import create_wedding_site
from .delete import delete_wedding_site
from .get_one import get_wedding_site
from .list import list_wedding_sites
from .patch import patch_wedding_site
from .schemas import WeddingSiteRead

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
            "Slug already in use",
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
            "Slug already in use",
        ),
        status.HTTP_422_UNPROCESSABLE_CONTENT: get_error_response(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "Validation error",
        ),
    },
    summary="Partially update a wedding site",
)

wedding_sites_router.add_api_route(
    "/{site_id}",
    delete_wedding_site,
    methods=["DELETE"],
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        **_auth_responses,
        status.HTTP_404_NOT_FOUND: get_error_response(
            status.HTTP_404_NOT_FOUND,
            "Wedding site not found",
        ),
    },
    summary="Delete a wedding site",
)
