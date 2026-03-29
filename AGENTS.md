# Guidance for AI coding agents

Before making non-trivial changes in this repository, **read every `*.instructions.md` file** in **[`.github/instructions/`](.github/instructions/)** whose scope matches the paths you are editing.

**Cursor:** the file **`.cursor/rules/agents.mdc`** is set to **`alwaysApply: true`** so this guidance is reinforced in-editor; it does not replace reading **`AGENTS.md`** and the instruction files when you need full detail.

Each file has YAML frontmatter with **`applyTo`** (glob patterns from the repository root). Use those patterns to decide which instruction files apply to your change. **Treat the body of every applicable file as binding guidance** for this repo—**for any AI assistant, agent, or automated coding tool**, not a single vendor.

## Human-oriented docs

- **[`README.md`](README.md)** — setup, Docker, Make, CI, endpoint overview.
- **Tone & scope:** when editing **`README.md`** or **`docs/**/*.md`**, follow **[`.github/instructions/documentation.instructions.md`](.github/instructions/documentation.instructions.md)** (high-level reader-facing docs; operational detail in `.env.example` / code).

If other repo-wide instruction files are added under **`.github/`** (for any product), **still honor** all matching **`.github/instructions/*.instructions.md`** rules for files that fall under their **`applyTo`** globs.
