---
applyTo: "tests/**/*.py"
---

## Context (read first)

- **Runner:** `pytest` with **`asyncio_mode = strict`** (`pyproject.toml`). Async tests need **`@pytest.mark.asyncio`**. Async fixtures use **`@pytest_asyncio.fixture`**.
- **DB:** Integration tests use PostgreSQL. Session-scoped setup creates database **`app_db_test`**; **`client`** overrides **`get_session`** so the app and test share the test session. **Do not** assume SQLite.
- **Layout:** Mirror `src/` under `tests/` — `tests/api/` = HTTP, `tests/domains/` = services/repositories, `tests/fixtures/` = shared pytest fixtures, root **`conftest.py`** re-exports fixtures.

---

## MUST

- **Mirror paths:** Code under `src/domains/foo/service.py` → tests under `tests/domains/foo/test_service.py` (or split layout below). Code under `src/api/foo/` → `tests/api/foo/`.
- **Naming:** `test__<unit_under_test>__<scenario>` where **scenario** is a **condition** (input/state), **not** the expected error message or status text.
  - Good: `test__register__empty_password`, `test__get_user__without_token`
  - Bad: `test__register__returns_422` (outcome in name), `test__login__fails` (vague)
- **AAA structure:** Each test body uses three comment lines exactly (so reviewers and agents scan quickly):

```python
# Arrange
# Act
# Assert
```

Place real code under each; leave no step empty without reason.

- **No duplicate layers:** Behavior deeply tested in **`tests/domains/`** (rules, normalization, hashing, branches) **must not** be re-tested exhaustively in **`tests/api/`**. API tests prove **HTTP contract**: status codes, JSON shape, headers, validation surface.

---

## SHOULD

- **Fixtures:** Build data via **`tests/fixtures/`** and factories (`wedding_site_factory`, register + login for tokens) instead of inlining large setup in every test.
- **API tests** (`tests/api/`): status codes, response keys (including **absent** secrets: `password`, `password_hash`), **`{"detail": ...}`** error shape where applicable, one happy path per feature unless regressions need more.
- **Service tests** (`tests/domains/`): business rules, exception types (`pytest.raises`), edge cases, and combinations API tests skip.

---

## Splitting large test files (~200+ lines)

1. Replace `tests/.../test_foo.py` with directory **`tests/.../foo/`** (drop `test_` prefix and `.py`).
2. Add focused files: `test_create.py`, `test_list.py`, etc., still under the same mirrored path.

Example:

- Before: `tests/domains/orders/test_service.py`
- After: `tests/domains/orders/service/test_create.py`, `test_refund.py`, …

---

## AVOID

- Redundant comments (“test that login works”).
- **Business-logic assertions** duplicated across API and domain suites for the same rule.
- **`print()`** in tests — use assertions or logging if debugging, remove before finish.

---

## Quick decision: where should this test live?

| Question | If yes → |
|----------|----------|
| Does it need **HTTPX + ASGI** / full route stack? | `tests/api/` |
| Does it only need **service/repository** + DB session? | `tests/domains/` |
| Is it only testing **Pydantic** or pure functions? | Same package mirror under `tests/domains/` or `tests/utils/` |

---

## If you are unsure

- Open an existing test in the same layer (`tests/api/users/` or `tests/domains/wedding_sites/`) and **match its patterns** (fixtures, client usage, assertions).
