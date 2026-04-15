# Wedding RSVP backend — implementation plan

This document phases product work for **wedding-rsvp-be**. It complements the existing scaffold (JWT auth, `wedding_sites` domain, Alembic, tests).

## Implementation status

Use this table to track what is actually built vs still planned. Update the **Status** and **Notes** columns when you finish a milestone (e.g. after a PR merge).

**Status values:** `Not started` · `In progress` · `Done` · `Blocked` (explain in Notes)

| Phase | Scope | Status | Notes |
|-------|--------|--------|-------|
| **0** | Product decisions | `Done` | Captured above; change Status if you revisit a decision. |
| **1** | `wedding_sites` table + `domains/wedding_sites` | `Done` | Alembic rev `4d9a2ee8107b` (`20260325_1200_*`); domain + service tests. |
| **2** | Auth verification for FE + wedding sites HTTP API | `Done` | 2.1: README “Frontend integration” + login `token_type`; auth verified against existing tests. 2.2: `/api/v1/wedding-sites` CRUD (`tests/api/wedding_sites/`). |
| **3** | AI agent (owner + public trial, 3-turn cap) | `Done` | Alembic `b8e4c91a2f70`; `anonymous_agent_sessions` + `StubAgentBackend`; `POST /public/agent/sessions|turn`, `POST /wedding-sites/{id}/agent/turn`; env: `ANONYMOUS_AGENT_*`, `RATE_LIMIT_PUBLIC_AGENT_*`. |
| **4** | Guests, RSVPs, public invite page | `Not started` | |

*Bump the **Last updated** line whenever you change a status.*

**Last updated:** 2026-03-29

---

## Phase 0 — Decisions (agreed)

- **Sites per user:** Multiple wedding sites per account (dashboard lists many sites).
- **Public identity:** Each site has a unique **`slug`** (globally unique in the system) for future public URLs.
- **Config storage:** Builder / page content is stored as **JSON** (`config`) on the site row, with an optional **`schema_version`** integer for forward-compatible frontend schema changes. The backend treats `config` as an opaque structured blob (validate JSON shape at the HTTP boundary as “object” only unless you add stricter schemas later).
- **Public RSVP / guests:** Deferred until after Phase 2 (see **Phase 4** placeholder below).
- **Anonymous AI trial:** Users **without accounts** may use the agent for up to **3 interactions** (aligned with the current frontend cap). This requires **public** agent endpoints and **server-side** enforcement of the limit (not only UI). Detailed shape lives under **Phase 3**.

---

## Phase 1 — Database tables and first domains (no new public routes yet)

**Goal:** Add persistence for wedding sites and introduce a **`wedding_sites`** domain with the same layering as **`users`** (repository, service, dependencies). No AI; no requirement for new HTTP endpoints in this phase beyond what you need to ship migrations and domain tests—**Phase 2** exposes the API.

### 1.1 Tables

#### `users` (existing)

Already in production schema; Phase 1 does not change it.

| Column          | Type   | Notes                          |
|-----------------|--------|--------------------------------|
| `id`            | UUID   | PK                             |
| `email`         | string | unique, indexed                |
| `password_hash` | string | bcrypt                         |

#### `wedding_sites` (new)

One row per wedding website owned by a user.

| Column            | Type        | Notes |
|-------------------|-------------|--------|
| `id`              | UUID        | PK, `default_factory=uuid4` |
| `owner_user_id`   | UUID        | FK → `users.id`, indexed, `ON DELETE CASCADE` (recommended) |
| `slug`            | string      | unique, indexed (case-insensitive uniqueness policy TBD at implementation—e.g. store normalized lowercase) |
| `title`           | string      | optional display name for dashboard |
| `status`          | string/enum | e.g. `draft` \| `published` (SQLModel/PG enum or string with CHECK—match project convention) |
| `config`          | JSON/JSONB  | site builder state (themes, blocks, copy); **not** exposed as ORM in API responses as raw table row—use DTOs in Phase 2 |
| `schema_version`  | int         | optional; default `1` for current frontend contract |
| `created_at`      | timestamptz | server default / `utc_now` pattern used elsewhere |
| `updated_at`      | timestamptz | updated on write |

**Indexes / constraints**

- Unique on `slug`.
- Index on `(owner_user_id)` for “list my sites”.

