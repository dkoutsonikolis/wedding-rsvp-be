from typing import Any

from .schemas import ErrorResponse


def get_error_response(status_code: int, description: str) -> dict[str, Any]:
    return {
        "model": ErrorResponse,
        "description": description,
    }
