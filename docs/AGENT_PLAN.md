# Agent implementation plan

This document tracks **product and engineering steps** for the wedding-site builder assistant. It complements `**docs/plan.md`** (phased product plan) and the code under `**src/domains/agent/**`.

**Current baseline:** each turn sends the user message plus current **`config`** to the LLM; the model returns a short reply and a **full updated `config`**, which the API persists (public trial session or owner site). Shared prompt and structured turn logic live in **`structured_agent_backend.py`** (`StructuredAgentBackend`); provider types and Gemini wiring live under **`providers/`** (`config.py`, `gemini.py`). The **`AgentBackend`** port is **`ports.py`**; the offline stub is **`stub_backend.py`**. Backend selection is configured at app startup.

---

## Guiding principles

- Ship **one narrow capability** at a time (e.g. a single section or field family), then widen.
- Treat `**config`** as a **contract with the frontend**: document the slice you automate before expanding the prompt.
- Prefer **prompt + validation** first; add **tools** when the model repeatedly corrupts unrelated JSON or you need deterministic edits.

---

## Task list (initial)

Use this as a working checklist; reorder or split as you learn.


| #   | Task                                    | Notes                                                                                                                                                                                                                |
| --- | --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **Choose the first user story**         | One concrete outcome (e.g. “update hero title/copy” or “set couple names”). Defines “done” for the first milestone.                                                                                                  |
| 2   | **Document the `config` slice**         | Short description of JSON paths/shapes the agent may read or write for that story (align with the Next.js builder). Avoid duplicating the whole schema here—link or reference the FE contract if it lives elsewhere. |
| 3   | **Draft and iterate the system prompt** | Extend instructions in the agent backend: role, safety rules, “preserve unrelated keys,” and 1–2 **few-shot** examples for the chosen slice. Keep examples maintainable (small JSON snippets).                       |
| 4   | **Tune model settings (if needed)**     | Temperature, max output, retries—balance creativity vs. stable JSON; adjust in code where model settings are set.                                                                                                    |
| 5   | **Add a server-side guard before save** | Merge strategy, size limits, or rejection rules so bad or partial model output cannot wipe unrelated `config`. Unit-test the guard with stub configs.                                                                |
| 6   | **Manual eval loop**                    | Fixed inputs (message + `config`) and expected behavior; run locally with the LLM backend enabled (see `**.env.example`**). Capture failures and feed back into prompt/guard.                                        |
| 7   | **Optional: introduce tools**           | If step 6 is unstable, add Pydantic AI tools for discrete operations (e.g. patch a known path) and narrow the model’s freedom.                                                                                       |
| 8   | **Automated tests**                     | Keep CI on **stub**; add tests for merge/guard logic; optional mocked LLM or marked integration tests for regressions.                                                                                               |
| 9   | **Observability**                       | Log failures (without secrets); consider latency/token metrics when you tune cost or SLAs.                                                                                                                           |
| 10  | **Update this doc**                     | When a milestone ships, mark tasks done and add the next slice (new rows or a “Phase 2” subsection).                                                                                                                 |


---

## After the first slice

- Repeat rows 2–8 for the **next** builder capability.
- Revisit **anonymous trial copy** (403 messaging) if the assistant’s capabilities change what “trial” means for users.
- If `**config`** gains a formal JSON Schema in the repo, reference it from here instead of duplicating field lists.

---

## References (code)

- **`src/domains/agent/ports.py`** — `AgentBackend` protocol.
- **`src/domains/agent/stub_backend.py`** — `StubAgentBackend` (no live LLM).
- **`src/domains/agent/structured_agent_backend.py`** — `StructuredAgentBackend`: loads default system prompt from **`prompts/wedding_builder_system.txt`**, structured turn output, run flow.
- **`src/domains/agent/providers/config.py`** — `ProviderLlmConfig`; subclass per vendor when needed.
- **`src/domains/agent/providers/gemini.py`** — `GeminiBackendConfig` + `structured_agent_backend_from_gemini`.
- `**src/domains/agent/service.py**` — turn orchestration and persistence.
- `**src/domains/agent/factory.py**` — backend selection from settings.
- `**docs/plan.md**` — Phase 3 HTTP surface and product context.