**Alembic**

- New revision creating `wedding_sites`.
- Import the SQLModel class in `src/db/migrations/env.py` so future autogenerate sees it.

### 1.2 Domain: `wedding_sites`

**Location:** `src/domains/wedding_sites/` (folder name plural, per `.github/instructions/src.instructions.md`).

| Module            | Responsibility |
|-------------------|----------------|
| `models.py`       | SQLModel table `WeddingSite`; optional small enums (e.g. `SiteStatus`) in `enums.py` if you prefer not to inline strings. |
| `repository.py`   | `WeddingSitesRepository`: async CRUD scoped by `owner_user_id` where applicable (`get_by_id_for_user`, `list_for_user`, `create`, `update`, `delete` as needed). **All** SQL/`session.exec` for this aggregate lives here. |
| `service.py`      | `WeddingSitesService`: business rules (slug normalization/validation, ensure unique slug on create, forbid cross-user access by delegating to repository with `user_id`). No raw SQL. |
| `dependencies.py` | `get_wedding_sites_service` → yields service with `AsyncSession`. |
| `exceptions.py`   | Optional: e.g. `WeddingSiteNotFoundError`, `SlugConflictError` mapped to HTTP in Phase 2. |

**Phase 1 tests (recommended)**

- `tests/domains/wedding_sites/`: service/repository tests with DB (patterns like `tests/domains/users/`).
- No requirement for API tests until Phase 2 if routes do not exist yet.

---

## Phase 2 — Basic HTTP: auth compatibility + wedding site endpoints

**Goal:** Let the **Next.js** app become functional against this API: same **register / login / refresh / current user** contract as today, plus **list and manage** wedding sites (metadata + `config`) for the authenticated owner.

### 2.1 Auth (existing) — verify and document for the frontend

