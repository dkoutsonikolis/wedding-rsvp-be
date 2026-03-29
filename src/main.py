from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy import text
from sqlmodel.ext.asyncio.session import AsyncSession

from api.common.schemas import ErrorResponse
from api.public import public_agent_router
from api.users import auth_router, users_router
from api.wedding_sites import wedding_sites_router
from config import settings
from db.db import engine, get_session
from middleware.limiter import limiter
from middleware.logging_middleware import RequestLoggingMiddleware
from utils.logging import get_logger, setup_logging

# Setup logging
setup_logging(debug=settings.DEBUG)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown: dispose async engine on exit."""
    # Startup
    logger.info("Application starting up...")
    if settings.CORS_CREDENTIALS and settings.CORS_ORIGINS.strip() == "*":
        logger.warning(
            "CORS_CREDENTIALS is True but CORS_ORIGINS is '*'. "
            "Browsers reject credentialed cross-origin requests with a wildcard origin; "
            "set CORS_ORIGINS to an explicit comma-separated list in production."
        )
    yield
    # Shutdown
    logger.info("Application shutting down...")
    await engine.dispose()
    logger.info("Database engine disposed")


app = FastAPI(title="Wedding RSVP API", lifespan=lifespan)
app.state.limiter = limiter

# CORS middleware
# Parse CORS settings from environment variables
cors_origins = settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS != "*" else ["*"]
cors_methods = settings.CORS_METHODS.split(",") if settings.CORS_METHODS != "*" else ["*"]
cors_headers = settings.CORS_HEADERS.split(",") if settings.CORS_HEADERS != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in cors_origins],
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=[method.strip() for method in cors_methods],
    allow_headers=[header.strip() for header in cors_headers],
)

app.add_middleware(SlowAPIMiddleware)

# Request/Response logging middleware
if settings.LOG_REQUESTS:
    app.add_middleware(RequestLoggingMiddleware)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """422: map Pydantic validation errors to a single human-readable `detail` string."""
    logger.warning(f"Validation error: {exc.errors()}")
    error_messages = []
    for error in exc.errors():
        msg = error.get("msg", str(error))
        loc = error.get("loc", [])
        if loc:
            # Filter out location prefixes like "path", "query", "body"
            field_path = " -> ".join(
                str(item) for item in loc if item not in ("body", "path", "query")
            )
            error_messages.append(f"{field_path}: {msg}" if field_path else msg)
        else:
            error_messages.append(msg)
    error_detail = "; ".join(error_messages)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=ErrorResponse(detail=error_detail).model_dump(),
    )


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
    """429: align with `ErrorResponse` shape used elsewhere."""
    detail = str(exc.detail) if exc.detail is not None else "Too many requests"
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content=ErrorResponse(detail=detail).model_dump(),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Return `HTTPException` as `ErrorResponse` JSON."""
    logger.warning(f"HTTP error {exc.status_code}: {exc.detail}")
    detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(detail=detail).model_dump(),
        headers=exc.headers,
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """500: log server-side, return generic `detail` to the client."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(detail="Internal server error").model_dump(),
    )


# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/ready")
async def ready(session: AsyncSession = Depends(get_session)):
    try:
        await session.execute(text("SELECT 1"))
    except Exception as e:
        logger.warning("Readiness check failed: %s", e)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=ErrorResponse(detail="Database unavailable").model_dump(),
        )
    return {"status": "ok"}


# Versioned API
api_v1 = APIRouter(prefix="/api/v1")
api_v1.include_router(auth_router)
api_v1.include_router(users_router)
api_v1.include_router(public_agent_router)
api_v1.include_router(wedding_sites_router)

app.include_router(api_v1)
