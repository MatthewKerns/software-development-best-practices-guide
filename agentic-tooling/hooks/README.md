# Claude Code Hooks — Portable Edition

Three drop-in Claude Code hooks, genericized so any project can use them:

| Hook | Event | Purpose |
|------|-------|---------|
| `security-check.sh` | `PreToolUse` | Safety gate: hard-blocks catastrophic commands, force-asks risky ones, blocks sensitive-file access |
| `statusline.sh`     | `statusLine` | Renders a 4-line status line (worktree/branch/diff, context %, 5h/7d usage, cost, footprint) |
| `check-profile.sh`  | `SessionStart` | Injects the active permission-profile label as context Claude can see |

These were extracted from a private project's `.claude/` and stripped of
domain-specific logic. Cloud/infra rules are preserved but commented out and
easy to toggle on.

## Installation

1. Copy the scripts into your project at `.claude/hooks/`:
   ```bash
   mkdir -p .claude/hooks
   cp agentic-tooling/hooks/security-check.sh .claude/hooks/
   cp agentic-tooling/hooks/statusline.sh     .claude/hooks/
   cp agentic-tooling/hooks/check-profile.sh  .claude/hooks/
   chmod +x .claude/hooks/*.sh
   ```
   The executable bit is REQUIRED — Claude Code invokes hooks directly, and a
   non-executable hook silently fails (no protection).

2. Wire them in `.claude/settings.json`. A ready-to-copy template lives in
   `settings.example.json`; the relevant blocks:
   ```json
   {
     "hooks": {
       "SessionStart": [
         { "hooks": [
           { "type": "command",
             "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/check-profile.sh",
             "timeout": 5 } ] }
       ],
       "PreToolUse": [
         { "matcher": "Bash|Read|Write|Edit",
           "hooks": [
             { "type": "command",
               "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/security-check.sh",
               "timeout": 5 } ] }
       ]
     },
     "statusLine": {
       "type": "command",
       "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/statusline.sh",
       "padding": 0
     }
   }
   ```
   `$CLAUDE_PROJECT_DIR` is set by Claude Code to the project root. The
   `Bash|Read|Write|Edit` matcher is required — the security hook checks Bash
   commands and Read/Write/Edit file paths.

3. Requirements on PATH: `bash`, `jq`. The status line additionally uses (all
   optional, degrade gracefully): `curl`, `ccusage`, `gdate`, and on macOS the
   `security` Keychain tool.

## `security-check.sh`

Defense-in-depth gate evaluated in order for Bash commands:

1. **Hard block** (exit 2, no override) — universally catastrophic ops:
   `rm -rf /` and family, `rm` of `~`, `sudo`, `su`, `mkfs`, `dd of=/dev/*`,
   `> /dev/sd*`, `git rebase`, `eval`, dot-source (`. script.sh`), and
   case-insensitive `DROP DATABASE` / `redis-cli FLUSHALL|FLUSHDB`.
2. **Repo-aware `rm`** — `rm` targeting a path outside the git repo is blocked
   (exception: `/tmp`, `/private/tmp`, `/var/folders` scratch dirs).
3. **Branch-aware push** (optional) — see `PROTECTED_BRANCHES` below.
4. **Force ask** (exit 0 + JSON) — risky-but-recoverable git ops:
   `git push --force` / `--force-with-lease`, `git reset --hard`,
   `git clean -f`, `git branch -D`.

For Read / Write / Edit it blocks **sensitive files** (`.env`, `.envrc`,
`.aws/`, `.azure/`, `.gcloud/`, `.ssh/`, `*.pem`, `*.key`, `id_rsa`/`id_*`,
`.kube/`, `.npmrc`, `.pypirc`, `.netrc`, docker/gh config, `credentials`,
`secrets.*`, `passwords.*`, `tokens.*`). `.env.example` is whitelisted.

Commands are normalized (quotes stripped) before matching to prevent
quote-based bypass (`'git' 'rebase'` → `git rebase`).

**Exit-code contract (do not change):**
- `0` = allow, OR force-ask via stdout JSON:
  `{"hookSpecificOutput":{"permissionDecision":"ask","permissionDecisionReason":"..."}}`
