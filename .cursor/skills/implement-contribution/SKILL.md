---
name: implement-contribution
description: >
  Use when an engineer finished onboarding scaffold (file structure exists) and needs to
  implement the model, pipeline, and tests. Invoke on demand — e.g. "/implement-contribution
  slug solarvision". For validation gates before PR, use validate-contribution. Complements
  04-onboarding-scaffold.mdc and diffusers .ai/skills/model-integration.
---

# Implement Contribution (Phases 3–5)

**Rollout Phase 3 skill** — on-demand playbook after the skeleton exists.

Rules (`04-onboarding-scaffold.mdc`) teach passively during editing. This skill runs
**implementation and tests** when the engineer knows what they're building.

## Execution contract

Execute Phases 3–5 sequentially to completion. Do not stop or ask between phases. Do not run
`make quality`, `make style`, or pytest gates — that is `validate-contribution`. If you hit
a blocker that requires real assets (weights, external repos), scaffold what you can, note
the deferral, and continue to the next phase.

## When to invoke

- Scaffold is done (slug confirmed, `__init__.py` imports registered)
- User says: "implement the model", "finish the pipeline", "walk me through Phases 3–5"
- Engineer graduated past discovery — they know *what* they're building

## Before starting

If the user provides a slug in the invocation message, use it directly. Only ask if missing.

Confirm:

1. **Slug** — e.g. `solarvision` (directory names, test paths, conversion script)
2. **Modular vs standard** — default modular
3. **Reference pipeline** — e.g. `@folder modular_pipelines/flux2/` for patterns

## Phase 3 — Implement model

Follow `02-model-conventions.mdc`:

1. Implement transformer with `ModelMixin` + `ConfigMixin` + `@register_to_config`
2. Attention processor pattern + `dispatch_attention_fn`
3. Gradient checkpointing support
4. Write `scripts/convert_<slug>_to_diffusers.py` — if a checkpoint is available, verify parity (< 1e-3). If no checkpoint exists, scaffold the full script structure (argparse, key-renaming helpers, save logic) and mark parity verification as deferred.
5. Reuse existing scheduler when possible

## Phase 4 — Implement pipeline

**Modular (default)** — build in order:

1. `decoders.py` → 2. `encoders.py` → 3. `before_denoise.py` → 4. `denoise.py`
5. `modular_blocks_<slug>.py` → 6. `modular_pipeline.py`

Follow `01-pipeline-conventions.mdc`. Never subclass another pipeline.

## Phase 5 — Write tests

Follow `03-testing-standards.mdc`:

1. Pipeline tests: `PipelineTesterMixin`, tiny configs in `get_dummy_components`
2. Model tests: `python utils/generate_model_tests.py`, fill TODOs
3. Skip LoRA, `@slow`, and integration tests in the initial PR

## After Phase 5 — invoke validate-contribution

When implementation and tests are in place, stop. Say:

> "Implementation and tests are ready. Invoke **validate-contribution** to run quality gates before PR."

Do not run `make style`, `make quality`, or pytest. Do not declare the contribution complete.

## How this fits the stack

| Layer | Role |
|-------|------|
| **Rules** (Phase 1 rollout) | Passive conventions — always on while editing |
| **Hook** (Phase 2 rollout) | `.cursor/hooks/quality-reminder.py` — nudge validation after writes |
| **This skill** (Phase 3 rollout) | Phases 3–5: implement model, pipeline, tests |
| **`validate-contribution`** | Pre-PR gates: `make quality` + pytest fix loop |
| **`.ai/skills/model-integration`** | Upstream diffusers reference — read during discovery |
| **CI** | `pr_tests.yml` — hard merge gate |

## Do not

- Re-run Phase 1 discovery if the skeleton already exists
- Run validation gates (that is `validate-contribution`)
- Duplicate full rule text — cite the relevant `.mdc` file
- Replace CI with custom validators
