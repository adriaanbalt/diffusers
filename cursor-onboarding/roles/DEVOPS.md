# DevOps / Platform — Quick Guide

**Cursor rule:** `08-multi-role-ops.mdc`  
**Opens when:** You edit `.github/**`, `Makefile`, `setup.py`, `.cursorignore`

## CI path (diffusers example)

1. `make quality` — style, imports, lint (~30s)
2. Fast pytest on changed paths
3. GPU tests — separate workflow when needed

## What Cursor rules catch vs CI

| Layer | Catches | Blocks merge? |
|-------|---------|---------------|
| Cursor rules + agent | Conventions, patterns, structural gaps | No — advises |
| CI | Style, lint, tests | **Yes** |

## Protected paths (`.cursorignore`)

AI must not modify without human review:

- `.github/workflows/`
- `setup.py`, `pyproject.toml`
- Secrets, release scripts

## Cursor prompt

```
I'm on the platform team. Walk me through CI stages for a new pipeline PR,
what Cursor rules catch vs what only CI or human review can catch,
and which files AI should never modify.
```

## Ownership

See `PLATFORM-RUNBOOK.md` for rule maintenance after SA handoff.
