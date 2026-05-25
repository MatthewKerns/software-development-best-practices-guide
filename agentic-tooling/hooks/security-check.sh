#!/bin/bash
# =============================================================================
# SECURITY ENFORCEMENT HOOK — Portable / generic edition
# =============================================================================
# PROVENANCE
#   Extracted and genericized from a private project's PreToolUse safety gate.
#   It is a defense-in-depth layer that runs on EVERY Bash / Read / Write / Edit
#   tool call, regardless of what `settings.json` permissions allow. Wire it up
#   as a Claude Code PreToolUse hook (see hooks/README.md for the snippet).
#
# WHAT IT DOES
#   Three layers, evaluated in order for Bash commands:
#     1. HARD BLOCK  (exit 2)  — universally catastrophic ops. No override.
#     2. REPO-AWARE rm         — rm outside the git repo is blocked (temp dirs OK).
#     3. FORCE ASK   (exit 0 + JSON) — risky-but-legitimate ops prompt the user.
#   For Read / Write / Edit:
#     - Sensitive files (.env, keys, ssh, cloud creds) are hard-blocked.
#     - Optional branch protection blocks edits on protected branches.
#
# CUSTOMIZING
#   - Universal hard-blocks and force-asks below are safe defaults for any repo.
#   - Cloud / infra / domain-specific rules (AWS, CDK, Terraform, Pulumi,
#     kubectl, DB migrations, package publishing, container registry, etc.) live
#     in the clearly-marked "OPTIONAL" block near the top, COMMENTED OUT by
#     default. Uncomment the lines you want to enable for your project.
#   - PROTECTED_BRANCHES (below) controls which branches block Write/Edit.
#     Empty by default — set it to e.g. ("main" "staging") to enable.
#
# EXIT CODES (Claude Code hook contract — do not change)
#   0 = Allow (continue) OR Force Ask (emit JSON to stdout, see below)
#   2 = Hard Block (stop tool execution, message shown to Claude via stderr)
#
# FORCE-ASK JSON CONTRACT (stdout, exit 0):
#   {"hookSpecificOutput":{"permissionDecision":"ask","permissionDecisionReason":"..."}}
# =============================================================================

HOOK_MODE="active"
HOOK_LABEL="Active (portable edition)"

set -euo pipefail

# -----------------------------------------------------------------------------
# CONFIG: protected branches for Write/Edit (project-specific — empty = disabled)
# -----------------------------------------------------------------------------
# Direct Write/Edit on these branches is hard-blocked, forcing a feature branch.
# Leave empty to disable branch protection entirely. Example: ("main" "staging")
PROTECTED_BRANCHES=()

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# =============================================================================
# COMMAND NORMALIZATION - Prevent quote-based bypass attacks
# =============================================================================
normalize_command() {
    echo "$1" | sed "s/['\"]//g"
}

# =============================================================================
# REPO-AWARE PATH CHECKING - Allow operations within repo, block outside
# =============================================================================
get_repo_root() {
    git rev-parse --show-toplevel 2>/dev/null || echo ""
}

