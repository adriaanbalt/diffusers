# Platform Runbook — Owning Cursor Onboarding Rules

**Audience:** Platform team, developer experience, internal tools  
**Use:** Day-to-day ownership after SA handoff (Req #4)

---

## What you own

| Asset | Location | Change frequency |
|-------|----------|------------------|
| Cursor rules | `.cursor/rules/*.mdc` | When conventions change |
| Hooks | `.cursor/hooks.json`, `.cursor/hooks/` | Rollout Phase 2 — after lighthouse metrics |
| Skills | `.cursor/skills/*/SKILL.md` | Rollout Phase 3 — on-demand workflows |
| AI boundaries | `.cursorignore` | Rarely — security review required |
| Engineer guide | `ONBOARDING.md` (repo root) | When workflow changes |
| Governance | `GOVERNANCE.md` (repo root) | Privacy, MCP approval, guardrails — security review |
| Role guides | `cursor-onboarding/roles/*.md` | When role workflows change |

**You do not own:** Cursor product settings, user licenses, org-wide MCP configs — coordinate with IT/admin.

---

## Rule file anatomy

Each `.mdc` file has YAML frontmatter:

```yaml
---
description: One-line summary for Cursor
globs: ["src/yourlib/**"]   # When rule activates
alwaysApply: false          # true only for scaffold/onboarding
---
```

| Field | Guidance |
|-------|----------|
| `description` | Clear enough for engineers to understand scope |
| `globs` | Narrow — avoid activating 5 rules on every file |
| `alwaysApply` | Use sparingly; only for onboarding scaffold |

---

## How to change a convention

**Definition of done for any convention change:**

1. Code change implements new pattern
2. Relevant `.mdc` rule updated in the **same PR**
3. `ONBOARDING.md` updated if workflow affected
4. Enablement note in team channel if breaking change
5. Optional: add/update `examples/` file

**Never:** Change convention in code without updating rules — creates drift and erodes trust.

---

## How to add a new rule

1. Identify pattern from ≥3 PR review comments or CI failures
2. Create `.cursor/rules/NN-descriptive-name.mdc` (use next number)
3. Set `globs` to minimum scope needed
4. Include WHY, not just WHAT — engineers should learn the pattern
5. PR review by senior maintainer + one recent joiner ("would this have helped you?")
6. Merge with at least one example in `examples/` if non-obvious

---

## How to remove a rule

Remove if:
- Pattern hasn't caught a meaningful violation in 3 months
- Convention deprecated in codebase
- Rule duplicates CI check with no educational value

Archive in PR description — don't silent-delete.

---

## Boundaries (`.cursorignore`)

**Protected paths — require human review for any change:**

- `.github/workflows/` — CI definitions
- `setup.py`, `pyproject.toml` — package metadata
- `*.pem`, `*.key`, `.env*` — secrets
- `scripts/release_*` — release tooling

**Process to modify `.cursorignore`:** Platform lead + security review. Document rationale in PR.

---

## CI integration

**Principle:** Rules advise in the editor; **existing CI enforces at merge.**

| Layer | Tool | Blocks merge? |
|-------|------|---------------|
| Real-time | Cursor rules + agent | No |
| Local | `make quality`, pytest (engineer's machine) | No — discipline |
| CI | `pr_tests.yml` (or customer equivalent) | **Yes** |

**Do not** duplicate convention checks in a custom script unless CI cannot express the check — drift between rules and script erodes trust.

---

## Enablement cadence

| Event | When | Format |
|-------|------|--------|
| New hire onboarding | Day 1 | Point to `ONBOARDING.md`; 30 min Cursor walkthrough |
| Rule change | Same week as PR merge | Slack post + link to diff |
| Quarterly review | Every 3 months | 30 min — prune rules, review metrics |
| Role session | On expand to new team | Use `cursor-onboarding/roles/*.md` as handout |

---

## Hooks and skills (Rollout Phases 2–3)

| Surface | When to enable | What it does |
|---------|----------------|--------------|
| **Hooks** | After lighthouse metrics prove rules work | `quality-reminder.py` nudges `make quality` after pipeline/model writes — fails open, no custom validator |
| **Skills** | When engineers graduate past scaffold | `implement-contribution` — on-demand Phases 3–6; complements diffusers `.ai/skills/` |

Enable hooks in `.cursor/hooks.json` only after the pilot squad is comfortable with rules. Add skills when engineers repeatedly ask for implementation walkthroughs post-scaffold.

---

## Escalation to Cursor SA

| Situation | Action |
|-----------|--------|
| Rule consistently wrong or ignored | SA review — is pattern wrong or rule poorly written? |
| Cursor product limitation blocks workflow | SA files feedback to Product |
| Adoption metrics flat after 90 days | SA recovery session — see `ROLLOUT-PLAYBOOK.md` |
| New monorepo / major restructure | SA discovery subset for new globs |

---

## Interview talking point

> "I don't want to be the only person who can edit these. This runbook is how the platform team owns rules the same way they own CI configs — PR-reviewed, version-controlled, definition of done includes doc updates."
