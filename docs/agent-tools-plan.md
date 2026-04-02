# Wedding builder agent — tools plan

This document describes a **planned** move from “model returns the whole site `config` each turn” to a **hybrid**: **PydanticAI-style tools** for narrow, deterministic edits, plus an optional **escape hatch** (small patch or targeted replace) for creative or rare changes. It targets the **current default site template** used by the paired frontend.

**Contract note:** Block shapes and default IDs live in the frontend package (`createDefaultSiteConfig` and `lib/wedding-config/types.ts` in the wedding RSVP website repo). This doc stays behavioral, not a duplicate schema.

---

## Default template slice

The baseline builder site is built from five blocks (stable IDs in defaults):

| Order | Block id           | Type           |
| ----- | ------------------ | -------------- |
| 0     | `hero-1`           | `hero`         |
| 1     | `wedding-party-1`  | `wedding-party`|
| 2     | `gallery-1`        | `gallery`      |
| 3     | `venue-1`          | `venue`        |
| 4     | `rsvp-1`           | `rsvp`         |

Other block types (`couple-story`, `registry`, `faq`, …) exist in the type system but are **out of scope** for this first tools pass until they appear in the default flow or product prioritizes them.

---

## Why tools

- **Smaller model output** — fewer tokens and less risk of corrupting unrelated JSON.
- **Deterministic edits** — server applies known operations on merged config (aligned with existing merge/normalize guards).
- **Clear UX mapping** — user utterances map to named operations (“hide gallery”, “set names”, “update ceremony address”).

The model can still use **one** broader path when no tool fits (e.g. replace a block’s `data` or a documented patch shape).

---

## Tool groups (shipped vs planned)

### **Site surface** — shipped (`domains/agent/tools/`)

High-level tools over the whole site shape (order, global theme, full read). Registered via `register_site_surface_tools`.

| Concept | Purpose |
| ------- | ------- |
| `reorder_blocks` | Ordered list of `block_id` values (updates `order`) — `tools/site_surface.py` |
| `apply_theme` | **`theme_id` only**, from the curated theme registry — `tools/site_surface.py` |
| `get_full_site_config` | Read-only full JSON for nested `data` — `tools/site_surface.py` |

Deterministic merges live in `tools/mutations/site_surface.py`.

### **Hero** (`hero-1`) — planned

| Concept | Purpose |
| ------- | ------- |
| `set_couple_names` | `partner_one`, `partner_two` (highest-frequency edit) |
| `set_hero_details` | Optional fields: date, tagline, cover/couple image URLs, `show_countdown` (single tool with optional fields **or** split if schemas should stay tiny) |

### **Section titles & wedding party** (`wedding-party-1`; title tool reusable)

| Concept | Purpose |
| ------- | ------- |
| `set_section_title` | `(block_id, title)` — reusable for party, gallery, RSVP, etc. |
| `upsert_wedding_party_member` / `remove_wedding_party_member` | **Or** defer list CRUD and use escape hatch **replace `members` array** until volume justifies it |

### **Gallery** (`gallery-1`) — planned

| Concept | Purpose |
| ------- | ------- |
| `set_gallery_layout` | `grid` \| `masonry` \| `carousel` |
| Photo list | Prefer **replace full `photos` list** or **add/remove by id** — avoid positional merge from the model |

### **Venue** (`venue-1`) — planned

| Concept | Purpose |
| ------- | ------- |
| `set_venue_ceremony` / `set_venue_reception` | Structured subfields (name, address, time, map URL, description, image) |
| `set_venue_same_location` | Boolean gate for reception visibility |

### **RSVP** (`rsvp-1`) — planned

| Concept | Purpose |
| ------- | ------- |
| `set_rsvp_copy` | Title, description, optional deadline |
| `set_rsvp_field_flags` | Meal/dietary/plus-one/song toggles and optional meal options |
| `set_rsvp_custom_questions` | Prefer **replace full list** for stable arrays |

---

## Minimal MVP (suggested build order)

If implementing incrementally, this order matches common natural-language requests without exploding the tool surface:

1. `set_couple_names` (hero)
2. `set_section_title` (shared)
3. `set_hero_details` (hero)
4. Venue ceremony/reception + `same_location` (venue — one or two tools)
5. `set_rsvp_copy` + `set_rsvp_field_flags` (RSVP)
6. `apply_theme` (already shipped — site surface)
7. **Escape hatch:** e.g. `apply_config_patch` or “replace `data` for `block_id`” for gallery photos, party members, and custom questions until dedicated list tools exist

Hide/show sections: use structured `config` patches on each block’s `visible` field (no dedicated tool in the current backend).

---

## Implementation notes (backend)

- **Identify blocks by `block_id` when possible.** Fallback to **unique `type`** only when a single instance exists (true for the default template).
- **Nested arrays:** prefer **replace** or **id-keyed add/remove**; avoid ambiguous merges.
- **Theme:** first version should accept only **known theme ids** so invalid theme objects cannot be saved. **Open-ended / creative theme editing** (custom colors, fonts, decorations) is intentionally **out of scope for this plan** and deferred until product and validation strategy are defined.

---

## Relation to existing code

- **Site surface** tools live under **`src/domains/agent/tools/`** (`register_site_surface_tools` from `StructuredAgentBackend`).
- Merge and normalization (`config_processing/merge.py`, `config_processing/normalize.py`) remain the **safety net** around partial or noisy model output; tools **apply on top of** merged config as deterministic steps.
- System prompt and observability under `src/domains/agent/` should stay aligned with which tools exist and when to use the escape hatch (`config` patch).

For phased product steps and checklist, see **`docs/AGENT_PLAN.md`**.
