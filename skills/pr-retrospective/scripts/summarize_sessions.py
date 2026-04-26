#!/usr/bin/env python3
"""
Summarize Claude Code sessions into short, informative blurbs that replace
the raw `opening_prompt` field in the retrospective workbook.

Design:
  - One batched Anthropic API call covers all sessions in sessions.json.
  - System prompt is cached via `cache_control` so re-runs are cheap.
  - Model replies in pipe-delimited CSV (session_id|summary|work_type).
    Pipe-delimited because prose summaries often contain commas.
  - Output writes sessions.json back in-place (or to --out) with two new
    fields per session: `summary` and `work_type`.

Usage:
  summarize_sessions.py \
      --sessions-json /tmp/pr6-retro-test/sessions.json \
      --out /tmp/pr6-retro-test/sessions.json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import anthropic


SYSTEM_PROMPT = """You summarize Claude Code engineering sessions for a PR retrospective.

For each session you will receive a compact block with:
  - session id (first 12 chars)
  - duration, message count, compaction count, near-done / direction-change counts
  - branches touched
  - the first user prompt (truncated)
  - top tools invoked (with counts)
  - top files edited (with counts)

From that signal, infer *what the session was actually working on* — the feature,
bug fix, refactor, investigation, or workflow. Name concrete components
(file areas, task names, endpoints) when they're visible. Do NOT parrot the
opening prompt; synthesize across the tool mix and file list.

Output rules — THIS IS THE ONLY FORMAT I WILL ACCEPT:
  - Pipe-delimited CSV, no preamble, no trailing prose, no code fences.
  - First line is the header exactly: session_id|summary|work_type
  - Each subsequent line is one session.
  - `summary`: 12-25 words. Start with a past-tense action verb
    (Implemented, Fixed, Debugged, Wired, Investigated, Refactored, Migrated,
    Set up, Hardened, Documented, Diagnosed, Ported, Extended).
  - Name the concrete thing: "TikTok webhook merchant resolution", not "a feature".
  - If the session was diffuse (many unrelated edits), say so: "Mixed:
    <thing A>, <thing B>, <thing C>".
  - Escape any literal pipe in the summary as " / ".
  - `work_type`: one of: feature, bugfix, refactor, infra, debug, docs,
    tests, review, ops, mixed.
  - No quotes, no markdown, no numbering. Exactly one row per input session.
  - Preserve the exact session ids from the input blocks."""


def short_file(path: str) -> str:
    """Strip worktree prefixes so file hints fit in the prompt."""
    if not path:
        return ""
    # Drop everything up to and including the project dir name
    for marker in ("/mcf-amz-tiktok/", "/ecommerce-tools/", "/workspace/"):
        idx = path.find(marker)
        if idx >= 0:
            return path[idx + len(marker):]
    return path


def build_session_block(s: dict[str, Any]) -> str:
    sid = (s.get("id") or "")[:12]
    dur = s.get("duration_hours", 0)
    msgs = s.get("message_count", 0)
    compact = s.get("compaction_events", 0)
    near = s.get("near_done_prompts", 0)
    direction = s.get("direction_changes", 0)
    branches = ", ".join(s.get("branches_seen") or []) or "(none)"
    opener = (s.get("opening_prompt") or "").strip().replace("\n", " ")[:280]

    tools = s.get("tools_used") or {}
    top_tools = sorted(tools.items(), key=lambda kv: kv[1], reverse=True)[:6]
    tools_str = ", ".join(f"{k}:{v}" for k, v in top_tools) or "(none)"

    files = s.get("top_files_edited") or []
    top_files = [f"{short_file(p)}:{c}" for p, c in files[:8]]
    files_str = "; ".join(top_files) or "(none)"

    return (
        f"[{sid}] duration={dur}h msgs={msgs} compacted={compact} "
        f"near_done={near} direction_changes={direction}\n"
        f"  branches: {branches}\n"
        f"  opener: {opener}\n"
        f"  tools: {tools_str}\n"
        f"  files: {files_str}"
    )


def parse_csv_reply(text: str) -> dict[str, tuple[str, str]]:
    """Return {session_id_prefix: (summary, work_type)}.

    Tolerant: skips any preamble, handles stray whitespace, strips code fences.
    """
    # Strip code fences if the model adds them despite instructions.
    text = re.sub(r"^```[a-zA-Z]*\n?|```$", "", text.strip(), flags=re.MULTILINE)

    out: dict[str, tuple[str, str]] = {}
    saw_header = False
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if not saw_header:
            if line.lower().startswith("session_id|"):
                saw_header = True
            continue
        parts = line.split("|", 2)
        if len(parts) < 2:
            continue
        sid = parts[0].strip()
        summary = parts[1].strip() if len(parts) >= 2 else ""
        work_type = parts[2].strip().lower() if len(parts) == 3 else ""
        if sid:
            out[sid] = (summary, work_type)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sessions-json", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="claude-opus-4-7")
    ap.add_argument("--max-tokens", type=int, default=8000)
    args = ap.parse_args()

    path = Path(args.sessions_json)
    payload = json.loads(path.read_text())
    sessions = payload.get("sessions") or []
    if not sessions:
        print("No sessions to summarize.", file=sys.stderr)
        return 1

    blocks = [build_session_block(s) for s in sessions]
    user_msg = (
        f"Summarize the following {len(sessions)} Claude Code sessions. "
        f"Reply only with the pipe-delimited CSV described in your instructions.\n\n"
        + "\n\n".join(blocks)
    )

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    print(
        f"Calling {args.model} with {len(sessions)} sessions "
        f"(~{sum(len(b) for b in blocks):,} chars of session data)...",
        file=sys.stderr,
    )

    with client.messages.stream(
        model=args.model,
        max_tokens=args.max_tokens,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_msg}],
    ) as stream:
        final = stream.get_final_message()

    reply = "".join(
        blk.text for blk in final.content if getattr(blk, "type", None) == "text"
    )

    usage = final.usage
    print(
        f"Tokens — input: {usage.input_tokens}, output: {usage.output_tokens}, "
        f"cache_read: {getattr(usage, 'cache_read_input_tokens', 0)}, "
        f"cache_create: {getattr(usage, 'cache_creation_input_tokens', 0)}",
        file=sys.stderr,
    )

    parsed = parse_csv_reply(reply)
    if not parsed:
        print("ERROR: could not parse any rows from model reply.", file=sys.stderr)
        print("--- raw reply ---", file=sys.stderr)
        print(reply, file=sys.stderr)
        return 2

    matched = 0
    for s in sessions:
        sid = (s.get("id") or "")[:12]
        if sid in parsed:
            summary, work_type = parsed[sid]
            s["summary"] = summary
            s["work_type"] = work_type
            matched += 1

    print(f"Matched summaries for {matched}/{len(sessions)} sessions.", file=sys.stderr)
    if matched < len(sessions):
        missing = [
            (s.get("id") or "")[:12]
            for s in sessions
            if "summary" not in s
        ]
        print(f"Missing: {missing}", file=sys.stderr)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {out}", file=sys.stderr)
    return 0 if matched == len(sessions) else 3


if __name__ == "__main__":
    raise SystemExit(main())
