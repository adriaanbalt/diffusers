# Cursor Governance — Enterprise Onboarding

**Audience:** Platform team, security/compliance, engineering leadership  
**Use:** Approve before lighthouse rollout; review quarterly with rule audit

---

## Purpose

This document defines **what AI may access, what it may modify, and which external integrations are approved** for Cursor-assisted contribution to this codebase. It complements `.cursorignore` (context boundaries) and project rules (convention teaching).

**Out of scope here:** engineer workflow (scaffold → implement → validate) lives in `ONBOARDING.md`; multi-role usage lives in role rules `06`–`09` and `cursor-onboarding/roles/`.

---

## Privacy and data handling

| Control | Policy |
|---------|--------|
| **Privacy Mode** | Required for production engineering workspaces. Code and prompts are not retained for model training per Cursor enterprise terms. |
| **Indexing** | Project rules, skills, and hooks are plain markdown in git — same access control as source code. |
| **What leaves the repo** | Only what engineers send in Agent/Ask prompts. `.cursorignore` excludes sensitive paths from default AI context. |
| **Customer sign-off** | Security reviews Privacy Mode config and `.cursorignore` in Phase 0 before lighthouse install. |

**SA talking point:** Rules don't transmit externally on their own. Privacy Mode + `.cursorignore` are the enterprise trust boundary — not a parallel compliance system.

**Lighthouse KPIs:** Baseline and review cadence in [`cursor-onboarding/SUCCESS-METRICS.md`](cursor-onboarding/SUCCESS-METRICS.md); rollout phases in [`cursor-onboarding/ROLLOUT-PLAYBOOK.md`](cursor-onboarding/ROLLOUT-PLAYBOOK.md).

---

## Approved MCP integrations (MCP rollout — after lighthouse)

Enable only after lighthouse metrics prove rules work. Platform + security approve per connector.  
*(Distinct from hook rollout — see Agent guardrails below.)*

| Connector | Use case | Priority | Notes |
|-----------|----------|----------|-------|
| **Linear / Jira** | Scaffold Phase 1 — ticket context | High | Read-only task metadata; no arbitrary repo dump |
| **GitHub** | PR status, review comments, reference repos | High | CI status after push; team blocking patterns |
| **Notion / Confluence** | Internal wiki if CONTRIBUTING.md is thin | Medium | Convention lookups — rules remain source of truth |
| **Sentry** | Production errors tied to pipeline under review | Low | Stretch — post-onboarding |
| **Datadog** | Not in v1 | — | Defer unless customer explicitly requests |

**Not approved by default:** connectors that pull full production databases, arbitrary internal repos, or credential stores without scoped OAuth and security review.

---

## `.cursorignore` rationale

By default, AI **should not receive context from or be steered toward editing**:

| Path class | Why |
|------------|-----|
| `.github/workflows/*.yml` | CI changes require human review; prevents accidental workflow breakage |
| `setup.py`, `pyproject.toml`, release scripts | Supply chain and release integrity |
| `*.pem`, `*.key`, `.env*`, `secrets/` | Credential exposure |
| `src/diffusers/utils/dummy_*.py` | Generated — edits overwritten |
| Large weights (`*.safetensors`, `*.ckpt`, …) | Context bloat; not needed for convention work |

`.cursorignore` ≠ `.gitignore` — git still tracks CI configs. Excluded paths are omitted from default Agent context; **policy** requires human review before any CI or release change (including if an engineer explicitly `@file`s a protected path).

---

## Multi-audience (PM, QA, DevOps)

Governance defines **boundaries and approval** — not role-specific workflows.

| Audience | Mechanism | This doc covers |
|----------|-----------|-----------------|
| **Engineers** | Rules `00`–`05`, scaffold `04`, skills | Boundaries only — workflow in `ONBOARDING.md` |
| **Researchers** | Rule `06-multi-role-researcher.mdc` | — |
| **Reviewers** | Rule `07-multi-role-reviewer.mdc` | — |
| **DevOps / platform** | Rule `08-multi-role-ops.mdc` | CI boundaries, `.cursorignore`, MCP policy |
| **PM** | Rule `09-multi-role-pm.mdc` | — |
| **QA** | Rule `03-testing-standards.mdc` + testing prompts in delivery package | — |

One repo, different globs and prompts — not separate configs per role.

---

## Agent guardrails

| Guardrail | Mechanism |
|-----------|-----------|
| No CI/release edits (default) | `.cursorignore` + branch protection |
| Convention teaching | Project rules (passive, in-editor) |
| Anti-patterns / review checklist | Rule `05-code-review.mdc` |
| Quality nudge after writes | Hook `quality-reminder.py` (hook rollout; fails open) → points to `validate-contribution` |
| Implementation playbook | Skill `implement-contribution` — model, pipeline, tests (Phases 3–5) |
| Mechanical pre-PR gates | Skill `validate-contribution` — `make style`, `make quality`, slug pytest, fix loop |
| Rubric self-review | `.ai/skills/self-review` (upstream) — same spirit as `@claude` CI reviewer |
| Hard merge gate | Existing CI — `pr_tests.yml`, `make quality`, pytest |
| Destructive git ops | Not blocked by hook in v1 — human PR review + branch protection |

**Two layers before merge:** `validate-contribution` runs the same mechanical gates as CI; `self-review` + human reviewer catch architecture and convention issues rules cannot encode.

Hooks nudge; skills guide; CI enforces. None replace code review.

---

## Upstream vs customer AI docs

| Asset | Owner | Role |
|-------|-------|------|
| `.ai/AGENTS.md` | Diffusers maintainers (upstream) | Agent orientation — style, `make quality`, skill index |
| `.ai/skills/self-review` | Upstream | Pre-PR rubric aligned with `@claude` CI |
| `.cursor/rules/*.mdc` | Platform team (customer) | Glob-scoped conventions — onboarding + multi-role |
| `.cursor/hooks/` | Platform team | Hook rollout — post-write quality nudge |
| `.cursor/skills/implement-contribution` | Platform team | On-demand implementation (Phases 3–5) |
| `.cursor/skills/validate-contribution` | Platform team | On-demand pre-PR validation (mechanical gates) |

**Do not duplicate** upstream `AGENTS.md` — complement it with Cursor-native project rules and skills.

---

## Ownership and audit cadence

| Activity | Owner | Cadence |
|----------|-------|---------|
| Rule changes | Platform team via PR | Same PR as convention change |
| `.cursorignore` changes | Platform lead + security | As needed; rare |
| MCP connector approval | Platform + security | Per connector at MCP rollout |
| Rule/skill audit | Platform champion | Quarterly — remove rules unused 3+ months |
| Lighthouse metrics review | Platform lead + SA | 30/60/90 days — see `SUCCESS-METRICS.md` |
| Privacy Mode verification | IT / security | Annual or on Cursor contract renewal |

See also: `ONBOARDING.md`, `.cursor/rules/`, and the SA delivery package in [`cursor-onboarding/`](cursor-onboarding/CUSTOMER-DELIVERY-PACKAGE.md) (`ROLLOUT-PLAYBOOK.md`, `PLATFORM-RUNBOOK.md`, `SUCCESS-METRICS.md`).
