---
applyTo: "src/**/*.py"
---

## Context (read first)

- **Stack:** FastAPI (async), SQLModel + SQLAlchemy async, PostgreSQL, Alembic, Pydantic v2, `PYTHONPATH` includes `src/` (imports **never** use a `src.` prefix).
- **Layout:** `api/<domain>/` = HTTP layer (routers, Pydantic IO). `domains/<domain>/` = persistence + business rules (models, repository, service, `dependencies.py`). `db/` = engine, session, migrations. `main.py` wires middleware, exception handlers, and `api_v1` router.
- **Session:** Use `Depends(get_session)` in routes; services receive `AsyncSession` via repositories. Do not run ad-hoc SQL in endpoint functions except where the codebase already does for infrastructure (e.g. health/readiness patterns).

---

## Priority when rules conflict

1. **Correctness & security** (secrets, authz, SQL injection, transactional integrity)
2. **Layering** (API thin → service → repository → DB)
3. **Consistency** with existing modules in this repo (mirror `wedding_sites` / `users` patterns)
4. **Style** (comments, docstrings)

---

## MUST

- **Imports:** `from config import settings`, `from domains...`, `from api...` — **never** `from src....`
- **Database access:** Only inside **repository** methods for that domain. **Services** call their domain’s repository. **Another domain’s data:** call that domain’s **service**, not its repository, from your service.
- **HTTP layer:** Request/response bodies use **Pydantic schemas** (`api/<domain>/schemas.py`). Do **not** expose SQLModel/table models as `response_model` or body params on routes (use DTOs like `UserPublic` or domain-specific `*Read` / `*Create` types).
- **Versioned routes:** New public HTTP endpoints live under **`/api/v1/...`** via routers included from `main.py` on `api_v1`. **Exception:** infrastructure routes **`/health`**, **`/ready`** stay on the app root.
- **Errors:** For documented OpenAPI errors on a route, use **`get_error_response(...)`** from `api.common` in `add_api_route(..., responses={...})`.
- **Logging:** Use **`get_logger(__name__)`** from `utils.logging` — **no** `print()`.
- **Migrations:** New/changed SQLModel tables must be reflected in **`src/db/migrations/env.py`** imports (for autogenerate) and a new Alembic revision.

---

## SHOULD

- **One class per file** for model, repository, and service in a domain. Multiple small related functions in one module are OK (e.g. `password.py`, `jwt.py`).
- **Enums:** Domain enums in `domains/<domain>/enums.py`, imported from models — not defined inline in `models.py`.
- **Naming:** Domain folder names plural (`users`, `wedding_sites`). Classes: `UsersRepository`, `UsersService`, dependency `get_users_service`. Prefer **`routers.py`** when a domain exposes more than one router (e.g. `auth_router` + `users_router`).
- **Variable names:** Do **not** use **single-letter** names for parameters, return-bound locals, or values carried across more than a line or two (e.g. `run_usage`, not `u`). **Exceptions:** idiomatic micro-scopes only—`i` / `j` / `k` in a short indexed loop, `e` in `except ... as e`, and `k` / `v` in `.items()` when the meaning is obvious from context.
- **Endpoints:** One **route handler function** per file (`list.py`, `create.py`, …). Handler stays thin: validate input, call service, map to output schema.
- **Routers:** Prefer **flat** inclusion in `main.py` under `api_v1` — avoid deep nesting of routers (reduces duplicate tags in OpenAPI). Use **`tags=[...]`** for how the API reads to clients (`auth`, `users`, `wedding-sites`, …), not for internal folder names.
- **IDs:** API-exposed aggregate roots **SHOULD** use **`UUID`** + `default_factory=uuid4`. Internal/reference tables **MAY** use `int` PKs; never `id: int | None = Field(default=None, primary_key=True)` — PKs are required in the type system.

---

## AVOID

- Domain logic or `session.exec(...)` inside **`api/`** route functions.
- **`print()`** for diagnostics.
- Keyword-only separator `*` in function/method signatures.
- Docstrings that only restate the function name. Args/Returns blocks when types already explain the contract.
- Comments that narrate **what** the next line does (obvious from code).
- URL paths that mirror **only** internal folder names without reflecting a resource (e.g. stutter segments like `/items/items`).

---

## API checklist (new or changed routes)

- [ ] Pydantic **input** and **output** types (no raw ORM on the wire).
- [ ] Handler uses **`Depends(get_<domain>_service)`** (or appropriate deps).
- [ ] **`responses=`** documents non-2xx errors the client can see.
- [ ] Router **`prefix`**/`tags` keep OpenAPI clear; mount on **`api_v1`** in `main.py` if the URL must be under **`/api/v1`**.

---

## Primary keys (quick reference)

| Exposure | PK type | Pattern |
|----------|---------|---------|
| Returned to clients as entity id | `UUID` | `id: UUID = Field(primary_key=True, default_factory=uuid4)` |
| Internal / not an API id | `int` | `id: int = Field(primary_key=True)` (DB autoincrement) |

FKs to UUID entities use **`UUID`**.

---

## If you are unsure

- Copy the **shape** of **`users`** (auth + `users_router`) or **`wedding_sites`** (domain-only until HTTP is added).
- Prefer **adding** `schemas.py` DTOs over widening ORM models for API contracts.
