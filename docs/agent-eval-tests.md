# Agent eval test list

This document defines a practical evaluation set for the wedding builder agent, grouped by:

- **Functional tests**: content/structure requests are applied correctly in `config`.
- **Stylistic tests**: visual design requests are applied correctly (theme/colors/typography/style mood).

Use these as a repeatable manual or scripted checklist whenever prompt, tools, merge logic, or model settings change.

---

## Scope

The tests reflect the current backend behavior:

- Agent returns `assistant_message` and a config patch.
- Server merges patch into existing config.
- Site-surface tools can be used for operations like block reorder and theme apply.
- Section-level content updates can be done through config patching.

Note: some stylistic requests may depend on what style fields are currently supported by the frontend contract and backend validators. Keep cases aligned with supported fields.

---

## Functional eval tests

Each case should verify:

- `assistant_message` acknowledges the request.
- Only intended parts of `config` change.
- Unrelated sections remain unchanged.

### F01 - Change hero couple names

- **User input:** "Change the couple names to Maria and Nikos."
- **Expected config behavior:** names in hero block are updated.
- **Fail if:** names unchanged, wrong block changed, or unrelated fields are overwritten.

### F02 - Change hero date/tagline copy

- **User input:** "Set the wedding date to June 14, 2027 and make the tagline 'Celebrate with us in Athens'."
- **Expected config behavior:** hero date and tagline are updated.
- **Fail if:** partial update only, malformed date field, or unrelated hero media fields reset.

### F03 - Reorder sections

- **User input:** "Move RSVP before the gallery section."
- **Expected config behavior:** `order` is updated so `rsvp-1` appears before `gallery-1`.
- **Fail if:** duplicate/missing block IDs, no order change, or content mutation outside order.

### F04 - Update section title copy

- **User input:** "Rename 'Wedding Party' to 'Our Favorite People'."
- **Expected config behavior:** target section title changes.
- **Fail if:** title changed in wrong section or section data removed.

### F05 - Venue ceremony details

- **User input:** "Set ceremony to St. George Church, 5:30 PM, 12 Olive Street."
- **Expected config behavior:** ceremony name/time/address fields are updated.
- **Fail if:** reception fields are unexpectedly modified or venue structure is broken.

### F06 - RSVP copy and deadline

- **User input:** "Update RSVP text to 'Please reply by May 1' and set deadline to 2027-05-01."
- **Expected config behavior:** RSVP text and deadline update.
- **Fail if:** RSVP toggles/questions are wiped or deadline format is corrupted.

### F07 - Toggle RSVP options

- **User input:** "Enable plus-one and dietary restrictions."
- **Expected config behavior:** corresponding RSVP flags become true.
- **Fail if:** unrelated toggles flip, or meal options/questions get deleted.

### F08 - Multi-intent request

- **User input:** "Change couple names to Anna & Theo and move venue above gallery."
- **Expected config behavior:** both content and order updates are applied in one turn.
- **Fail if:** only one intent is applied or config is partially corrupted.

### F09 - No-op / clarify request

- **User input:** "Can you show me what sections I currently have?"
- **Expected config behavior:** no config mutation.
- **Fail if:** any persisted config change happens for a read-only question.

---

## Stylistic eval tests (site visual changes)

Each case should verify:

- requested visual styling change is applied in `config`
- non-style content (names, dates, venues, RSVP text) is not unintentionally changed
- unsupported styling requests are handled safely (clarify or decline without corrupting config)

### S01 - Apply theme

- **User input:** "Switch to a more elegant theme."
- **Expected config behavior:** theme changes to a valid supported theme id.
- **Fail if:** invalid theme payload is saved, no style change happens, or content fields mutate.

### S02 - Change background color

- **User input:** "Use a warm ivory background."
- **Expected config behavior:** background color/style token updates in the correct theme/style location.
- **Fail if:** color is applied to wrong key, invalid color value is saved, or non-style fields are altered.

### S03 - Change accent/primary color

- **User input:** "Make accents dusty rose."
- **Expected config behavior:** accent/primary color value updates.
- **Fail if:** multiple unrelated colors change unexpectedly or contrast-breaking invalid values are stored.

### S04 - Typography style change

- **User input:** "Use a more classic serif look for headings."
- **Expected config behavior:** heading font family/style token updates to a supported option.
- **Fail if:** unsupported font value is written directly or body/heading mapping becomes inconsistent.

### S05 - Section style variant

- **User input:** "Make the gallery feel more editorial and clean."
- **Expected config behavior:** relevant style/layout variant changes for gallery (if supported).
- **Fail if:** gallery content list is changed when only styling was requested.

### S06 - Decorative intensity adjustment

- **User input:** "Reduce decorative elements and keep it minimal."
- **Expected config behavior:** decoration-related style flags/tokens are reduced.
- **Fail if:** decorative changes remove required content blocks or break section rendering shape.

### S07 - Multi-style request in one turn

- **User input:** "Apply a romantic theme, soften background colors, and use elegant typography."
- **Expected config behavior:** all requested style dimensions update consistently in one response.
- **Fail if:** only partial style intent is applied without clarification, or config becomes internally inconsistent.

### S08 - Unsupported style request handling

- **User input:** "Apply a custom gradient animation background and parallax transitions everywhere."
- **Expected config behavior:** agent asks for clarification or explains limitation without unsafe config mutation.
- **Fail if:** agent writes unsupported/unknown keys that can break frontend rendering.

---

## Suggested scoring

Use a simple pass/fail sheet per test:

- **Functional pass**: intended config change applied, no unintended mutation.
- **Stylistic pass**: requested visual style change is correctly applied without side effects.

Optional aggregate metrics:

- Functional pass rate (%)
- Stylistic pass rate (%)
- Critical regressions count (data loss, malformed config, invalid order)

---

## Regression cadence

Run this suite when:

- system prompt changes
- tool surface changes
- merge/normalization logic changes
- model/provider/settings change

Keep this list updated as new editable sections or tools are introduced.
