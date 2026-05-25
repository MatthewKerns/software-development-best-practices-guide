# Security Hook Tests

Unit tests for `../hooks/security-check.sh` verifying its regex patterns work as
intended. The hook is a defense-in-depth layer that runs on every Bash / Read /
Write / Edit tool call, regardless of `settings.json` permissions.

## Running

```bash
# From the guide root (agentic-tooling/ lives at the repo root):
python3 -m pytest agentic-tooling/tests/ -q        # if python3 has pytest
pytest agentic-tooling/tests/ -q                   # or the pytest binary

# A single category
pytest agentic-tooling/tests/test_hard_block_patterns.py -v

# Faster dev loop (subset)
pytest agentic-tooling/tests/ -k "hard_block" --tb=short
```

Requires `pytest` and a `bash` + `jq` on PATH. ~35s for the full suite (each
hook invocation spawns jq + grep subprocesses). `pytest -n auto` parallelizes if
`pytest-xdist` is installed.

## Test Modules

| File | What it tests |
|------|---------------|
| `test_hard_block_patterns.py`  | Universal hard blocks (exit 2): rm -rf /, sudo, mkfs, dd of=/dev/, > /dev/sd*, git rebase, DROP DATABASE, redis FLUSH*, repo-aware rm |
| `test_force_ask_patterns.py`   | Universal force-asks (exit 0 + JSON): git push --force, reset --hard, clean -f, branch -D; plus default-allowed git push / merge / gh |
| `test_chaining_patterns.py`    | Chaining (`&&`, `\|\|`, `;`) and injection handling; eval/dot-source blocks; disabled pipe-to-interpreter checks |
| `test_sensitive_files.py`      | Blocked file access (.env, .aws/, .ssh/, .kube/, *.pem/*.key, credentials) and the .env.example whitelist |
| `test_allowed_commands.py`     | Safe commands pass through, including cloud read-only ops and (by default) the OPTIONAL cloud destructive ops |
| `test_edge_cases.py`           | Case sensitivity, whitespace, word boundaries, quote-bypass normalization, tool-name handling |
| `test_optional_cloud_rules.py` | The OPTIONAL cloud/infra guardrails — runs against a temp copy of the hook with the OPTIONAL block uncommented (AWS/CDK/Terraform/Pulumi/kubectl/DB-migrations/publishing) and with PROTECTED_BRANCHES enabled |
| `test_settings_schema.py`      | `../hooks/settings.example.json` wiring + hook files exist and are executable + the hook keeps its universal blocks and an OPTIONAL block that stays commented by default |

## Fixtures (`conftest.py`)

- `run_security_hook(tool, command=, file_path=)` — invoke the hook, get `(returncode, stdout, stderr)`
- `assert_blocked(...)` — exit 2 + "BLOCKED" in stderr
- `assert_allowed(...)` — exit 0, no permission JSON
- `assert_force_ask(...)` — exit 0 + `permissionDecision":"ask"` JSON

The hook path is resolved relative to the test file (`../hooks/security-check.sh`),
so the suite is location-independent.

## How the OPTIONAL-rules tests work

`security-check.sh` keeps cloud/infra guardrails commented out by default to stay
portable. `test_optional_cloud_rules.py` does NOT mutate the real hook — its
`patched_hook` fixture writes a temp copy with the `# FORCE_ASK_PATTERNS+=(...)`
lines uncommented (and `PROTECTED_BRANCHES` populated for the branch tests), then
runs against that copy. This proves the optional rules work when enabled while
the shipped hook stays default-off.

## When you change the hook

1. Add/adjust test case(s) in the matching module.
2. If you add an OPTIONAL rule, cover it in `test_optional_cloud_rules.py`.
3. Run the full suite.
4. Keep `security-check.sh` executable (`chmod +x`) — `test_settings_schema.py`
   asserts this, since a non-executable hook silently fails.
