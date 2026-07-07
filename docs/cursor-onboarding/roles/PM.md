# Product Manager — Quick Guide

**Cursor rule:** `09-multi-role-pm.mdc`  
**Opens when:** You view pipeline files or `docs/**`

## What you can ask (no code required)

- "What does [PipelineName] do?"
- "What inputs and outputs does it accept?"
- "What's the difference between standard and modular?"
- "What must a new engineer deliver before we ship to internal users?"
- "Summarize onboarding steps for a new contributor"

## What to track during rollout

| Signal | Where | Meaning |
|--------|-------|---------|
| Time to first PR | GitHub / Linear | Onboarding speed |
| CI pass rate (first push) | GitHub Actions | Rules + CI working |
| Review cycles per PR | GitHub | Less convention back-and-forth |
| Convention comments trending down | PR reviews | Engineers internalizing patterns |

See `SUCCESS-METRICS.md` for full dashboard.

## What PMs should not do

- Edit `.cursor/rules/` directly — propose via platform lead
- Bypass CI to hit timelines
- Ask engineers to skip tests for v1

## Cursor prompt

```
I'm a PM — explain in plain English, no code. What does [PipelineName] do?
What would a new engineer need to deliver before we could ship this to
internal users?
```

You can also read `ONBOARDING.md` standalone — no Cursor required.