- `2` = hard block; the stderr message is shown to Claude.

### Optional / project-specific sections

Everything below is off by default so the hook stays portable. To customize,
edit the clearly-marked spots near the top of the script:

- **`PROTECTED_BRANCHES=()`** (config array, top of file) — empty by default.
  Set to e.g. `("main" "staging")` to force-ask `git push` to those branches
  and hard-block direct `Write`/`Edit` on them. Worktree-aware (resolves the
  branch from the edited file's directory).

- **OPTIONAL: cloud / infra guardrails** (commented block near the top) —
  uncomment individual `# FORCE_ASK_PATTERNS+=('...')` lines to enable. These
  were the source project's domain-specific rules:
  - AWS destructive: `aws ... delete-`, `aws ... terminate-`, `aws s3 rm/rb`
  - IaC: `cdk destroy/deploy`, `terraform destroy/apply`, `pulumi destroy/up`,
    `kubectl delete namespace|--all`
  - CI triggers: `gh workflow run`, `gh run rerun`
  - DB migrations: `dropdb`, `alembic upgrade/downgrade/revision`
  - Publishing: `npm publish`, `pip upload`, `twine upload`, `docker push/login`

  To **hard-block** something instead of force-asking (e.g. `aws rds delete-*`
  for irrecoverable production data loss), add the pattern to
  `HARD_BLOCK_PATTERNS` — and place it *before* the broad `aws ... delete-`
  force-ask so it short-circuits first.

- **OPTIONAL: project-specific hard blocks** (inside `HARD_BLOCK_PATTERNS`) —
  e.g. a `deploy-staging` / `deploy-prod` script that only humans should run.

- **`INJECTION_PATTERNS`** — pipe-to-interpreter and command-substitution
  blocks, disabled by default (too restrictive for normal dev: Claude
  legitimately uses `echo ... | python3 -c` and `$(curl ... | jq ...)`).
  Uncomment for a stricter posture.

## `statusline.sh`

Renders four lines after every assistant message (keep it fast):

1. worktree marker + dir + branch + diff summary · model
2. context-window % (used/total) · session $
3. 5h-window progress bar/% · window $ · burn $/hr · carbon footprint
4. 7d-window progress bar/% · week $ · $/day avg · carbon footprint

Worktree detection uses Claude Code's native `.worktree.path` when present,
falling back to a process-tree walk. The 5h/7d utilization comes from
`/api/oauth/usage` (token read from the macOS Keychain or
`~/.claude/.credentials.json`), cached at `/tmp/cc-usage-cache-$UID.json`
(TTL 300s). Cost figures come from `ccusage` if installed.

**All external dependencies are optional and guarded** — without `ccusage`,
`curl`, a credential, or `gdate`, the affected fields render `?` or collapse;
the line never errors. Dollar figures are token-pricing equivalents; the 5h/7d
% are the authoritative plan-utilization numbers. AWS/project-specific env
display from the original has been removed; there's nothing project-specific to
configure.

## `check-profile.sh`

`SessionStart` hook. Reads `_profile_label` from `.claude/settings.local.json`
and emits it as context for Claude (SessionStart stdout on exit 0 is added as
context, not shown to the user). If no `settings.local.json` exists, it emits a
"no profile loaded" notice.

Configure the three CONFIG values at the top:
- `KNOWN_PROFILES=()` — optional expected labels; if set and the loaded label
  isn't among them, the notice flags it. Empty = accept any label.
- `SETUP_HINT` — the command/instructions shown when no profile is loaded.
- `SECURITY_SUMMARY` — one-line reminder of active guardrails; edit to match
  whatever your `security-check.sh` enforces.

This hook is purely advisory (it never blocks). Drop it if your project doesn't
use a permission-profile convention.

## Tests

See `../tests/` for the pytest suite covering the universal rules, sensitive
files, edge cases, and the OPTIONAL rules (exercised against a temp copy of the
hook with the optional block uncommented). Run from the guide root:

```bash
pytest agentic-tooling/tests/ -q
```
