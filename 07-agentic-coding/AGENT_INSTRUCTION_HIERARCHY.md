# Agent Instruction File Hierarchy

**Purpose:** A scalable convention for the instruction files that AI coding agents load
(`CLAUDE.md`, `AGENTS.md`) — one source of truth per area, inherited from root, and readable
by every major agent tool.

**Scope:** Any repository worked on by Claude Code, Codex, Gemini, or similar agents.

---

## The Problem

A single monolithic `CLAUDE.md` (often 500–900 lines) becomes unmaintainable: it mixes
universal rules with area-specific detail, it's loaded in full on every session (burning
context), and it's tool-specific (Codex/Gemini look for `AGENTS.md`, not `CLAUDE.md`).

## The Pattern: `CLAUDE.md → @AGENTS.md`, inherited per area

```
/CLAUDE.md            → one line:  @AGENTS.md          (pointer; keeps Claude Code happy)
/AGENTS.md            → root master instructions (universal rules)        ← the real file
/src/services/CLAUDE.md   → @AGENTS.md
/src/services/AGENTS.md   → area-specific rules; root auto-loads via the CLAUDE.md chain
/src/components/CLAUDE.md  → @AGENTS.md
/src/components/AGENTS.md  → area-specific rules
```

Three rules make it work:

1. **`AGENTS.md` is the real instruction file.** `AGENTS.md` is the emerging cross-tool standard
   (Claude Code, Codex, Gemini, Cursor all read it). Put your content there.
2. **`CLAUDE.md` is a one-line pointer:** its entire contents are `@AGENTS.md`. The `@` import
   syntax tells Claude Code to load the sibling `AGENTS.md`. This avoids duplicating content in
   two files while keeping both tools satisfied.
3. **Nest per area, inherit from root.** Each meaningful directory (a service layer, a component
   library, an infra package) gets its own `AGENTS.md` + one-line `CLAUDE.md`. The root file holds
   rules that apply *everywhere*; area files hold only what's specific to that area. When an agent
   enters an area, it loads the local file; the parent chain loads via the `CLAUDE.md` hierarchy.

### Why a pointer instead of a symlink?

A real one-line file (`@AGENTS.md`) is portable across OSes and survives `git` on Windows; a
symlink can break. The `@` import is also explicit and greppable.

## Root `AGENTS.md` — recommended outline

Use `AGENTS.template.md` (in this directory) as the starting point. Sections:

- **Scope** — one paragraph: what this codebase is, and that area files hold local rules.
- **On Startup** — what to load and when (this file always; local `AGENTS.md` on entering an area;
  skills only when the task matches; never bulk-load docs).
- **Boundaries** — `Always Do` / `Ask First` / `Never Do`. The single most valuable section.
- **Chosen Tools** — the project's library/framework registry, so agents don't introduce
  duplicate dependencies. Pairs with a DRY/duplication check before proposing anything new.
- **Task Management & Parallel Execution** — when to use the task list and subagents.
- **Git Workflow** — branch model, what needs human approval, worktree usage.
- **Permission Profiles** — which role profiles exist and what each restricts (see
  `agentic-tooling/settings/`).
- **Testing Protocol** — what to run before handing back to a human.
- **Documentation Areas** — a map of which directories have their own `AGENTS.md`.
- **Skills Index** — table of available skills and when to use each.
- **Communication / Meta** — tone, and a generated-on/by footer.

## Area `AGENTS.md` — keep it thin

An area file should answer: *"What do I need to know to safely change code in THIS directory that
isn't already in the root file?"* Typically: the local architecture pattern, the canonical
helper to reuse, and the local "never do" items. If an area file starts repeating the root, delete
the repetition.

## On Startup discipline (context hygiene)

State this explicitly in the root file so agents don't over-load context:

- Load the root `AGENTS.md` (via `CLAUDE.md`) — always.
- Load a local `AGENTS.md` only when entering that area.
- Load a skill only when the task matches its description.
- Load long-form docs/README only when architecture detail is actually needed.
- Never bulk-load documentation "just in case."

## Migrating from a monolithic `CLAUDE.md`

1. Rename the substantive content target to `AGENTS.md`; replace `CLAUDE.md` with `@AGENTS.md`.
2. Move generic standards (naming, function design, testing prose) **out** — reference this guide
   instead of restating it (via the `mango-tools` MCP server or `node_modules/@matthewkerns/...`).
3. Pull area-specific detail into nested `AGENTS.md` files; leave only universal rules at root.
4. Add the `On Startup` discipline so the now-smaller files stay small.

## Cross-tool benefit

Because the real file is `AGENTS.md`, the same instructions serve Claude Code (via the `CLAUDE.md`
pointer), Codex, and Gemini (point `.gemini/settings.json` at `AGENTS.md`). One source, every agent.

---

**Related:** `AGENTS.template.md` (ready-to-fill template), `agentic-tooling/settings/` (permission
profiles referenced by the Permission Profiles section), `08-project-management/` (planning docs).
