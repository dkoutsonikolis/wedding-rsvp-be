from fastapi import APIRouter, status

from api.common import get_error_response

from .create import create_message
from .list import list_messages
from .schemas import MessageRead

router = APIRouter(prefix="/messages", tags=["messages"])

router.add_api_route(
    "/",
    list_messages,
    methods=["GET"],
    response_model=list[MessageRead],
    summary="List messages",
)

router.add_api_route(
    "/",
    create_message,
    methods=["POST"],
    response_model=MessageRead,
    responses={
        status.HTTP_422_UNPROCESSABLE_CONTENT: get_error_response(
            status.HTTP_422_UNPROCESSABLE_CONTENT, "Validation error"
        ),
    },
    summary="Create a message",
)
