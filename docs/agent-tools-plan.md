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

## Tool tiers (proposed)

### Tier 1 — Universal (any template layout)

| Concept | Purpose |
| ------- | ------- |
| `set_block_visible` | `block_id` + `visible` |
| `remove_blocks` / restore | Integrate with existing **removed-blocks** semantics (or hide-only policy, per product) |
| `reorder_blocks` | Ordered list of `block_id` values (updates `order`) |
| `apply_theme` | **`theme_id` only**, from the curated theme registry (see Theme note below) |

### Tier 2 — Hero (`hero-1`)

| Concept | Purpose |
| ------- | ------- |
| `set_couple_names` | `partner_one`, `partner_two` (highest-frequency edit) |
| `set_hero_details` | Optional fields: date, tagline, cover/couple image URLs, `show_countdown` (single tool with optional fields **or** split if schemas should stay tiny) |

### Tier 3 — Section titles and wedding party (`wedding-party-1`)

| Concept | Purpose |
| ------- | ------- |
| `set_section_title` | `(block_id, title)` — reusable for party, gallery, RSVP, etc. |
| `upsert_wedding_party_member` / `remove_wedding_party_member` | **Or** defer list CRUD and use escape hatch **replace `members` array** until volume justifies it |

### Tier 4 — Gallery (`gallery-1`)

| Concept | Purpose |
| ------- | ------- |
| `set_gallery_layout` | `grid` \| `masonry` \| `carousel` |
| Photo list | Prefer **replace full `photos` list** or **add/remove by id** — avoid positional merge from the model |

### Tier 5 — Venue (`venue-1`)

| Concept | Purpose |
| ------- | ------- |
| `set_venue_ceremony` / `set_venue_reception` | Structured subfields (name, address, time, map URL, description, image) |
| `set_venue_same_location` | Boolean gate for reception visibility |

### Tier 6 — RSVP (`rsvp-1`)

| Concept | Purpose |
| ------- | ------- |
| `set_rsvp_copy` | Title, description, optional deadline |
| `set_rsvp_field_flags` | Meal/dietary/plus-one/song toggles and optional meal options |
| `set_rsvp_custom_questions` | Prefer **replace full list** for stable arrays |

---

## Minimal MVP tool set (smallest useful surface)

If implementing incrementally, this set matches common natural-language requests without exploding the tool surface:

1. `set_couple_names`
2. `set_block_visible` + block removal/restore (as one or two tools)
3. `set_section_title`
4. `set_hero_details`
5. Venue ceremony/reception + `same_location` (one or two tools)
6. `set_rsvp_copy` + `set_rsvp_field_flags`
7. `apply_theme` (registry-only)
8. **Escape hatch:** e.g. `apply_config_patch` or “replace `data` for `block_id`” for gallery photos, party members, and custom questions until dedicated list tools exist

---

## Implementation notes (backend)

- **Identify blocks by `block_id` when possible.** Fallback to **unique `type`** only when a single instance exists (true for the default template).
- **Nested arrays:** prefer **replace** or **id-keyed add/remove**; avoid ambiguous merges.
- **Theme:** first version should accept only **known theme ids** so invalid theme objects cannot be saved. **Open-ended / creative theme editing** (custom colors, fonts, decorations) is intentionally **out of scope for this plan** and deferred until product and validation strategy are defined.

---

## Relation to existing code

- Merge and normalization (`config_merge.py`, `config_normalize.py`) remain the **safety net** around partial or noisy model output; tools **apply on top of** merged config as deterministic steps.
- System prompt and observability under `src/domains/agent/` should be updated when tools ship (when to call which tool; when to use the escape hatch).

For phased product steps and checklist, see **`docs/AGENT_PLAN.md`**.
