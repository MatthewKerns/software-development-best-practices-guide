#!/bin/bash
# =============================================================================
# CLAUDE CODE STATUS LINE — Portable / generic edition
# =============================================================================
# PROVENANCE
#   Extracted and genericized from a private project's statusLine renderer.
#   Project-specific env display (e.g. AWS_PROFILE and other app-specific vars)
#   has been removed. Everything here degrades gracefully when optional tooling
#   (ccusage, the macOS Keychain, gdate) is missing — missing data renders "?".
#
# Four lines:
#   L1: worktree marker + dir + branch + diff summary  · 🧠 model
#   L2: context % (used/total)  · session $
#   L3: ⏱  5h progress bar + %  · $ window  · 🔥 burn $/hr  · 🌳 footprint
#   L4: 📅 7d progress bar + %  · $ week  · 🔥 $ per-day avg  · 🌳 footprint
#
# Worktree:   linked if `git --git-dir` != `git --git-common-dir`.
# 5h / 7d %:  fetched from https://api.anthropic.com/api/oauth/usage using the
#             OAuth access token. On macOS the token is read from the Keychain
#             (service "Claude Code-credentials"); otherwise from
#             ~/.claude/.credentials.json. Cached at /tmp/cc-usage-cache-${UID}.json
#             with TTL=300s. OPTIONAL — lines render "?" without it.
# 7d / block $: summed from `ccusage` if installed (OPTIONAL).
#
# Configure in .claude/settings.json → statusLine. Runs after every assistant
# message — keep it fast (<400ms warm, longer when refreshing cache).
#
# NOTE: dollar figures are token-pricing equivalents (what the same work would
# cost via the pay-per-token API). On Max/Pro plans you pay a flat subscription;
# the 5h/7d % from /api/oauth/usage are the authoritative plan-utilization
# numbers.
# =============================================================================

USAGE_CACHE="/tmp/cc-usage-cache-${UID:-$(id -u)}.json"
USAGE_TTL=300

input=$(cat)

# ---- stdin fields -----------------------------------------------------------
model_name=$(echo "$input" | jq -r '.model.display_name // "?"')
context_window_size=$(echo "$input" | jq -r '.context_window.context_window_size // 0')
current_usage=$(echo "$input" | jq '.context_window.current_usage')

# Resolve workspace dir. Claude Code treats linked worktrees as part of the
# parent project — session logs land in the main repo's project dir, $PWD and
# all stdin fields (cwd, workspace.current_dir, workspace.project_dir) point at
# the main repo even when the user launched `claude` from a worktree. The only
# place the worktree path survives is in the ancestor shell's own CWD (the
# shell that ran `claude`). Walk up the process tree to recover it.
detect_terminal_cwd() {
    local pid=$PPID
    local steps=0
    while [ "$pid" -gt 1 ] && [ $steps -lt 15 ]; do
        local comm
        comm=$(ps -o comm= -p "$pid" 2>/dev/null | awk '{print $NF}' | sed 's|^.*/||' | sed 's|^-||')
        case "$comm" in
            zsh|bash|sh|fish|dash|tcsh|ksh)
                lsof -a -p "$pid" -d cwd -Fn 2>/dev/null | awk '/^n/{print substr($0,2); exit}'
                return
                ;;
        esac
        local ppid
        ppid=$(ps -o ppid= -p "$pid" 2>/dev/null | tr -d ' ')
        [ -z "$ppid" ] && return
        pid="$ppid"
        steps=$((steps + 1))
    done
}

# Native Claude Code worktree fields (newer versions ship these). When set,
# .worktree.path is the absolute path to the linked worktree — definitive.
# Falls back to process-tree walk for older versions that don't ship it.
stdin_worktree_path=$(echo "$input" | jq -r '.worktree.path // empty')
stdin_worktree_name=$(echo "$input" | jq -r '.worktree.name // empty')
stdin_worktree_branch=$(echo "$input" | jq -r '.worktree.branch // empty')

terminal_cwd=$(detect_terminal_cwd)
script_pwd="$PWD"
stdin_cwd=$(echo "$input" | jq -r '.cwd // empty')
stdin_workspace=$(echo "$input" | jq -r '.workspace.current_dir // empty')
stdin_project=$(echo "$input" | jq -r '.workspace.project_dir // empty')


