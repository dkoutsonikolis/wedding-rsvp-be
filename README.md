# FastAPI Template

A modern FastAPI template with async SQLModel, Alembic migrations, Docker support, PyJWT-based auth, and a clean domain-driven layout.

## Features

- 🚀 **FastAPI** with async/await support
- 🗄️ **SQLModel** as ORM for database models (async PostgreSQL)
- ⚙️ **pydantic-settings** for type-safe configuration management
- 📦 **uv** for fast dependency management
- 🐳 **Docker** for containerized development
- 🔄 **Alembic** for database migrations
- 📁 **Domain-driven** project structure
- 🔥 **Hot reload** in development mode
- ✅ **Pre-commit hooks** for code quality
- 🧪 **Pytest** for testing with async support
- 🔍 **Ruff** for fast linting and formatting
- 📝 **MyPy** for static type checking
- 🚢 **GitHub Actions** CI/CD for automated testing and linting
- 🔐 **Auth** — register, login, **refresh tokens** (rotated on `POST /api/v1/auth/refresh`), **`GET /api/v1/user`** (Bearer access JWT) with bcrypt and **PyJWT**; **rate limits** on auth routes via **slowapi**
- 📋 **Consistent API errors** — validation and HTTP exceptions return `{ "detail": "..." }` via shared schemas
- 📤 **API response models** — example `messages` routes return Pydantic DTOs (`MessageRead`), not raw ORM objects

## Prerequisites

- **Python** (version specified in `.python-version`) - Install via `pyenv` (recommended for managing multiple Python versions) or use `uv` to manage it automatically
- **Docker** and **Docker Compose**

**Note:** If you use `pyenv` to manage Python versions, you can easily switch between different Python versions for different projects. `uv` will automatically use the Python version set by `pyenv` and create a `.venv` for you - no need for `pyenv-virtualenv`.

## Quick Start

### 0. Set Up Python Version (if using pyenv)

If you're using `pyenv` to manage Python versions:

```bash
# Install the Python version specified in .python-version (if not already installed)
pyenv install $(cat .python-version)

# The project includes a .python-version file, so pyenv will automatically
# use the correct Python version when you cd into this directory
```

This ensures `uv` uses the correct Python version. The project already includes a `.python-version` file, so pyenv will automatically use it. If you need to change the Python version for this project, you can run `pyenv local <version>` (which updates the `.python-version` file) or edit the file directly.

### 1. Install uv

You have two options:

**Option A: Install uv globally (simpler)**
```bash
make install-uv
```
This installs `uv` globally via pip. Simple and works for most cases.

**Option B: Install uv in a pyenv virtualenv (more control)**
```bash
# Create a pyenv virtualenv with the project's Python version
# The virtualenv name includes the Python version for clarity
pyenv virtualenv $(cat .python-version) fast-api-template-$(cat .python-version)

# Activate it
pyenv activate fast-api-template-$(cat .python-version)

# Install uv in this virtualenv
make install-uv
```
This approach allows you to manage different `uv` versions per project and keeps `pyenv` as your only global tool. Then `uv` will manage the project's `.venv` for dependencies.

### 2. Set Up Environment Variables

```bash
make setup-env
```

This creates a `.env` file from `.env.example`. Review and update the values if needed for your local setup.

**Note:** `.env` is gitignored - it contains your local development secrets. In staging/production, environment variables are set directly in the deployment platform (Docker, Kubernetes, cloud services, etc.).

**Secrets:** Change **`JWT_SECRET_KEY`** (and any other defaults) before deploying. The template ships dev-friendly defaults only.

**What the app reads:** Pydantic **`Settings`** only require **`DATABASE_URL`** (plus optional flags such as `DEBUG`, CORS, JWT, logging). The **`POSTGRES_*`** variables in `.env.example` exist for the **Docker Compose `db` service**; Compose substitutes them into the Postgres container—they are not loaded into `Settings`.

**CORS:** If **`CORS_CREDENTIALS=True`** and **`CORS_ORIGINS=*`**, browsers will not send credentialed requests successfully. The app logs a **warning** on startup in that case; use an explicit comma-separated origin list when you need cookies or `Authorization` from browser clients.

