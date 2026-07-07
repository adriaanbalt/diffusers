# Customer Delivery Package

What a Cursor Solutions Architect leaves behind after a lighthouse engagement — beyond the demo artifact in the repo.

**Location:** `cursor-onboarding/` — separate from HuggingFace library docs in `docs/source/en/`.

---

## Two layers (both in this repo)

| Layer | What it is | Where in repo |
|-------|------------|---------------|
| **Lighthouse artifact** | Rules, hooks, skills, `.cursorignore`, [`ONBOARDING.md`](../../ONBOARDING.md), [`GOVERNANCE.md`](../../GOVERNANCE.md) | Repo root + `.cursor/` |
| **SA delivery docs** | Rollout, runbooks, metrics, role guides | **`cursor-onboarding/`** (this folder) |

**What you demo in 45 minutes** = lighthouse artifact (Blocks 3–7).  
**What proves SA thinking** = this package (Block 9 / flex).

---

## Package contents

| Document | Audience | Purpose |
|----------|----------|---------|
| [`EXECUTIVE-SUMMARY.md`](EXECUTIVE-SUMMARY.md) | VP Eng, platform director | Problem, solution, ROI, ask |
| [`ROLLOUT-PLAYBOOK.md`](ROLLOUT-PLAYBOOK.md) | SA, platform lead, ADM | Phased deployment over 4–6 weeks |
| [`PLATFORM-RUNBOOK.md`](PLATFORM-RUNBOOK.md) | Platform / developer experience team | Own and evolve rules without SA |
| [`SUCCESS-METRICS.md`](SUCCESS-METRICS.md) | PM, leadership, SA | Measure adoption and impact |
| [`ONBOARDING.md`](../../ONBOARDING.md) | New engineers | Self-serve first contribution (repo root) |
| [`GOVERNANCE.md`](../../GOVERNANCE.md) | Platform, security, leadership | Privacy Mode, approved MCP, AI guardrails (repo root) |
| [`roles/`](roles/) | PM, QA, reviewer, researcher, DevOps | Role-specific one-pagers |
| `.cursor/rules/` + `.cursorignore` | All engineering | Conventions (Rollout Phase 1) |
| `.cursor/hooks/` | Platform team | Quality nudge after writes (Rollout Phase 2) |
| `.cursor/skills/` | Engineers on demand | Phases 3–6 playbook (Rollout Phase 3) |

---

## How this maps to the interview requirements

| Req | Lighthouse artifact | SA delivery layer |
|-----|---------------------|-------------------|
| 1 Scaffold | `04-onboarding-scaffold.mdc`, Phase 1–2 demo | Rollout Phase 1 — lighthouse squad |
| 2 Catch mistakes | Rules + agent review | Metrics — violation rate trending down |
| 3 CI/deploy | `pr_tests.yml`, `.cursorignore`, `GOVERNANCE.md` | Platform runbook — CI integration |
| 4 Maintainable | Rules in git | Runbook — rule change process |
| 5 Multi-role | Rules `06`–`09` | Role one-pagers + enablement sessions |

---

## Interview talking point

> "The rules are the engine. This folder is how I'd deploy it at a real customer — phased rollout, platform ownership, success metrics, and role enablement so adoption scales without me embedded forever. We keep it out of `docs/source/en/` so it doesn't collide with upstream library documentation."
