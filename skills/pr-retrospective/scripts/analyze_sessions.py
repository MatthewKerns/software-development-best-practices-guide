#!/usr/bin/env python3
"""
Parse Claude Code session JSONL files and produce a structured summary for
pr-retrospective Excel generation.

Usage:
  analyze_sessions.py \
      --pr-window 2026-03-31 2026-04-19 \
      --project-path /path/to/repo \
      --out sessions.json

Session files live at: ~/.claude/projects/<path-encoded-cwd>/*.jsonl
  - path-encoded-cwd: the absolute path with "/" replaced by "-"
  - Multiple project dirs correspond to worktrees — this script scans every
    project dir whose decoded cwd starts with the passed --project-path.
  - Each JSONL line is one message object. Types seen in practice:
      user, assistant, tool_use, tool_result, summary,
      permission-mode, file-history-snapshot

Compaction detection:
  - top-level key isCompactSummary == True, OR
  - subtype == "compact_boundary"
  (Pre-compaction exchanges remain in the file either way; the compaction
   only shrinks what gets sent to the model on subsequent turns.)

Output shape (JSON written to --out):
{
  "window": {"start": "...", "end": "..."},
  "project_dirs_scanned": [...],
  "total_sessions": N,
  "total_messages": N,
  "sessions": [
    {
      "id": "uuid",
      "project_dir": "-Users-...",
      "first_ts": "...",
      "last_ts": "...",
      "duration_hours": 4.3,
      "message_count": 6440,
      "by_type": {"user": 123, "assistant": 456, ...},
      "compacted": true,
      "compaction_events": 3,
      "opening_prompt": "first user prompt, first 200 chars",
      "user_prompt_count": 45,
      "near_done_prompts": 3,       # "are we ready", "is this done", etc.
      "direction_changes": 2,       # "actually", "wait", "never mind"
      "tools_used": {"Bash": 800, "Edit": 200, "Read": 1500, ...},
      "top_files_edited": [["backend/api/v1/endpoints/products.py", 15], ...],
      "branches_seen": ["mcf-order-fulfillment", ...],
      "cwds_seen": [...]
    },
    ...
  ]
}
"""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


NEAR_DONE_PATTERNS = [
    r"\bare we (ready|done)\b",
    r"\bis (this|that|it) (done|ready|complete)\b",
    r"\bwhat('?s| is) left\b",
    r"\bhow close\b",
    r"\banything else\b",
    r"\bready (to (merge|ship|submit|push)|for review)\b",
    r"\bcan we (push|merge|ship|submit|commit)\b",
    r"\bany (blockers|issues|concerns|gaps)\b",
    r"\balmost (there|done|ready)\b",
    r"\bfinal (check|pass|review)\b",
    r"\blooks? good\??\b",
    r"\bgood to go\b",
    r"\bshould we (merge|push|ship)\b",
    r"\bapprove this\b",
    r"\ball (set|done|green)\b",
    r"\bare we good\b",
    r"\bwrap (this|it) up\b",
]
DIRECTION_CHANGE_PATTERNS = [
    r"^\s*actually[, ]",
    r"^\s*wait[, ]",
    r"\bnever mind\b",
    r"^\s*scratch (that|the last)\b",
    r"\blet'?s (try|go) (a )?(different|another|new)\b",
    r"\bon second thought\b",
    r"\bchange of plans?\b",
    r"\bnew approach\b",
    r"\bback (up|out|track)\b",
    r"\brevert (that|this|the)\b",
    r"\bundo (that|this|the last)\b",
    r"\bforget (that|this|what)\b",
    r"\binstead,?\s+(let'?s|we should|try)\b",
    r"\brethink\b",
]


def decode_project_dir(dir_name: str) -> str:
    """Reverse the path-encoding Claude Code uses."""
    return "/" + dir_name.lstrip("-").replace("-", "/")


def find_project_dirs(claude_root: Path, project_path: str) -> list[Path]:
    """Return every project dir whose decoded cwd starts with project_path."""
    if not claude_root.exists():
        return []
    # Normalize: strip trailing slash; match either exact or "{project_path}-..." suffix
    project_path = project_path.rstrip("/")
    hits: list[Path] = []
    for d in sorted(claude_root.iterdir()):
        if not d.is_dir() or not d.name.startswith("-"):
            continue
        decoded = decode_project_dir(d.name)
        # Encoded dirs use "-" in place of "/" AND "." — we conservatively match prefixes
        # on the encoded name directly.
        encoded_project = project_path.replace("/", "-").replace(".", "-")
        if d.name == encoded_project or d.name.startswith(encoded_project + "-"):
            hits.append(d)
    return hits


