# Claude Code Settings Templates

Portable `settings.json` templates for any project's `.claude/` directory. They wire the
guide's hooks (`agentic-tooling/hooks/`) and establish a **base + role-profile** model so
permission rules aren't duplicated per developer.

## Files

| File | Purpose |
|------|---------|
| `settings.base.json` | Immutable base: common allow/deny permissions, hook wiring (`check-profile`, `security-check`, `statusline`), `statusLine`, and universal `env`. Copy to `<project>/.claude/settings.json`. |
| `settings.profile.template.json` | Role profile skeleton. Copy to `<project>/.claude/settings/settings.<role>.json` and fill in deny/ask gates. A permissive role leaves the arrays empty and relies on the base deny list + security hook. |

## The base + profile model

1. **Base (`settings.json`)** holds everything shared: the hook wiring, universal hard-deny
   patterns (`rm -rf /`, `git push --force`, …), and `env`. It does **not** change per person.
2. **Profiles (`settings/settings.<role>.json`)** layer role-specific `deny`/`ask` gates on top.
   - *Permissive* role → empty `deny`/`ask`/`allow`; the base deny list and `security-check.sh`
     are the safety net.
   - *Restricted* role → enumerate denied tools/paths (infra, CI/CD, auth core) and `ask` gates
     (pushes, installs, migrations).
3. A selector (a `make settings` target, or `check-profile.sh`) copies the chosen profile over
   `settings.local.json` so Claude Code merges it on top of the base.

## Install

```bash
# From a consuming project, after installing the guide and syncing hooks:
bpg-sync --project . --only hooks          # puts hooks in .claude/hooks/
cp node_modules/@matthewkerns/software-development-best-practices-guide/agentic-tooling/settings/settings.base.json .claude/settings.json
# then create .claude/settings/settings.<role>.json from the template
```

## Customizing

- **Cloud/infra projects:** merge the `_optional_cloud_denies` block from `settings.base.json`
  into the real `deny[]` array.
- **Hook paths** assume `"$CLAUDE_PROJECT_DIR"/.claude/hooks/`. Keep that layout or adjust.
- Drop `check-profile.sh` from `SessionStart` if you don't use the profile selector.

See `../hooks/README.md` for what each hook does and which sections are project-specific.
