# syntax=docker/dockerfile:1

############################
# Base stage
############################
FROM python:3.13-slim AS base

# Copy uv binaries (recommended method)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency files first
COPY pyproject.toml uv.lock ./

# Install *only production dependencies* here
RUN uv sync --frozen --no-dev

############################
# Development stage
############################
FROM base AS development

# Install dev dependencies only (reuses cached base layer)
RUN uv sync --frozen

# Copy source code
COPY src ./src
COPY scripts ./scripts
COPY tests ./tests

# Expose app port
EXPOSE 8000

# Set environment vars for development
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src \
    UVICORN_RELOAD=true

# Run wait_for_db, migrations, then uvicorn with reload
CMD ["sh", "-c", "python scripts/wait_for_db.py && uv run alembic -c src/db/alembic.ini upgrade head && uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload"]

############################
# Production stage
############################
FROM base AS production

COPY src ./src
COPY scripts ./scripts

RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

CMD ["sh", "-c", "python scripts/wait_for_db.py && uv run alembic -c src/db/alembic.ini upgrade head && uv run uvicorn main:app --host 0.0.0.0 --port 8000"]