workspace_dir=""
# .worktree.path is Claude Code's native, authoritative signal — use it first.
if [ -n "$stdin_worktree_path" ] && [ -e "$stdin_worktree_path/.git" ]; then
    workspace_dir="$stdin_worktree_path"
fi
# Otherwise try each candidate, picking the first that IS a linked worktree.
if [ -z "$workspace_dir" ]; then
    for cand in "$terminal_cwd" "$script_pwd" "$stdin_cwd" "$stdin_workspace" "$stdin_project"; do
        [ -z "$cand" ] && continue
        [ ! -e "$cand/.git" ] && continue
        gdir=$(cd "$cand" 2>/dev/null && git rev-parse --git-dir 2>/dev/null)
        gcommon=$(cd "$cand" 2>/dev/null && git rev-parse --git-common-dir 2>/dev/null)
        if [ -n "$gdir" ] && [ -n "$gcommon" ] && [ "$gdir" != "$gcommon" ]; then
            workspace_dir="$cand"
            break
        fi
    done
fi
# Otherwise pick the first candidate that's any git checkout.
if [ -z "$workspace_dir" ]; then
    for cand in "$terminal_cwd" "$stdin_workspace" "$stdin_cwd" "$script_pwd" "$stdin_project"; do
        [ -n "$cand" ] && [ -e "$cand/.git" ] && { workspace_dir="$cand"; break; }
    done
fi
[ -z "$workspace_dir" ] && workspace_dir="${stdin_workspace:-${stdin_cwd:-$script_pwd}}"

# ---- context % --------------------------------------------------------------
fmt_k() { local n=${1:-0}; if [ "$n" -ge 1000 ]; then echo "$((n / 1000))k"; else echo "$n"; fi; }
if [ "$current_usage" != "null" ]; then
    input_tokens=$(echo "$current_usage" | jq -r '.input_tokens // 0')
    cache_creation=$(echo "$current_usage" | jq -r '.cache_creation_input_tokens // 0')
    cache_read=$(echo "$current_usage" | jq -r '.cache_read_input_tokens // 0')
    total_current=$((input_tokens + cache_creation + cache_read))
    if [ "$context_window_size" -gt 0 ]; then
        ctx_pct=$((total_current * 100 / context_window_size))
    else
        ctx_pct=0
    fi
    tok_used=$(fmt_k "$total_current")
    tok_total=$(fmt_k "$context_window_size")
else
    ctx_pct=0; tok_used="0"; tok_total="?"
fi

# ---- worktree + branch + diff ----------------------------------------------
wt_marker="📁"; wt_name=""; branch=""; diff_summary=""
if [ -e "$workspace_dir/.git" ]; then
    pushd "$workspace_dir" >/dev/null 2>&1
    git_dir=$(git rev-parse --git-dir 2>/dev/null)
    git_common_dir=$(git rev-parse --git-common-dir 2>/dev/null)
    toplevel=$(git rev-parse --show-toplevel 2>/dev/null)
    branch=$(git --no-optional-locks branch --show-current 2>/dev/null)
    [ -z "$branch" ] && branch=$(git --no-optional-locks rev-parse --short HEAD 2>/dev/null)
    [ -n "$toplevel" ] && wt_name=$(basename "$toplevel")
    if [ -n "$git_dir" ] && [ -n "$git_common_dir" ] && [ "$git_dir" != "$git_common_dir" ]; then
        wt_marker="🌳"
    fi
    stat=$(git --no-optional-locks diff --shortstat 2>/dev/null)
    if [ -n "$stat" ]; then
        added=$(echo "$stat" | grep -oE '[0-9]+ insertion' | grep -oE '[0-9]+'); [ -z "$added" ] && added=0
        removed=$(echo "$stat" | grep -oE '[0-9]+ deletion' | grep -oE '[0-9]+'); [ -z "$removed" ] && removed=0
        diff_summary="  +${added} −${removed}"
    fi
    popd >/dev/null 2>&1
else
    wt_name=$(basename "$workspace_dir")
fi

