---
applyTo:
  - "README.md"
  - "docs/**/*.md"
---

## Context

These files are **human-oriented**: onboarding, product context, and endpoint summaries. They complement **`.env.example`**, source, and OpenAPI for operational and implementation detail.

---

## MUST

- **Stay high level** in introductory or overview sections: product purpose, main stack, and what the system does—not exhaustive env var names, default model ids, test-only flags, or step-by-step provider setup unless the doc is explicitly a setup/deployment guide.
- **Put operational detail in the right place:** new config keys, rate-limit strings, and secret names belong in **`.env.example`**, short comments in **`config.py`**, or focused runbooks—not repeated in every README paragraph or plan section.
- **API bullets** in README may name paths, status codes, and **request/response shape** (what integrators need). Defer **backend wiring** (which LLM, `AGENT_BACKEND` values, pytest overrides) to `.env.example` or code unless debugging a specific integration issue.

---

## SHOULD

- Prefer **one pointer** (“see `.env.example`”, “see `/docs`”) over duplicating tables of settings.
- Keep **planning docs** (`docs/`) aligned with reality when you change behavior, without turning them into copies of `README` or `.env.example`.

---

## AVOID

- Dumping **low-level or duplicate** config lists into README or general docs whenever a feature is added.
- **Vendor-specific** marketing or tutorial prose unless the repo already uses that style for a dedicated doc.