is_path_in_repo() {
    local path="$1"
    local repo_root=$(get_repo_root)

    if [ -z "$repo_root" ]; then
        return 1
    fi

    if [[ "$path" == *".."* ]]; then
        return 1
    fi

    if [[ "$path" == "~"* ]]; then
        return 1
    fi

    local abs_path
    if [[ "$path" = /* ]]; then
        abs_path="$path"
    else
        abs_path="$(pwd)/$path"
    fi

    local normalized
    normalized=$(python3 -c "import os; print(os.path.normpath('$abs_path'))" 2>/dev/null || echo "")

    if [ -z "$normalized" ]; then
        return 1
    fi

    if [[ "$normalized" == "$repo_root"* ]]; then
        return 0
    else
        return 1
    fi
}

# =============================================================================
# HARD BLOCK PATTERNS - Universal. These are NEVER allowed via Claude.
# =============================================================================
# Catastrophic, irrecoverable local-machine damage and history rewrites.
# Keep this list lean and universal — project/cloud specifics go in the
# OPTIONAL block below, not here.
HARD_BLOCK_PATTERNS=(
    # System destructive operations — irrecoverable local-machine damage.
    '(\b|/)rm\s+(-[a-zA-Z]*r[a-zA-Z]*\s+)*-[a-zA-Z]*f[a-zA-Z]*\s+/$'
    '(\b|/)rm\s+(-[a-zA-Z]*r[a-zA-Z]*\s+)*-[a-zA-Z]*f[a-zA-Z]*\s+/\s'
    '(\b|/)rm\s+.*\s+~$'
    '(\b|/)rm\s+.*\s+~/'
    '(\b|/)rm\s+(-[a-zA-Z]*\s+)*~$'
    '(\b|/)rm\s+(-[a-zA-Z]*\s+)*~/'
    '(\b|/)rm\s+(-[a-zA-Z]*r[a-zA-Z]*\s+)*-[a-zA-Z]*f[a-zA-Z]*\s+/usr'
    '(\b|/)rm\s+(-[a-zA-Z]*r[a-zA-Z]*\s+)*-[a-zA-Z]*f[a-zA-Z]*\s+/etc'
    '(\b|/)rm\s+(-[a-zA-Z]*r[a-zA-Z]*\s+)*-[a-zA-Z]*f[a-zA-Z]*\s+/var'
    '(\b|/)rm\s+(-[a-zA-Z]*r[a-zA-Z]*\s+)*-[a-zA-Z]*f[a-zA-Z]*\s+/home'
    '(\b|/)rm\s+(-[a-zA-Z]*r[a-zA-Z]*\s+)*-[a-zA-Z]*f[a-zA-Z]*\s+/Users'
    '(\b|/)rm\s+(-[a-zA-Z]*r[a-zA-Z]*\s+)*-[a-zA-Z]*f[a-zA-Z]*\s+/System'
    '(\b|/)rm\s+(-[a-zA-Z]*r[a-zA-Z]*\s+)*-[a-zA-Z]*f[a-zA-Z]*\s+/Applications'
    '(\b|/)sudo\s+'
    '(\b|/)su\s+(-|root|--login|-l)'
    '(\b|/)mkfs(\s|\.)'
    '(\b|/)dd\s+.*of=/dev/'
    '(\b|/)[a-zA-Z]*\s*>\s*/dev/sd[a-z]'   # > /dev/sda — overwrite raw disk

    # Git — only rebase stays hard-blocked here (rewrites history with conflict
    # potential). Force-push / reset --hard / clean -f / branch -D are in the
    # FORCE_ASK list (recoverable via reflog when caught early).
    '(\b|/)git\s+rebase'

    # Shell code execution — prompt-injection vectors.
    '\beval\s+'
    '^\.\s+\S'

    # ----- OPTIONAL: project-specific hard blocks (uncomment to enable) -----
    # Direct deploy/release script that humans should always run, never Claude:
    # 'deploy-staging'
    # 'deploy-prod'
)

# Case-insensitive hard-block patterns (SQL / datastore destruction).
HARD_BLOCK_PATTERNS_NOCASE=(
    'DROP\s+DATABASE'
    '(\b|/)redis-cli\s+FLUSHALL'
    '(\b|/)redis-cli\s+FLUSHDB'
)

# =============================================================================
# FORCE ASK PATTERNS - Universal. Risky-but-legitimate ops prompt before run.
# =============================================================================
# Recoverable or reversible, but worth a visible confirm. Git destructive ops
# live here because they're recoverable via reflog when caught early.
FORCE_ASK_PATTERNS=(
    # Git destructive — recoverable via reflog, but confirm before action.
    '(\b|/)git\s+push\b.*\s(-f|--force)\b'
    '(\b|/)git\s+push\b.*--force-with-lease'
    '(\b|/)git\s+reset\s+--hard'
    '(\b|/)git\s+clean\s+-[a-zA-Z]*f'
    '(\b|/)git\s+branch\s+-D\b'
)

# =============================================================================
# OPTIONAL: cloud / infra guardrails (uncomment to enable)
# =============================================================================
# These rules are domain-specific (AWS, CDK, Terraform, Pulumi, Kubernetes,
# database migrations, package/registry publishing). They are DISABLED by
# default so the hook stays portable. To enable a guardrail, uncomment its
# line(s). Each appends to FORCE_ASK_PATTERNS unless noted otherwise.
#
# Tip: anything you want HARD-BLOCKED (no override) instead of force-asked —
# e.g. `aws rds delete-*` for irrecoverable production data loss — should be
# added to HARD_BLOCK_PATTERNS above, and listed BEFORE the broad AWS force-ask
# patterns here so it short-circuits first.
#
# --- AWS destructive (deletes / terminates / s3 removal) ---
# FORCE_ASK_PATTERNS+=('(\b|/)aws\s+[a-z0-9-]+\s+delete-')
# FORCE_ASK_PATTERNS+=('(\b|/)aws\s+[a-z0-9-]+\s+terminate-')
# FORCE_ASK_PATTERNS+=('(\b|/)aws\s+s3\s+rm\s+')
# FORCE_ASK_PATTERNS+=('(\b|/)aws\s+s3\s+rb\s+')
# To HARD-BLOCK RDS deletes (production data loss is unrecoverable) instead,
# add this to HARD_BLOCK_PATTERNS above — it must come before the broad
# `aws ... delete-` force-ask so it short-circuits first:
#   '(\b|/)aws\s+rds\s+delete-'
#
# --- Infrastructure-as-code destruction ---
# FORCE_ASK_PATTERNS+=('(\b|/)cdk\s+destroy')
# FORCE_ASK_PATTERNS+=('(\b|/)terraform\s+destroy')
# FORCE_ASK_PATTERNS+=('(\b|/)pulumi\s+destroy')
# FORCE_ASK_PATTERNS+=('(\b|/)kubectl\s+delete\s+(namespace|ns)\b')
# FORCE_ASK_PATTERNS+=('(\b|/)kubectl\s+delete\b.*(-A|--all)')
#
# --- Infrastructure deployment ---
# FORCE_ASK_PATTERNS+=('(\b|/)cdk\s+deploy')
# FORCE_ASK_PATTERNS+=('(\b|/)terraform\s+apply')
# FORCE_ASK_PATTERNS+=('(\b|/)pulumi\s+up')
#
# --- CI triggers (reversible, but worth a confirm) ---
# FORCE_ASK_PATTERNS+=('(\b|/)gh\s+workflow\s+run')
# FORCE_ASK_PATTERNS+=('(\b|/)gh\s+run\s+rerun')
#
# --- Database migrations / drop ---
# FORCE_ASK_PATTERNS+=('(\b|/)dropdb\s+')
# FORCE_ASK_PATTERNS+=('(\b|/)alembic\s+upgrade')
# FORCE_ASK_PATTERNS+=('(\b|/)alembic\s+downgrade')
# FORCE_ASK_PATTERNS+=('(\b|/)alembic\s+revision')
#
# --- Package publishing ---
# FORCE_ASK_PATTERNS+=('(\b|/)npm\s+publish')
# FORCE_ASK_PATTERNS+=('(\b|/)pip\s+upload')
# FORCE_ASK_PATTERNS+=('(\b|/)twine\s+upload')
#
# --- Container registry operations ---
# FORCE_ASK_PATTERNS+=('(\b|/)docker\s+push')
# FORCE_ASK_PATTERNS+=('(\b|/)docker\s+login')
# =============================================================================

# =============================================================================
# CODE INJECTION PATTERNS — DISABLED by default
# =============================================================================
# Pipe-to-interpreter and command-substitution patterns are too restrictive in
# normal development. Claude legitimately uses things like
# `echo "..." | python3 -c "..."` and `$(curl ... | jq ...)` for diagnostics.
# The remaining hard blocks (eval, sudo, rm -rf /, mkfs, dd of=/dev/) cover the
# catastrophic cases. Uncomment to re-enable a stricter posture.
INJECTION_PATTERNS=(
    # '\|\s*(/[a-z/]*)?(bash|sh|zsh|python[23]?|perl|ruby|node|php)\b'
    # '\$\([^)]*\b(curl|wget|nc|netcat|bash|sh|zsh|python|perl|ruby|node|php|rm|dd|mkfs)\b'
    # '`[^`]*\b(curl|wget|nc|netcat|bash|sh|zsh|python|perl|ruby|node|php|rm|dd|mkfs)\b'
)

# =============================================================================
# SENSITIVE FILE PATTERNS - Block Read/Write access to credentials
# =============================================================================
SENSITIVE_FILES_WHITELIST=(
    '\.env\.example$'
)

SENSITIVE_FILES=(
    '\.env$'
    '\.env\.'
    '\.envrc$'
    '/\.aws/'
    '/\.azure/'
    '/\.gcloud/'
    '/\.ssh/'
    '\.pem$'
    '\.key$'
    'id_rsa'
    'id_ed25519'
    'id_ecdsa'
    'id_dsa'
    '/\.kube/'
    '/\.npmrc$'
    '/\.pypirc$'
    '/\.netrc$'
    '/\.docker/config\.json'
    '/\.config/gh/'
    'credentials'
    'secrets\.(json|ya?ml|conf|txt)$'
    'passwords?\.(json|ya?ml|conf|txt)$'
    'tokens?\.(json|ya?ml|conf|txt)$'
)

# =============================================================================
# BASH COMMAND VALIDATION
# =============================================================================
if [ "$TOOL_NAME" = "Bash" ] && [ -n "$COMMAND" ]; then

    NORMALIZED=$(normalize_command "$COMMAND")

    # --- CHECK 1: Hard Blocks (highest priority) ---
    for pattern in "${HARD_BLOCK_PATTERNS[@]}"; do
        if echo "$NORMALIZED" | grep -qE "$pattern"; then
            echo "" >&2
            echo "========== SECURITY HOOK BLOCK ==========" >&2
            echo "BLOCKED by: .claude/hooks/security-check.sh" >&2
            echo "Reason: Destructive or dangerous command detected" >&2
            echo "Pattern: $pattern" >&2
            echo "" >&2
            echo "This command could cause irreversible damage to" >&2
            echo "infrastructure, data, or git history." >&2
            echo "" >&2
            echo "To run this command: Execute it manually in your terminal." >&2
            echo "DO NOT DISABLE this security hook." >&2
            echo "==========================================" >&2
            exit 2
        fi
    done

    # Case-insensitive check
    for pattern in "${HARD_BLOCK_PATTERNS_NOCASE[@]}"; do
        if echo "$NORMALIZED" | grep -qiE "$pattern"; then
            echo "" >&2
            echo "========== SECURITY HOOK BLOCK ==========" >&2
            echo "BLOCKED by: .claude/hooks/security-check.sh" >&2
            echo "Reason: Database destruction command detected" >&2
            echo "Pattern: $pattern" >&2
            echo "" >&2
            echo "This command would destroy database data." >&2
            echo "" >&2
            echo "To run this command: Execute it manually in your terminal." >&2
            echo "DO NOT DISABLE this security hook." >&2
            echo "==========================================" >&2
            exit 2
        fi
    done

    # --- CHECK 2: Code Injection Patterns (no-op when array is empty) ---
    for pattern in ${INJECTION_PATTERNS[@]+"${INJECTION_PATTERNS[@]}"}; do
        if echo "$NORMALIZED" | grep -qE "$pattern"; then
            echo "" >&2
            echo "========== SECURITY HOOK BLOCK ==========" >&2
            echo "BLOCKED by: .claude/hooks/security-check.sh" >&2
            echo "Reason: Code injection pattern detected" >&2
            echo "Pattern: $pattern" >&2
            echo "" >&2
            echo "Piping to interpreters or command substitution can" >&2
            echo "execute arbitrary code and is a security risk." >&2
            echo "" >&2
            if [[ "$pattern" == *'|'* ]]; then
                echo "Hint: Use separate commands instead of piping to bash/python/etc." >&2
            else
                echo "Hint: If you need literal backticks or \$(), use single quotes" >&2
                echo "      to prevent shell expansion (e.g., 'text with \`code\`')." >&2
            fi
            echo "DO NOT DISABLE this security hook." >&2
            echo "==========================================" >&2
            exit 2
        fi
    done

    # --- CHECK 3: Repo-Aware rm Commands ---
    if echo "$NORMALIZED" | grep -qE '(\b|/)rm\s+'; then
        RM_PATHS=$(echo "$NORMALIZED" | sed -E 's/^.*\brm\s+//' | tr ' ' '\n' | grep -v '^-' | grep -v '^$')

        for rm_path in $RM_PATHS; do
            if [[ "$rm_path" == -* ]]; then
                continue
            fi

            # Allow rm in temp directories — Claude's scratch space.
            if [[ "$rm_path" == /tmp/* ]] || [[ "$rm_path" == /private/tmp/* ]] || [[ "$rm_path" == /var/folders/* ]]; then
                continue
            fi

            if ! is_path_in_repo "$rm_path"; then
                echo "" >&2
                echo "========== SECURITY HOOK BLOCK ==========" >&2
                echo "BLOCKED by: .claude/hooks/security-check.sh" >&2
                echo "Reason: rm command targets path outside repository" >&2
                echo "Path: $rm_path" >&2
                echo "" >&2
                echo "Claude Code can only delete files within the current" >&2
                echo "git repository. Files outside the repo are protected." >&2
                echo "" >&2
                echo "Repo root: $(get_repo_root)" >&2
                echo "" >&2
                echo "To delete files outside the repo: run manually in terminal." >&2
                echo "DO NOT DISABLE this security hook." >&2
                echo "==========================================" >&2
                exit 2
            fi
        done
    fi

    # --- CHECK 4: Branch-aware git push (optional — protected branches) ---
    # If PROTECTED_BRANCHES is set, force-ask before pushing to one of them.
    # Pushes to other branches pass through silently.
    if [ ${#PROTECTED_BRANCHES[@]} -gt 0 ] && echo "$NORMALIZED" | grep -qE '(\b|/)git\s+push'; then
        TARGET_BRANCH=$(echo "$NORMALIZED" | sed 's/.*git *push *[^ ]* *//' | awk '{print $1}')
        for protected in "${PROTECTED_BRANCHES[@]}"; do
            if [[ "$TARGET_BRANCH" == "$protected" ]]; then
                echo "{\"hookSpecificOutput\":{\"permissionDecision\":\"ask\",\"permissionDecisionReason\":\"Push to protected branch '$protected' requires approval\"}}"
                exit 0
            fi
        done
    fi

    # --- CHECK 5: Force Ask (triggers approval prompt) ---
    # Case-sensitive grep: patterns like `git branch -D` rely on the capital D
    # to distinguish forced delete from `git branch -d` (safe merged-only delete).
    for pattern in "${FORCE_ASK_PATTERNS[@]}"; do
        if echo "$NORMALIZED" | grep -qE "$pattern"; then
            echo "{\"hookSpecificOutput\":{\"permissionDecision\":\"ask\",\"permissionDecisionReason\":\"Critical command requires approval: $pattern\"}}"
            exit 0
        fi
    done
fi

# =============================================================================
# FILE READ VALIDATION
# =============================================================================
if [ "$TOOL_NAME" = "Read" ] && [ -n "$FILE_PATH" ]; then
    NORMALIZED_PATH=$(normalize_command "$FILE_PATH")

    WHITELISTED=false
    for pattern in "${SENSITIVE_FILES_WHITELIST[@]}"; do
        if echo "$NORMALIZED_PATH" | grep -qiE "$pattern"; then
            WHITELISTED=true
            break
        fi
    done

    if [ "$WHITELISTED" = false ]; then
        for pattern in "${SENSITIVE_FILES[@]}"; do
            if echo "$NORMALIZED_PATH" | grep -qiE "$pattern"; then
            echo "" >&2
            echo "========== SECURITY HOOK BLOCK ==========" >&2
            echo "BLOCKED by: .claude/hooks/security-check.sh" >&2
            echo "Reason: Sensitive file access denied" >&2
            echo "Pattern: $pattern" >&2
            echo "File: $FILE_PATH" >&2
            echo "" >&2
            echo "This file may contain secrets, credentials, or keys." >&2
            echo "Claude Code cannot read sensitive files." >&2
            echo "" >&2
            echo "DO NOT DISABLE this security hook." >&2
            echo "==========================================" >&2
            exit 2
        fi
    done
    fi
fi

# =============================================================================
# WRITE/EDIT VALIDATION
# =============================================================================
if [[ "$TOOL_NAME" = "Write" || "$TOOL_NAME" = "Edit" ]] && [ -n "$FILE_PATH" ]; then
    NORMALIZED_PATH=$(normalize_command "$FILE_PATH")

    # --- CHECK: Branch Protection (optional — PROTECTED_BRANCHES) ---
    # Resolve branch from the file's directory so worktree edits check the
    # worktree's branch, not the launch dir's. If the file path isn't inside any
    # git tree (e.g. ~/.claude/plans/*, /tmp/*), there is no branch to protect —
    # allow the write. Disabled entirely when PROTECTED_BRANCHES is empty.
    if [ ${#PROTECTED_BRANCHES[@]} -gt 0 ]; then
        if [[ "$FILE_PATH" = /* ]]; then
            BRANCH_LOOKUP_DIR=$(dirname "$FILE_PATH")
        else
            BRANCH_LOOKUP_DIR="."
        fi
        CURRENT_BRANCH=$(git -C "$BRANCH_LOOKUP_DIR" branch --show-current 2>/dev/null || echo "")
        if [ -n "$CURRENT_BRANCH" ]; then
            for protected in "${PROTECTED_BRANCHES[@]}"; do
                if [ "$CURRENT_BRANCH" = "$protected" ]; then
                    echo "" >&2
                    echo "========== SECURITY HOOK BLOCK ==========" >&2
                    echo "BLOCKED by: .claude/hooks/security-check.sh" >&2
                    echo "Reason: Cannot edit files on protected branch" >&2
                    echo "Branch: $CURRENT_BRANCH" >&2
                    echo "" >&2
                    echo "Direct edits to a protected branch are not allowed." >&2
                    echo "Create a feature branch first:" >&2
                    echo "  git checkout -b feature/your-feature-name" >&2
                    echo "" >&2
                    echo "DO NOT DISABLE this security hook." >&2
                    echo "==========================================" >&2
                    exit 2
                fi
            done
        fi
    fi

    WHITELISTED=false
    for pattern in "${SENSITIVE_FILES_WHITELIST[@]}"; do
        if echo "$NORMALIZED_PATH" | grep -qiE "$pattern"; then
            WHITELISTED=true
            break
        fi
    done

    if [ "$WHITELISTED" = false ]; then
        for pattern in "${SENSITIVE_FILES[@]}"; do
            if echo "$NORMALIZED_PATH" | grep -qiE "$pattern"; then
                echo "" >&2
                echo "========== SECURITY HOOK BLOCK ==========" >&2
                echo "BLOCKED by: .claude/hooks/security-check.sh" >&2
                echo "Reason: Sensitive file write denied" >&2
                echo "Pattern: $pattern" >&2
                echo "File: $FILE_PATH" >&2
                echo "" >&2
                echo "This file may contain secrets, credentials, or keys." >&2
                echo "Claude Code cannot modify sensitive files." >&2
                echo "" >&2
                echo "DO NOT DISABLE this security hook." >&2
                echo "==========================================" >&2
                exit 2
            fi
        done
    fi
fi

# =============================================================================
# All checks passed - allow command
# =============================================================================
exit 0