### 3. Install Dependencies Locally

```bash
make install
```

This creates a local `.venv` with all dependencies for IDE support.

### 4. Start Docker Containers

```bash
make up
```

This builds and starts the database and application containers.

### 5. Database schema

With Docker, **migrations run automatically** when the app container starts. To apply them manually (for example after generating a new revision):

```bash
make migrate
```

### 6. Set Up Pre-commit Hooks (Optional but Recommended)

```bash
make pre-commit-install
```

This installs pre-commit hooks that automatically run code quality checks (formatting, linting, type checking) before each commit. This helps maintain code quality and consistency.

### 7. Access the Application

- **Root**: http://localhost:8000
- **Liveness**: `GET /health` — process is up (no dependency checks)
- **Readiness**: `GET /ready` — checks database connectivity via the same session dependency as the API (overridden in tests to use `app_db_test`)
- **Versioned API** (`/api/v1/…`):
  - `GET|POST /api/v1/messages/` — example resource (list + create)
  - `POST /api/v1/auth/register` — create user (`email`, `password` min 8 characters); response is `{ id, email }`
  - `POST /api/v1/auth/login` — returns `access_token`, `refresh_token`, `expires_in` / `refresh_expires_in` (seconds), and `user`
  - `POST /api/v1/auth/refresh` — body `{ "refresh_token": "..." }`; returns a new token pair (previous refresh JWTs are not blacklisted—stateless rotation only)
  - `GET /api/v1/user` — current user; send header `Authorization: Bearer <access_token>` (OpenAPI “Authorize” uses the same scheme)
- **Rate limits** (per client IP by default): register `5/minute`, login `10/minute`, refresh `30/minute` — override with `RATE_LIMIT_AUTH_*` in `.env`
- **API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## Development Workflow

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
make test path=tests/api/messages/test_create.py
make test path=tests/api/users/test_login.py

# Run tests in a specific directory
make test path=tests/api/
```

When running tests **on the host** (not inside Docker), ensure `DATABASE_URL` uses **`localhost`** as the database host (see `.env.example`). The test fixtures rewrite the hostname from `db` to `localhost` when you are not inside a container.

Tests use PostgreSQL. The suite creates a separate database (`app_db_test`) from your `DATABASE_URL` so development data in `app_db` is not touched. The test layout mirrors the source tree:
- `tests/api/` - API endpoint tests
- `tests/domains/` - Domain logic tests

**Note:** Make sure Docker containers are running (`make up`) before running tests, as they connect to the PostgreSQL database container.

**Rate limits in tests:** `tests/conftest.py` sets high `RATE_LIMIT_AUTH_*` values before the app is imported so the suite does not share one IP and hit production-like limits. To assert `429` behavior, lower those env vars in a dedicated test module loaded before `main` or call the limiter in a focused integration test.

### Code Quality

```bash
# Format code (auto-fix formatting issues)
make format

# Auto-fix what Ruff can fix (format + lint --fix)
make fix

