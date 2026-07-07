# Executive Summary — Cursor Onboarding for Convention-Heavy Platform Teams

**Audience:** VP Engineering, platform director, engineering leadership  
**Read time:** 2 minutes

---

## Problem

Platform teams maintaining large internal libraries lose **weeks of productivity per new hire** to convention debt. Tribal knowledge lives in PR comments and senior engineers' heads — not in tooling new contributors can access on day one. Review cycles burn on file placement, import registration, and test scaffolding instead of correctness and design.

## Solution

Embed **Cursor project rules** and a **guided first-contribution workflow** directly in the repository — alongside existing CI guardrails. New engineers get real-time guidance while coding; the platform team owns the rules in git; PM, QA, DevOps, and reviewers get scoped guidance without writing code.

## What we deliver

| Component | Outcome |
|-----------|---------|
| 10 scoped Cursor rules | Encode institutional knowledge — file structure, patterns, anti-patterns |
| Onboarding scaffold | Progressive first-contribution workflow (discovery → structure → implement → validate) |
| `.cursorignore` boundaries | AI stays out of CI configs, secrets, and release tooling |
| Integration with existing CI | No parallel enforcement system — team's `make quality` and pytest remain the merge gate |
| Rollout playbook + metrics | Phased adoption with measurable success criteria |

## Expected impact

| Metric | Typical baseline | Target (90 days) |
|--------|------------------|------------------|
| Time to first merged PR (new hire) | 3–4 weeks | 1.5–2 weeks |
| Convention-related review comments | High in first 2 PRs | ↓ 50%+ by PR 3 |
| CI pass rate on first push | Variable | ↑ toward team average within 30 days |

*Illustrative — calibrate in discovery with customer's actual ramp data.*

## Investment

| Phase | Duration | Cursor / SA involvement |
|-------|----------|-------------------------|
| Discovery | 2–3 days | SA interviews joiners, mines PR patterns |
| Lighthouse (1 squad) | 2 weeks | SA embedded — install rules, enablement sessions |
| Expand (2–3 teams) | 2–3 weeks | SA + platform champions — role enablement |
| Operationalize | Ongoing | Platform team owns via runbook; SA quarterly check-in |

## What we deliberately did not build

- Fully autonomous code generation (trust must be earned incrementally)
- Custom validator duplicating CI (single source of truth in rules + existing gates)
- Ticketing MCP integrations (customer-specific; week 2+ if needed)

## Ask

1. Sponsor one **lighthouse squad** (platform team + 3–5 new or recent hires)
2. Assign a **platform owner** for rule maintenance
3. Agree on **3 success metrics** from `SUCCESS-METRICS.md` before rollout

---

*Reference implementation: HuggingFace diffusers onboarding solution in this repository.*
