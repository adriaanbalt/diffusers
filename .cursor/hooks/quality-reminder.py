#!/usr/bin/env python3
"""
Rollout Phase 2 hook: nudge engineers toward validate-contribution after pipeline/model edits.

Fails open — never blocks edits. Points to validate-contribution skill and existing CI
commands (make quality, pytest), not a custom convention validator.
"""
from __future__ import annotations

import json
import sys

TRACKED_PATH_FRAGMENTS = (
    "src/diffusers/pipelines/",
    "src/diffusers/modular_pipelines/",
    "src/diffusers/models/",
    "tests/pipelines/",
    "tests/models/",
    "tests/modular_pipelines/",
)

REMINDER = (
    "Pipeline or model file was just written. Before opening a PR, invoke "
    "**validate-contribution** (`.cursor/skills/validate-contribution/SKILL.md`) to run "
    "`make style`, `make quality`, and pytest with the fix-and-re-run loop."
)


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

    return ""


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    path = _extract_path(payload)
    if not path or not any(fragment in path for fragment in TRACKED_PATH_FRAGMENTS):
        sys.exit(0)

    json.dump(
        {
            "additional_context": REMINDER,
            "user_message": (
                "Quality gate reminder: invoke /validate-contribution before you open a PR."
            ),
        },
        sys.stdout,
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
