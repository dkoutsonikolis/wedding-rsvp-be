from fastapi import APIRouter, status

from api.common import get_error_response

from .login import login
from .refresh import refresh_tokens
from .register import register_user
from .schemas import LoginResponse, UserPublic
from .user import get_user

auth_router = APIRouter(prefix="/auth", tags=["auth"])

users_router = APIRouter(prefix="", tags=["users"])

auth_router.add_api_route(
    "/register",
    register_user,
    methods=["POST"],
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_409_CONFLICT: get_error_response(
            status.HTTP_409_CONFLICT, "Email already registered"
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
    summary="Register a new user",
)

auth_router.add_api_route(
    "/login",
    login,
    methods=["POST"],
    response_model=LoginResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: get_error_response(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid credentials",
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
    summary="Login and receive access and refresh tokens",
)

auth_router.add_api_route(
    "/refresh",
    refresh_tokens,
    methods=["POST"],
    response_model=LoginResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: get_error_response(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid refresh token",
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
    summary="Exchange a refresh token for a new token pair (rotation)",
)

users_router.add_api_route(
    "/user",
    get_user,
    methods=["GET"],
    response_model=UserPublic,
    responses={
        status.HTTP_401_UNAUTHORIZED: get_error_response(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid authentication credentials",
        ),
    },
    summary="Get current authenticated user",
)
