# Rollout Playbook — Cursor Onboarding at Scale

**Audience:** Solutions Architect, platform lead, ADM  
**Use:** Phased deployment plan for a convention-heavy internal library

---

## Principles

1. **Start narrow** — one workflow ("add a pipeline"), one squad, prove value
2. **Integrate, don't replace** — rules advise; existing CI enforces
3. **Team owns it** — SA installs; platform team maintains
4. **Measure from day one** — baseline metrics before lighthouse launch
5. **Exit velocity** — goal is engineers internalizing patterns, not permanent rule dependence

---

## Phase 0 — Discovery (2–3 days)

**Goal:** Validate pain, identify patterns to encode, align stakeholders.

| Activity | Owner | Output |
|----------|-------|--------|
| Interview 2–3 recent joiners | SA | Top 10 day-one mistakes list |
| Mine last 20 onboarding PRs for review comments | SA + platform | Convention violation categories |
| Read CONTRIBUTING / internal docs | SA | Gap analysis vs tribal knowledge |
| Map SDLC — plan, build, review, test, deploy | SA | Where rules vs CI vs human review fit |
| Align on lighthouse squad + success metrics | SA + ADM + platform lead | Signed charter (see `EXECUTIVE-SUMMARY.md`) |

**Exit criteria:** Prioritized pattern list, lighthouse team named, metrics baseline captured.

---

## Phase 1 — Lighthouse (2 weeks)

**Goal:** One squad ships a first contribution using rules + scaffold with SA embedded.

| Week | Activities |
|------|------------|
| **1** | Install `.cursor/rules/`, `.cursorignore`, `ONBOARDING.md` via PR; platform team review |
| **1** | Enablement session 1 (60 min): rules overview, live scaffold walkthrough |
| **1–2** | Pair on first real contribution — SA observes, does not drive |
| **2** | Enablement session 2 (45 min): mistake-catching, reviewer checklist, CI path |
| **2** | Retrospective — what rules caught, what missed, what to add |

**Deliverables:**
- Merged rules PR in customer repo
- At least one engineer through Phases 1–6 with rules
- Feedback log for rule gaps

**Exit criteria:** Lighthouse engineer opens PR with ≤ average convention review comments for a first-timer.

---

## Phase 2 — Expand (2–3 weeks)

**Goal:** Roll to 2–3 adjacent teams; enable non-engineer roles.

| Activity | Detail |
|----------|--------|
| Enable hooks | Turn on `.cursor/hooks.json` — `quality-reminder.py` nudges `make quality` after pipeline/model writes |
| Role enablement sessions | Distribute `cursor-onboarding/roles/*.md` — PM, QA, reviewer, DevOps (30 min each) |
| Enable skills | `.cursor/skills/implement-contribution/` — on-demand Phases 3–6 after skeleton exists |
| Champion program | Identify 1 staff engineer per team as rule maintainer |
| Expand rule coverage | Add patterns discovered in lighthouse retro |
| Optional: `@docs` indexing | Expose internal API docs as agent context if customer uses doc portal |

**Exit criteria:** 3 teams using rules; platform owner can add a rule without SA.

---

## Phase 3 — Operationalize (week 5–6)

**Goal:** Customer runs without SA embedded; metrics reviewed monthly.

| Activity | Detail |
|----------|--------|
| Handoff to platform team | Walk through `PLATFORM-RUNBOOK.md` |
| Metrics dashboard | Track metrics from `SUCCESS-METRICS.md` |
| Rule maintenance cadence | Quarterly review; remove unused rules |
| Executive readout | Present 90-day results using `EXECUTIVE-SUMMARY.md` template |

**Exit criteria:** Platform team owns rule PRs; SA moves to quarterly advisory.

---

## Phase 4 — Scale (ongoing)

| Trigger | Action |
|---------|--------|
| New library or monorepo area | Discovery subset → new rule files scoped by glob |
| Convention change | Rule updated in same PR as code change |
| Adoption stalls | Recovery plan — see below |
| Major Cursor release | Re-test rules; update globs/features if needed |

---

## Recovery plan (adoption stalls)

**Symptoms:** Low Cursor usage, rules ignored, CI still catching same violations, leadership skepticism.

| Step | Action |
|------|--------|
| 1 | Re-baseline metrics — is problem adoption or rule quality? |
| 2 | Interview 2 engineers who stopped using it — friction points |
| 3 | Simplify — remove rules that haven't caught violations in 90 days |
| 4 | Re-run lighthouse pairing session with fresh squad |
| 5 | Executive re-alignment — tie back to time-to-first-PR ROI |

---

## RACI

| Task | SA | Platform team | Eng lead | AE |
|------|-----|---------------|----------|-----|
| Discovery | **R** | C | I | I |
| Rules content | **R** | **A** | C | I |
| Rules PR merge | C | **R/A** | I | I |
| Enablement sessions | **R** | C | I | I |
| Metrics tracking | C | **R** | **A** | I |
| Expansion decision | C | C | **A** | **R** |
| Executive readout | **R** | C | **A** | C |

*R = Responsible, A = Accountable, C = Consulted, I = Informed*

---

## Interview talking point

> "Week 1 is discovery — I don't install rules until I've validated patterns with recent joiners. Week 2–3 is lighthouse with one squad. By week 6 the platform team owns it via the runbook. I'm not trying to be permanent staff augmentation."
