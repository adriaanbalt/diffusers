# Cursor Governance — Enterprise Onboarding

**Audience:** Platform team, security/compliance, engineering leadership  
**Use:** Approve before lighthouse rollout; review quarterly with rule audit

---

## Purpose

This document defines **what AI may access, what it may modify, and which external integrations are approved** for Cursor-assisted contribution to this codebase. It complements `.cursorignore` (technical enforcement) and project rules (convention teaching).

---

## Privacy and data handling

| Control | Policy |
|---------|--------|
| **Privacy Mode** | Required for production engineering workspaces. Code and prompts are not retained for model training per Cursor enterprise terms. |
| **Indexing** | Project rules, skills, and hooks are plain markdown in git — same access control as source code. |
| **What leaves the repo** | Only what engineers send in Agent/Ask prompts. `.cursorignore` excludes sensitive paths from AI context. |
| **Customer sign-off** | Security reviews Privacy Mode config and `.cursorignore` in Phase 0 before lighthouse install. |

**SA talking point:** Rules don't transmit externally on their own. Privacy Mode + `.cursorignore` are the enterprise trust boundary — not a parallel compliance system.

---

## Approved MCP integrations (Rollout Phase 2+)

Enable only after lighthouse metrics prove rules work. Platform + security approve per connector.

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

AI **must not read or suggest edits** to:

| Path class | Why |
|------------|-----|
| `.github/workflows/*.yml` | CI changes require human review; prevents accidental workflow breakage |
| `setup.py`, `pyproject.toml`, release scripts | Supply chain and release integrity |
| `*.pem`, `*.key`, `.env*`, `secrets/` | Credential exposure |
| `src/diffusers/utils/dummy_*.py` | Generated — edits overwritten |
| Large weights (`*.safetensors`, `*.ckpt`, …) | Context bloat; not needed for convention work |

`.cursorignore` ≠ `.gitignore` — git still tracks CI configs; AI simply cannot modify them without explicit human intent.

---

## Agent guardrails

| Guardrail | Mechanism |
|-----------|-----------|
| No CI/release edits | `.cursorignore` |
| Convention teaching | Project rules (passive, in-editor) |
| Quality nudge after writes | Hook `quality-reminder.py` (Rollout Phase 2; fails open) |
| Hard merge gate | Existing CI — `make quality`, pytest |
| Pre-PR self-review | `.ai/skills/self-review` — same rubric as `@claude` CI reviewer |
| Destructive git ops | Not blocked by hook in v1 — human PR review + branch protection |

Hooks nudge; they do not replace CI or code review.

---

## Upstream vs customer AI docs

| Asset | Owner | Role |
|-------|-------|------|
| `.ai/AGENTS.md` | Diffusers maintainers (upstream) | Agent orientation — style, `make quality`, skill index |
| `.ai/skills/self-review` | Upstream | Pre-PR rubric aligned with `@claude` CI |
| `.cursor/rules/*.mdc` | Platform team (customer) | Glob-scoped conventions — onboarding + multi-role |
| `.cursor/hooks/` | Platform team | Rollout Phase 2 automation |
| `.cursor/skills/` | Platform team | Rollout Phase 3 on-demand workflows |

**Do not duplicate** upstream `AGENTS.md` — complement it with Cursor-native project rules.

---

## Ownership and audit cadence

| Activity | Owner | Cadence |
|----------|-------|---------|
| Rule changes | Platform team via PR | Same PR as convention change |
| `.cursorignore` changes | Platform lead + security | As needed; rare |
| MCP connector approval | Platform + security | Per connector at Phase 2 |
| Rule/skill audit | Platform champion | Quarterly — remove rules unused 3+ months |
| Privacy Mode verification | IT / security | Annual or on Cursor contract renewal |

See also: `ONBOARDING.md`, `.cursor/rules/`, and the SA delivery package in [`docs/cursor-onboarding/`](docs/cursor-onboarding/CUSTOMER-DELIVERY-PACKAGE.md) (`ROLLOUT-PLAYBOOK.md`, `PLATFORM-RUNBOOK.md`).

---

## Interview talking point

> "Governance isn't a slide — it's `.cursorignore` for boundaries, Privacy Mode for enterprise trust, an approved MCP list for Phase 2, and quarterly rule audits so guidance doesn't drift. CI still blocks merge; AI teaches and nudges, it doesn't own production."