# Check formatting, lint, and type-check (CI-style; does not modify files)
make lint
```

These commands use:
- **Ruff** for fast linting and formatting (replaces Black, isort, flake8, etc.)
- **MyPy** for static type checking

### Pre-commit Hooks

If you've installed pre-commit hooks (`make pre-commit-install`), they will automatically run before each commit:
- Code formatting (ruff format)
- Linting (ruff check)
- Type checking (mypy)
- Other checks (YAML, JSON, trailing whitespace, etc.)

To manually run pre-commit hooks on all files:
```bash
pre-commit run --all-files
```

### Adding a New Package

```bash
make add pkg=package-name
make build  # Rebuild Docker to include new package
```

### Creating Database Migrations

```bash
make migrations msg="description of changes"
```

### Stopping Containers

```bash
make down
```

## Available Make Commands

| Command | Description |
|---------|-------------|
| `make install-uv` | Install `uv` package manager locally |
| `make setup-env` | Create `.env` file from `.env.example` (first-time setup) |
| `make install` | Install all dependencies locally (for IDE support) |
| `make add pkg=<name>` | Add a new Python package |
| `make build` | Build Docker containers |
| `make up` | Start Docker containers (builds if needed) |
| `make down` | Stop Docker containers |
| `make restart` | `down` then `up` |
| `make migrate` | Run database migrations |
| `make migrations msg="<msg>"` | Create a new migration file |
| `make test path=<path>` | Run tests (optional path to specific test file/directory) |
| `make format` | Format code with ruff |
| `make fix` | Format and apply safe ruff fixes |
| `make lint` | Check format, lint, and run mypy (no writes) |
| `make pre-commit-install` | Install pre-commit hooks |

## Project Structure

```
.
├── AGENTS.md                # Pointers for AI agents → `.github/instructions/`
├── .cursor/
│   └── rules/               # Cursor: `agents.mdc` (alwaysApply) → same guidance
├── src/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Settings and configuration
│   ├── api/                 # API layer (HTTP handlers, schemas)
│   │   ├── common/          # Shared API types, `get_current_user`, error helpers
│   │   ├── messages/        # Example resource
│   │   └── users/           # Auth: register / login (JWT)
│   ├── db/                  # Database configuration
│   │   ├── db.py            # Database engine and session
│   │   └── migrations/      # Alembic migrations
│   ├── domains/             # Domain modules (business logic)
│   │   ├── messages/        # Example domain (models, repository, service, dependencies)
│   │   └── users/           # Users + auth helpers (models, repository, service, password, jwt, …)
│   ├── middleware/          # Custom middleware
│   └── utils/               # Utility functions
├── tests/                   # Test files
│   ├── api/                 # API endpoint tests
│   ├── domains/             # Domain logic tests
│   └── fixtures/            # Shared test fixtures
├── scripts/                 # Utility scripts
├── .github/
│   ├── instructions/        # Path-scoped agent rules (`*.instructions.md`, YAML `applyTo` globs)
│   └── workflows/
│       └── ci.yml           # GitHub Actions CI workflow
├── docker-compose.yml       # Docker services configuration
├── Dockerfile               # Multi-stage Docker build (production stage runs as non-root `appuser`)
├── Makefile                 # Development commands
├── pyproject.toml           # Project dependencies and tool configs
└── .pre-commit-config.yaml  # Pre-commit hooks configuration
```

### Import Style

The project uses a clean import style without the `src.` prefix. The `src/` directory is added to `PYTHONPATH` (via Docker environment variables and test configuration), so imports look like:

```python
from api.messages.schemas import MessageRead
from domains.messages.models import Message
from domains.users.models import User
from config import settings
from db.db import get_session
```

Instead of:

```python
from src.domains.messages.models import Message
from src.config import settings
from src.db.db import get_session
```

This makes imports cleaner and more standard for service repositories.

## IDE Configuration

If you use **VS Code** or **Cursor**, you can add the following configuration for better IDE support:

1. Create a `.vscode` folder in the project root (if it doesn't exist)
2. Create a `settings.json` file inside `.vscode/` with the following content:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.analysis.extraPaths": [
    "${workspaceFolder}/src"
  ],
  "python.analysis.autoImportCompletions": true,
  "python.analysis.typeCheckingMode": "basic",
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/*.pyo": true,
    "**/.pytest_cache": true,
    "**/.mypy_cache": true
  }
}
```

This configuration:
- Sets the Python interpreter to use the project's `.venv`
- Adds the `src` directory to Python analysis paths for better imports
- Hides `__pycache__` folders from the file explorer
- Enables basic type checking

**Note:** The `.vscode/` folder is gitignored, so each developer can configure their IDE as they prefer. This is just a suggested configuration for VS Code/Cursor users.

## CI/CD

The project includes a GitHub Actions workflow (`.github/workflows/ci.yml`) that automatically runs on push and pull requests to the `main` branch.

The CI pipeline includes:
- **Tests**: Installs dependencies with **uv**, starts **Docker Compose** (database + app image build), runs **`make test`** on the host against `localhost:5432` (tests use the isolated `app_db_test` database)
- **Linting**: **`make lint`** (ruff format check, ruff check, mypy)

The workflow uses **uv** with caching and **Python 3.13** (matches project requirements).

To view CI status, check the "Actions" tab in your GitHub repository.
