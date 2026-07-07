#!/usr/bin/env python3
"""
Rollout Phase 2 hook: nudge engineers toward validate-contribution after pipeline/model
edits (Agent Write or StrReplace).

Fails open — never blocks edits. Points to validate-contribution skill and existing CI
commands (make quality, pytest), not a custom convention validator.

Hook wiring:
- afterFileEdit / postToolUse: mark a tracked edit and try additional_context injection
- stop: if a tracked edit happened this turn, auto-submit a visible follow-up reminder
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

TRACKED_PATH_FRAGMENTS = (
    "src/diffusers/pipelines/",
    "src/diffusers/modular_pipelines/",
    "src/diffusers/models/",
    "tests/pipelines/",
    "tests/models/",
    "tests/modular_pipelines/",
    "docs/source/en/_toctree.yml",
    "docs/source/en/api/",
)

REMINDER = (
    "Pipeline, model, or API doc file was just written. Before opening a PR, invoke "
    "**validate-contribution** (`.cursor/skills/validate-contribution/SKILL.md`) to run "
    "`make style`, `make quality`, repository consistency checks, and pytest."
)

FOLLOWUP = (
    "Quality gate reminder: invoke /validate-contribution before you open a PR."
)

PENDING_FLAG = Path(__file__).resolve().parent / ".quality-reminder-pending"


def _extract_path(payload: dict) -> str:
    for key in ("file_path", "path", "file"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value.replace("\\", "/")

    for nested_key in ("tool_input", "arguments", "input"):
        nested = payload.get(nested_key)
        if not isinstance(nested, dict):
            continue
        for key in ("file_path", "path", "file", "target_file"):
            value = nested.get(key)
            if isinstance(value, str) and value:
                return value.replace("\\", "/")

    tool_output = payload.get("tool_output")
    if isinstance(tool_output, str) and tool_output:
        try:
            parsed = json.loads(tool_output)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, dict):
            nested_path = _extract_path(parsed)
            if nested_path:
                return nested_path

    return ""


def _is_tracked(path: str) -> bool:
    return bool(path) and any(fragment in path for fragment in TRACKED_PATH_FRAGMENTS)


def _handle_stop(payload: dict) -> None:
    if payload.get("status") != "completed":
        return
    if not PENDING_FLAG.exists():
        return

    PENDING_FLAG.unlink(missing_ok=True)
    json.dump({"followup_message": FOLLOWUP}, sys.stdout)


def _handle_edit(payload: dict) -> None:
    path = _extract_path(payload)
    if not _is_tracked(path):
        return

    PENDING_FLAG.write_text(path, encoding="utf-8")
    json.dump({"additional_context": REMINDER}, sys.stdout)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    if payload.get("hook_event_name") == "stop" or "status" in payload:
        _handle_stop(payload)
    else:
        _handle_edit(payload)

    sys.exit(0)


if __name__ == "__main__":
    main()