Keep the existing behavior and paths (already under `/api/v1`); confirm in CI and document for the FE:

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/v1/auth/register` | Body: email, password (min length per existing validation). Returns `access_token`, `refresh_token`, `expires_in`, `refresh_expires_in`, and `user`. |
| `POST` | `/api/v1/auth/login` | Returns `access_token`, `refresh_token`, `expires_in`, `refresh_expires_in`, `user`. |
| `POST` | `/api/v1/auth/refresh` | Body: `refresh_token`; returns new token pair. |
| `GET`  | `/api/v1/user` | `Authorization: Bearer <access_token>`; current user profile. |

**Frontend notes**

- Use **`Authorization: Bearer`** (not cookies) unless you later add cookie-based sessions.
- Set **`CORS_ORIGINS`** in `.env` to the Next.js dev/prod origin(s); see `README.md` if `CORS_CREDENTIALS` is true.
- Rate limits already apply to auth routes; FE should handle `429` + `ErrorResponse` shape `{ "detail": "..." }`.

No semantic change required in Phase 2 unless you discover a bug; treat this step as **verification + integration contract**.

### 2.2 Wedding sites API (new)

All routes: **Bearer required**, `tags` e.g. `wedding-sites`, thin handlers → `WeddingSitesService`, Pydantic DTOs in `api/wedding_sites/schemas.py` (**no** ORM in `response_model`).

| Method | Path | Summary |
|--------|------|---------|
| `GET`    | `/api/v1/wedding-sites` | List all sites where `owner_user_id == current_user.id`. |
| `POST`   | `/api/v1/wedding-sites` | Create site (body: `slug`, optional `title`, optional initial `config` / `status`). Enforce slug uniqueness. |
| `GET`    | `/api/v1/wedding-sites/{site_id}` | Get one site if owned by current user (include `config` for builder load). |
| `PATCH`  | `/api/v1/wedding-sites/{site_id}` | Partial update: `title`, `slug` (if allowed), `status`, `config`, `schema_version` as needed. Used for **manual / builder saves** until Phase 3. |
| `DELETE` | `/api/v1/wedding-sites/{site_id}` | Optional; delete if owned. |

**Errors**

- `404` for wrong id or not owner; `409` or `422` for slug conflict—pick one policy and document in OpenAPI via `get_error_response`.

**Tests**

- `tests/api/wedding_sites/`: list, create, get, patch with auth fixtures (`tests/fixtures/users.py`).

**Router registration**

- Include the new router on `api_v1` in `src/main.py`.

---

## Phase 3 — AI agent (authenticated + public trial)

**Goal:** Add the conversational agent routes: **logged-in** users go through the **owner** path (see below); **anonymous** users use **public** routes with a **hard cap of 3 agent interactions** per anonymous session. Keep **`PATCH /wedding-sites/{id}`** as a fallback for manual saves or migration tooling if you still want it.

### 3.1 Why add public endpoints

- Matches **try-before-signup**: the marketing/builder funnel can call the API **without** `register`/`login`.
- **Must enforce limits on the server**: the frontend can show “3 free tries,” but only the backend can prevent bypass (curl, cleared storage, etc.).

### 3.2 Anonymous session model (recommended)

Track trials with a **dedicated persistence row** (or equivalent), not “IP only” (NAT, mobile) and not “trust the client counter.”

| Approach | Outline |
|----------|--------|
| **Opaque session id** | On first use, create `anonymous_agent_sessions` (or similarly named) row: `id`, `interaction_count` (0), `config` (JSON, optional), `expires_at`, `created_at`. Return a **opaque token** to the client (random string or signed id) on **create**; client sends it on each turn via a **dedicated header** (e.g. `X-Anonymous-Session`) or **body field**—not as a Bearer user JWT. |
| **Server-side count** | Each successful **agent turn** increments `interaction_count`. When `interaction_count >= 3`, reject further turns with **`403`** or **`402`** + clear `detail` (e.g. “Trial limit reached; register to continue”). |
| **Config ownership** | Store `config` **on the session row** for anonymous users so turns stay stateful without a `User` or `WeddingSite`. After registration, FE/backend may **import** that config into a real `WeddingSite` (separate small flow in Phase 2/3—document when you implement). |

**Optional table (illustrative): `anonymous_agent_sessions`**

| Column              | Type        | Notes |
|---------------------|-------------|--------|
| `id`                | UUID        | PK |
| `token_hash`        | string      | store **hash** of the opaque token, not plaintext |
| `interaction_count` | int         | increment per completed agent turn |
| `config`            | JSON/JSONB  | draft builder state for this trial |
| `created_at` / `updated_at` | timestamptz | |
| `expires_at`        | timestamptz | optional TTL (e.g. 7 days) for garbage collection |

**Abuse controls**

- **Rate limits** stricter than authenticated routes (per IP + per session token); reuse `slowapi` patterns.
- Consider **CAPTCHA** or provider bot filters later if costs spike.

### 3.3 HTTP surface (illustrative)

| Audience | Method | Path (example) | Notes |
|----------|--------|----------------|--------|
| Anonymous | `POST` | `/api/v1/public/agent/sessions` | Creates session; returns `{ session_token, interactions_remaining: 3, config? }` (exact DTOs TBD). |
| Anonymous | `POST` | `/api/v1/public/agent/turn` | Body: `session_token`, `message`, optional `config` echo; runs agent; persists `config`; increments count; returns assistant reply + `interactions_remaining`. **403** when limit exceeded. |
| Authenticated | `POST` | `/api/v1/wedding-sites/{site_id}/agent/turn` | Bearer required; loads/saves **`WeddingSite.config`**; no 3-turn cap (or a higher/plan-based cap later). |

**Security**

- Public routes **must not** leak other users’ data; never accept `site_id` for anonymous editing of owned sites without a secret (trial uses **session** + session `config` only, or ephemeral id).
- Document CORS: only your Next.js origins in production.

### 3.4 Phase 1 migration note

You can **defer** `anonymous_agent_sessions` migration until Phase 3, or add the table in a Phase 1 migration if you prefer all schema up front—either is fine as long as **Phase 3** owns the behavior.

---

## Phase 4 — Guest list, RSVPs, public site (placeholder)

- Models: `Guest`, `Rsvp` (or equivalent), public read by `slug`, public `POST` RSVP with rate limits, owner responses dashboard endpoints.
- Flesh out when Phase 2 is stable.

---

## References

- Layering and API checklist: `.github/instructions/src.instructions.md`
- Existing patterns: `src/domains/wedding_sites/`, `src/domains/users/`, `src/api/users/`
- Builder assistant milestones (prompt, guards, tools): [`docs/AGENT_PLAN.md`](AGENT_PLAN.md)
