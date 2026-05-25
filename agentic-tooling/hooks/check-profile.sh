#!/bin/bash
# =============================================================================
# CLAUDE CODE PROFILE CONTEXT — SessionStart Hook (portable / generic edition)
# =============================================================================
# PROVENANCE
#   Extracted and genericized from a private project's SessionStart profile
#   validator. The mechanism is preserved; project-specific profile names and
#   security wording have been parameterized.
#
# WHAT IT DOES
#   At session start, reads the active permission-profile label from
#   `.claude/settings.local.json` (key: `_profile_label`) and injects it as
#   context Claude can see via stdout. Per Claude Code docs, SessionStart stdout
#   on exit 0 is added as context (not shown to the user directly). The status
#   line handles user-visible display.
#
#   If no settings.local.json exists, it emits a "no profile loaded" notice so
#   Claude knows the workspace is unconfigured.
#
# CUSTOMIZING
#   - KNOWN_PROFILES: optional list of expected profile labels. If set and the
#     loaded label isn't in it, the notice flags it as unrecognized. Leave empty
#     to accept any label.
#   - SETUP_HINT: the command your project uses to (re)select a profile.
#   - SECURITY_SUMMARY: one-line reminder of the active guardrails. Edit to match
#     whatever your security-check.sh enforces.
# =============================================================================

set -euo pipefail

# -----------------------------------------------------------------------------
# CONFIG (edit for your project)
# -----------------------------------------------------------------------------
# Expected profile labels (optional). Empty = accept any label without flagging.
# Example: KNOWN_PROFILES=("read-only" "standard" "trusted")
KNOWN_PROFILES=()

# Command the user runs to choose/refresh a profile (shown when none is loaded).
SETUP_HINT="select a permission profile (e.g. copy a profile into .claude/settings.local.json), then restart Claude Code"

# One-line summary of the guardrails enforced by security-check.sh.
SECURITY_SUMMARY="Security hook (.claude/hooks/security-check.sh) is the defense-in-depth layer. Hard blocks: sudo, su, rm -rf / family, mkfs, dd of=/dev/, > /dev/sd*, eval, source-prefix, git rebase, DROP DATABASE, redis FLUSHALL/FLUSHDB. Force-asks: git push --force / reset --hard / clean -f / branch -D (plus any optional cloud/infra guardrails you have enabled)."

# -----------------------------------------------------------------------------
# Resolve project dir / settings.local.json
# -----------------------------------------------------------------------------
# Prefer Claude Code's CLAUDE_PROJECT_DIR; fall back to walking up from the hook.
if [ -n "${CLAUDE_PROJECT_DIR:-}" ]; then
    PROJECT_DIR="$CLAUDE_PROJECT_DIR"
else
    PROJECT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
fi
SETTINGS_LOCAL="$PROJECT_DIR/.claude/settings.local.json"

# --- No profile loaded ---
if [ ! -f "$SETTINGS_LOCAL" ]; then
    cat <<CONTEXT
[SECURITY PROFILE] No permission profile loaded. To configure: $SETUP_HINT. Do not proceed with work until configured.
CONTEXT
    exit 0
fi

# --- Read profile label ---
PROFILE_LABEL=$(jq -r '._profile_label // "unknown"' "$SETTINGS_LOCAL" 2>/dev/null || echo "unknown")

# --- Optionally validate against the known list ---
PROFILE_NOTE=""
if [ ${#KNOWN_PROFILES[@]} -gt 0 ]; then
    RECOGNIZED=false
    for known in "${KNOWN_PROFILES[@]}"; do
        if [ "$PROFILE_LABEL" = "$known" ]; then
            RECOGNIZED=true
            break
        fi
    done
    if [ "$RECOGNIZED" = false ]; then
        PROFILE_NOTE=" (WARNING: '$PROFILE_LABEL' is not a recognized profile — expected one of: ${KNOWN_PROFILES[*]})"
    fi
fi

# --- Output context for Claude ---
cat <<CONTEXT
[SECURITY PROFILE] $PROFILE_LABEL active.$PROFILE_NOTE
$SECURITY_SUMMARY
CONTEXT

exit 0
