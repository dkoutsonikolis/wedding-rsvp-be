from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore extra env vars (e.g. app-specific secrets in downstream projects)
    )

    # Application database (PostgreSQL async URL). Compose-only vars like POSTGRES_USER live in .env
    # for the db service but are not read by this app.
    DATABASE_URL: str
    DEBUG: bool = False

    # CORS settings
    CORS_ORIGINS: str = "*"  # Comma-separated list of allowed origins, or "*" for all
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: str = "*"  # Comma-separated list of allowed methods, or "*" for all
    CORS_HEADERS: str = "*"  # Comma-separated list of allowed headers, or "*" for all

    # Logging settings
    LOG_REQUESTS: bool = True  # Enable request/response logging middleware

    # JWT (access + refresh; login, POST /api/v1/auth/refresh)
    JWT_SECRET_KEY: str = "change-this-jwt-secret-key-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Rate limits for auth routes (slowapi format, e.g. "10/minute")
    RATE_LIMIT_AUTH_REGISTER: str = "5/minute"
    RATE_LIMIT_AUTH_LOGIN: str = "10/minute"
    RATE_LIMIT_AUTH_REFRESH: str = "30/minute"

    # Anonymous agent trial (Phase 3)
    ANONYMOUS_AGENT_TOKEN_PEPPER: str = ""
    ANONYMOUS_AGENT_SESSION_TTL_DAYS: int = 7
    RATE_LIMIT_PUBLIC_AGENT_SESSION: str = "30/minute"
    RATE_LIMIT_PUBLIC_AGENT_TURN: str = "60/minute"

    # Agent: explicit backend choice (set in .env; factory runs at app startup).
    # auto = Gemini if GOOGLE_API_KEY, else Anthropic if ANTHROPIC_API_KEY, else Groq if GROQ_API_KEY, else stub.
    AGENT_BACKEND: Literal["auto", "stub", "gemini", "groq", "anthropic"] = "auto"
    # Max completed user+assistant turns from chat history included in the model prompt (owner sites may store more).
    AGENT_MODEL_HISTORY_MAX_TURNS: int = 5

    # Gemini via Generative Language API (same env name as Pydantic AI / google-genai).
    GOOGLE_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # Anthropic Claude — https://console.anthropic.com/
    ANTHROPIC_API_KEY: str | None = None
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"
    # Prompt caching (system instructions + tool definitions; see Anthropic / Pydantic AI docs).
    ANTHROPIC_PROMPT_CACHE: bool = True
    ANTHROPIC_PROMPT_CACHE_TTL: Literal["5m", "1h"] = "1h"

    # Groq Cloud API — https://console.groq.com/keys
    GROQ_API_KEY: str | None = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"


settings = Settings()  # type: ignore[call-arg]