# ---- ccusage: session $ + burn rate + 5h block $ (OPTIONAL) ----------------
session_cost=""; burn_rate=""; block_cost=""; block_resets=""
if command -v ccusage >/dev/null 2>&1; then
    ccusage_input=$(echo "$input" | jq 'del(.context_window)')
    ccusage_out=$(echo "$ccusage_input" | ccusage statusline --visual-burn-rate off 2>/dev/null)
    # Format: "🤖 model | 💰 X session / Y today / Z block (Th Tm left) | 🔥 $R/hr | 🧠 ctx"
    cost_seg=$(echo "$ccusage_out" | awk -F' \\| ' '{for(i=1;i<=NF;i++) if($i ~ /^💰/) print $i}')
    burn_rate=$(echo "$ccusage_out" | awk -F' \\| ' '{for(i=1;i<=NF;i++) if($i ~ /^🔥/) print $i}' | sed 's/^🔥 *//')
    session_cost=$(echo "$cost_seg" | sed -nE 's/.*💰[[:space:]]*([^ ]+)[[:space:]]+session.*/\1/p')
    block_cost=$(echo "$cost_seg" | sed -nE 's/.*\/[[:space:]]*([^ ]+)[[:space:]]+block.*/\1/p')
    block_resets=$(echo "$cost_seg" | sed -nE 's/.*\(([^)]*) left\).*/\1/p')
fi