def parse_ts(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        # JSONL stores ISO 8601 with trailing "Z"
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def window_contains(ts: datetime | None, start: datetime, end: datetime) -> bool:
    if ts is None:
        return False
    # All inputs should be timezone-aware; coerce naive start/end to UTC if needed
    if start.tzinfo is None:
        start = start.replace(tzinfo=ts.tzinfo)
    if end.tzinfo is None:
        end = end.replace(tzinfo=ts.tzinfo)
    return start <= ts <= end


def extract_text(message: Any) -> str:
    """Pull the textual user content from a message object of any shape."""
    if isinstance(message, str):
        return message
    if isinstance(message, dict):
        content = message.get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts: list[str] = []
            for c in content:
                if isinstance(c, dict):
                    t = c.get("text") or c.get("content") or ""
                    if isinstance(t, str):
                        parts.append(t)
            return "\n".join(parts)
    return ""


def extract_tool_info(msg_obj: dict) -> tuple[str | None, str | None]:
    """Return (tool_name, file_path_hint) from a tool_use message if present."""
    message = msg_obj.get("message", {})
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, list):
        return None, None
    for c in content:
        if not isinstance(c, dict) or c.get("type") != "tool_use":
            continue
        name = c.get("name")
        inp = c.get("input") or {}
        path = None
        if isinstance(inp, dict):
            path = inp.get("file_path") or inp.get("path") or inp.get("notebook_path")
            # Fall back to extracting a path from a Bash command if present
            if not path and name == "Bash":
                cmd = inp.get("command", "")
                m = re.search(r"(?:/[^\s:]+)+\.\w+", cmd or "")
                if m:
                    path = m.group(0)
        return name, path
    return None, None


def analyze_session(path: Path, start: datetime, end: datetime) -> dict | None:
    by_type: Counter[str] = Counter()
    tools: Counter[str] = Counter()
    files: Counter[str] = Counter()
    branches: set[str] = set()
    cwds: set[str] = set()
    user_prompts: list[str] = []
    near_done = 0
    direction = 0
    compaction_events = 0
    first_ts: datetime | None = None
    last_ts: datetime | None = None
    session_id: str | None = None
    in_window = False

    try:
        with path.open("r", encoding="utf-8") as fh:
            for line in fh:
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue

                t = obj.get("type", "?")
                by_type[t] += 1

                if session_id is None:
                    session_id = obj.get("sessionId") or path.stem

                ts = parse_ts(obj.get("timestamp"))
                if ts:
                    if first_ts is None or ts < first_ts:
                        first_ts = ts
                    if last_ts is None or ts > last_ts:
                        last_ts = ts
                    if window_contains(ts, start, end):
                        in_window = True

                if obj.get("isCompactSummary") or obj.get("subtype") == "compact_boundary":
                    compaction_events += 1

                if obj.get("gitBranch"):
                    branches.add(obj["gitBranch"])
                if obj.get("cwd"):
                    cwds.add(obj["cwd"])

                if t == "user":
                    text = extract_text(obj.get("message", {}))
                    if text and not text.startswith("<"):  # skip command/tool wrappers
                        user_prompts.append(text)
                        low = text.lower()
                        if any(re.search(p, low) for p in NEAR_DONE_PATTERNS):
                            near_done += 1
                        if any(re.search(p, low) for p in DIRECTION_CHANGE_PATTERNS):
                            direction += 1

                if t == "assistant":
                    tool_name, file_path = extract_tool_info(obj)
                    if tool_name:
                        tools[tool_name] += 1
                    if file_path:
                        files[file_path] += 1
    except OSError:
        return None

    if not in_window:
        return None  # session entirely outside the window

    duration_hours = (
        round((last_ts - first_ts).total_seconds() / 3600, 2)
        if first_ts and last_ts
        else 0.0
    )
    opening = next((p for p in user_prompts if p.strip()), "")[:200]

    return {
        "id": session_id,
        "file": str(path),
        "project_dir": path.parent.name,
        "first_ts": first_ts.isoformat() if first_ts else None,
        "last_ts": last_ts.isoformat() if last_ts else None,
        "duration_hours": duration_hours,
        "message_count": sum(by_type.values()),
        "by_type": dict(by_type),
        "compacted": compaction_events > 0,
        "compaction_events": compaction_events,
        "opening_prompt": opening,
        "user_prompt_count": len(user_prompts),
        "near_done_prompts": near_done,
        "direction_changes": direction,
        "tools_used": dict(tools.most_common(20)),
        "top_files_edited": files.most_common(20),
        "branches_seen": sorted(branches),
        "cwds_seen": sorted(cwds),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pr-window", nargs=2, required=True, metavar=("START", "END"))
    ap.add_argument("--project-path", required=True)
    ap.add_argument("--claude-root", default=str(Path.home() / ".claude" / "projects"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    start = datetime.fromisoformat(args.pr_window[0])
    end = datetime.fromisoformat(args.pr_window[1])
    # Treat naive dates as "whole day" inclusive
    if start.tzinfo is None:
        start = start.replace(hour=0, minute=0)
    if end.tzinfo is None:
        end = end.replace(hour=23, minute=59, second=59)

    claude_root = Path(args.claude_root)
    dirs = find_project_dirs(claude_root, args.project_path)

    sessions: list[dict] = []
    for d in dirs:
        for jf in sorted(d.glob("*.jsonl")):
            rec = analyze_session(jf, start, end)
            if rec is not None:
                sessions.append(rec)

    sessions.sort(key=lambda s: s.get("first_ts") or "")
    payload = {
        "window": {"start": start.isoformat(), "end": end.isoformat()},
        "project_dirs_scanned": [str(d) for d in dirs],
        "total_sessions": len(sessions),
        "total_messages": sum(s["message_count"] for s in sessions),
        "sessions": sessions,
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {out} — {len(sessions)} sessions, {payload['total_messages']} messages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
