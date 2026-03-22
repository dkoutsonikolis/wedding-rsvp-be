from .schemas import ErrorResponse


def get_error_response(status_code: int, description: str) -> dict:
    return {
        "model": ErrorResponse,
        "description": description,
    }