# ---- 5h / 7d utilization via /api/oauth/usage (cached, OPTIONAL) -----------
maybe_refresh_usage_cache() {
    local now mtime age
    now=$(date +%s)
    if [ -f "$USAGE_CACHE" ] && [ -s "$USAGE_CACHE" ]; then
        mtime=$(stat -f %m "$USAGE_CACHE" 2>/dev/null || stat -c %Y "$USAGE_CACHE" 2>/dev/null || echo 0)
        age=$((now - mtime))
        if [ "$age" -lt "$USAGE_TTL" ]; then return 0; fi
    fi

    local token=""
    # macOS Keychain (guarded — only present on macOS).
    if command -v security >/dev/null 2>&1; then
        token=$(security find-generic-password -s 'Claude Code-credentials' -w 2>/dev/null \
                | jq -r '.claudeAiOauth.accessToken // empty' 2>/dev/null)
    fi
    # Fallback: credentials file (Linux / non-Keychain setups).
    if [ -z "$token" ] && [ -f "$HOME/.claude/.credentials.json" ]; then
        token=$(jq -r '.claudeAiOauth.accessToken // empty' "$HOME/.claude/.credentials.json" 2>/dev/null)
    fi
    [ -z "$token" ] && return 1

    local resp
    resp=$(curl -fsS --max-time 3 https://api.anthropic.com/api/oauth/usage \
            -H "Authorization: Bearer $token" \
            -H "anthropic-beta: oauth-2025-04-20" 2>/dev/null)
    [ -z "$resp" ] && return 1

    local seven_day_cost=0
    local seven_tokens_json='{"input":0,"output":0,"cc":0,"cr":0}'
    local block_tokens_json='{"input":0,"output":0,"cc":0,"cr":0}'
    if command -v ccusage >/dev/null 2>&1; then
        local since
        since=$(date -v-7d +%Y%m%d 2>/dev/null || date -d "7 days ago" +%Y%m%d 2>/dev/null)
        if [ -n "$since" ]; then
            local daily_json
            daily_json=$(ccusage daily --json --since "$since" 2>/dev/null)
            if [ -n "$daily_json" ]; then
                seven_day_cost=$(echo "$daily_json" | jq '[.daily[].totalCost] | add // 0' 2>/dev/null)
                seven_tokens_json=$(echo "$daily_json" | jq '{
                    input:  ([.daily[].inputTokens]         | add // 0),
                    output: ([.daily[].outputTokens]        | add // 0),
                    cc:     ([.daily[].cacheCreationTokens] | add // 0),
                    cr:     ([.daily[].cacheReadTokens]     | add // 0)
                }' 2>/dev/null)
            fi
            [ -z "$seven_day_cost" ] && seven_day_cost=0
        fi
        # Block tokens (slow: ~3s, hence cached at the 300s TTL)
        local block_json
        block_json=$(ccusage blocks --active --json 2>/dev/null \
                    | jq '.blocks[] | select(.isActive == true) | {
                        input:  (.tokenCounts.inputTokens             // 0),
                        output: (.tokenCounts.outputTokens            // 0),
                        cc:     (.tokenCounts.cacheCreationInputTokens // 0),
                        cr:     (.tokenCounts.cacheReadInputTokens     // 0)
                    }' 2>/dev/null)
        [ -n "$block_json" ] && block_tokens_json="$block_json"
    fi

    echo "$resp" | jq \
        --argjson c "$seven_day_cost" \
        --argjson st "$seven_tokens_json" \
        --argjson bt "$block_tokens_json" \
        '. + {seven_day_cost: $c, seven_day_tokens: $st, block_tokens: $bt}' > "$USAGE_CACHE" 2>/dev/null
}

maybe_refresh_usage_cache

five_pct=""; seven_pct=""; seven_cost=""; five_resets_at=""; seven_resets_at=""
block_in=0; block_out=0; block_cc=0; block_cr=0
seven_in=0; seven_out=0; seven_cc=0; seven_cr=0
if [ -f "$USAGE_CACHE" ] && [ -s "$USAGE_CACHE" ]; then
    five_pct=$(jq -r '.five_hour.utilization // empty' "$USAGE_CACHE" 2>/dev/null)
    seven_pct=$(jq -r '.seven_day.utilization // empty' "$USAGE_CACHE" 2>/dev/null)
    seven_cost=$(jq -r '.seven_day_cost // empty' "$USAGE_CACHE" 2>/dev/null)
    five_resets_at=$(jq -r '.five_hour.resets_at // empty' "$USAGE_CACHE" 2>/dev/null)
    seven_resets_at=$(jq -r '.seven_day.resets_at // empty' "$USAGE_CACHE" 2>/dev/null)
    block_in=$(jq -r '.block_tokens.input // 0' "$USAGE_CACHE" 2>/dev/null)
    block_out=$(jq -r '.block_tokens.output // 0' "$USAGE_CACHE" 2>/dev/null)
    block_cc=$(jq -r '.block_tokens.cc // 0' "$USAGE_CACHE" 2>/dev/null)
    block_cr=$(jq -r '.block_tokens.cr // 0' "$USAGE_CACHE" 2>/dev/null)
    seven_in=$(jq -r '.seven_day_tokens.input // 0' "$USAGE_CACHE" 2>/dev/null)
    seven_out=$(jq -r '.seven_day_tokens.output // 0' "$USAGE_CACHE" 2>/dev/null)
    seven_cc=$(jq -r '.seven_day_tokens.cc // 0' "$USAGE_CACHE" 2>/dev/null)
    seven_cr=$(jq -r '.seven_day_tokens.cr // 0' "$USAGE_CACHE" 2>/dev/null)
fi

# ---- helpers ---------------------------------------------------------------
bar() {
    local pct=${1:-0}
    pct=${pct%.*}
    [ -z "$pct" ] && pct=0
    [ "$pct" -gt 100 ] && pct=100
    [ "$pct" -lt 0 ] && pct=0
    local width=10
    local filled=$((pct * width / 100))
    [ "$pct" -gt 0 ] && [ "$filled" -eq 0 ] && filled=1
    local out="" i
    for ((i=0; i<width; i++)); do
        if [ $i -lt $filled ]; then out="${out}▰"; else out="${out}▱"; fi
    done
    echo "$out"
}

pct_int() {
    local p=${1:-}
    [ -z "$p" ] && { echo ""; return; }
    printf '%.0f' "$p" 2>/dev/null
}

# Compute gCO₂e from token counts. Energy rates are conservative middle-of-road
# numbers anchored to the Feb 2025 Epoch AI revision and third-party Claude
# figures. Per-MTok rates (Wh/MTok), Claude-class weighted mix on AWS:
#   Input 150 · Output 750 · Cache-create 250 · Cache-read 10
# Infra: PUE 1.14, 287 gCO₂e/kWh (AWS blended). Honest uncertainty: ±2-3x.
co2_grams() {
    local in=${1:-0} out=${2:-0} cc=${3:-0} cr=${4:-0}
    local total=$((in + out + cc + cr))
    [ "$total" -eq 0 ] && return
    awk -v i="$in" -v o="$out" -v cc="$cc" -v cr="$cr" 'BEGIN {
        wh = (i*150 + o*750 + cc*250 + cr*10) / 1000000
        wh_pue = wh * 1.14
        printf "%.2f", (wh_pue / 1000) * 287
    }'
}

# Format gCO₂e for display: "Xg CO₂e" or "X.Xkg CO₂e".
fmt_co2() {
    local g=$1
    [ -z "$g" ] && return
    awk -v g="$g" 'BEGIN {
        if (g >= 1000) printf "%.1f kg CO₂e", g/1000
        else printf "%.0f g CO₂e", g
    }'
}

# Format tree-time to offset a given gCO₂e using mature-tree absorption
# (~22 kg CO₂/year). Auto-picks the most readable unit and pluralizes.
fmt_tree_time() {
    local g=$1
    [ -z "$g" ] && return
    awk -v g="$g" 'BEGIN {
        g_per_hour  = 2.510    # 22000 g/yr ÷ (365.25*24) hr
        g_per_day   = 60.232   # 22000 g/yr ÷ 365.25 day
        g_per_month = 1832     # ≈ 22000/12
        g_per_year  = 22000

        hours = g / g_per_hour
        days  = g / g_per_day
        months = g / g_per_month
        years = g / g_per_year

        if (hours < 48) {
            n = sprintf("%.0f", hours)
            unit = (n == "1") ? "tree-hour" : "tree-hours"
            printf "%s %s", n, unit
        } else if (days < 90) {
            n = sprintf("%.0f", days)
            unit = (n == "1") ? "tree-day" : "tree-days"
            printf "%s %s", n, unit
        } else if (months < 24) {
            n = sprintf("%.0f", months)
            unit = (n == "1") ? "tree-month" : "tree-months"
            printf "%s %s", n, unit
        } else {
            n = sprintf("%.1f", years)
            unit = (n == "1.0") ? "tree-year" : "tree-years"
            printf "%s %s", n, unit
        }
    }'
}

# Format an ISO 8601 timestamp as "Xd Yh Zm" until it. Empty if past/unparseable.
fmt_until() {
    local target_iso="$1"
    [ -z "$target_iso" ] && return
    local target_epoch=""
    if command -v gdate >/dev/null 2>&1; then
        target_epoch=$(gdate -d "$target_iso" +%s 2>/dev/null)
    fi
    if [ -z "$target_epoch" ]; then
        local cleaned
        cleaned=$(echo "$target_iso" | sed -E 's/\.[0-9]+//; s/\+00:00$//; s/Z$//')
        target_epoch=$(date -j -u -f "%Y-%m-%dT%H:%M:%S" "$cleaned" +%s 2>/dev/null)
    fi
    [ -z "$target_epoch" ] && return
    local now diff days hours mins out=""
    now=$(date +%s)
    diff=$((target_epoch - now))
    [ $diff -le 0 ] && { echo "0m"; return; }
    days=$((diff / 86400))
    hours=$(( (diff % 86400) / 3600 ))
    mins=$(( (diff % 3600) / 60 ))
    [ $days -gt 0 ] && out="${days}d "
    if [ $days -gt 0 ] || [ $hours -gt 0 ]; then
        out="${out}${hours}h "
    fi
    out="${out}${mins}m"
    echo "$out"
}

# Shorten the model display name: "Opus 4.7 (1M context)" -> "Opus 4.7 (1M)"
model_short=$(echo "$model_name" | sed -E 's/ context\)/)/')

# Right-pad $1 with spaces to char target $2 (bash counts UTF-8 codepoints
# natively in a UTF-8 locale; awk on BSD counts bytes which over-counts emoji).
right_pad() {
    local s="$1" target="$2"
    local pad=$((target - ${#s}))
    [ $pad -lt 0 ] && pad=0
    printf '%s%*s' "$s" $pad ''
}

# Column widths in UTF-8 codepoints.
COL1_W=34
COL2_W=18
COL3_W=18

# Compose up to four columns. Empty trailing cells collapse; internal empty
# cells get padded so later columns still align.
compose() {
    local c1="$1" c2="$2" c3="$3" c4="$4"
    local has2=""; [ -n "$c2" ] && has2=1
    local has3=""; [ -n "$c3" ] && has3=1
    local has4=""; [ -n "$c4" ] && has4=1

    if [ -z "$has2" ] && [ -z "$has3" ] && [ -z "$has4" ]; then
        printf '%s' "$c1"
        return
    fi

    local out
    out=$(right_pad "$c1" $COL1_W)
    if [ -n "$has2" ]; then
        if [ -n "$has3" ] || [ -n "$has4" ]; then
            out="${out}$(right_pad "$c2" $COL2_W)"
        else
            out="${out}${c2}"
        fi
    elif [ -n "$has3" ] || [ -n "$has4" ]; then
        out="${out}$(printf '%*s' $COL2_W '')"
    fi
    if [ -n "$has3" ]; then
        if [ -n "$has4" ]; then
            out="${out}$(right_pad "$c3" $COL3_W)"
        else
            out="${out}${c3}"
        fi
    elif [ -n "$has4" ]; then
        out="${out}$(printf '%*s' $COL3_W '')"
    fi
    [ -n "$has4" ] && out="${out}${c4}"
    printf '%s' "$out"
}

# Back-compat shim — three-column callers still work.
compose3() { compose "$1" "$2" "$3" ""; }

# ---- compose ---------------------------------------------------------------
# Line 1 — vertical pipes (no padding, free-form)
line1="${wt_marker} ${wt_name}"
[ -n "$branch" ] && line1="${line1} | 🌿 ${branch}"
line1="${line1} | 🧠 ${model_short}"

# Line 2 — context window with progress bar
ctx_col1="Cx $(bar "$ctx_pct") ${ctx_pct}% (${tok_used}/${tok_total})"
ctx_col2=""; [ -n "$session_cost" ] && ctx_col2="${session_cost} session"
line2=$(compose3 "$ctx_col1" "$ctx_col2" "")

# Line 3 — 5h window
five_until=$(fmt_until "$five_resets_at")
five_pct_i=$(pct_int "$five_pct")
if [ -n "$five_pct_i" ]; then
    five_col1="5h $(bar "$five_pct_i") ${five_pct_i}%"
    [ -n "$five_until" ] && five_col1="${five_col1} (${five_until})"
else
    five_col1="5h $(bar 0) ?%"
    [ -n "$block_resets" ] && five_col1="${five_col1} (${block_resets})"
fi
five_col2=""; [ -n "$block_cost" ] && five_col2="${block_cost} window"
five_col3=""; [ -n "$burn_rate" ] && five_col3="🔥 ${burn_rate}"
five_col4=""
block_co2=$(co2_grams "$block_in" "$block_out" "$block_cc" "$block_cr")
if [ -n "$block_co2" ]; then
    five_col4="🌳 $(fmt_tree_time "$block_co2") ($(fmt_co2 "$block_co2"))"
fi
line3=$(compose "$five_col1" "$five_col2" "$five_col3" "$five_col4")

# Line 4 — 7d window
seven_until=$(fmt_until "$seven_resets_at")
seven_pct_i=$(pct_int "$seven_pct")
if [ -n "$seven_pct_i" ]; then
    seven_col1="7d $(bar "$seven_pct_i") ${seven_pct_i}%"
    [ -n "$seven_until" ] && seven_col1="${seven_col1} (${seven_until})"
else
    seven_col1="7d $(bar 0) ?%"
fi
seven_col2=""; seven_col3=""; seven_col4=""
if [ -n "$seven_cost" ] && [ "$seven_cost" != "0" ]; then
    seven_cost_fmt=$(printf '$%.2f' "$seven_cost" 2>/dev/null)
    daily_avg=$(echo "$seven_cost" | awk '{printf "$%.2f", $1/7}')
    seven_col2="${seven_cost_fmt} week"
    seven_col3="🔥 ${daily_avg}/day"
fi
seven_co2=$(co2_grams "$seven_in" "$seven_out" "$seven_cc" "$seven_cr")
if [ -n "$seven_co2" ]; then
    seven_col4="🌳 $(fmt_tree_time "$seven_co2") ($(fmt_co2 "$seven_co2"))"
fi
line4=$(compose "$seven_col1" "$seven_col2" "$seven_col3" "$seven_col4")

printf "%s\n%s\n%s\n%s" "$line1" "$line2" "$line3" "$line4"
