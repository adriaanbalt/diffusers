# New Engineer Onboarding Guide

Welcome to the diffusers platform team. This guide gets you from zero to your first merged contribution using Cursor as your development environment.

> **Not using Cursor?** Follow the same steps — rules are additive. `make quality`, pytest, and human review are the merge gates for everyone.

## Before you start

1. **Clone the repository**
   ```bash
   git clone https://github.com/huggingface/diffusers.git
   cd diffusers
   pip install -e ".[dev,test]"
   ```

2. **Open in Cursor** — `.cursor/rules/` activates automatically and guides your workflow

3. **Verify your setup**
   ```bash
   make style    # Should complete without errors
   make quality  # Should complete without errors
   python -c "import diffusers; print(diffusers.__version__)"
   ```

4. **Read governance once** — [`GOVERNANCE.md`](GOVERNANCE.md) (Privacy Mode, approved MCP, AI boundaries)

## Your first contribution: Add a new pipeline

This is the most common first contribution. The rules guide you step-by-step; here's the overview:

### Step 1: Understand what you're building

Ask yourself:
- What model am I integrating? (Get the reference repo URL)
- Do I have a runnable inference script?
- Should this be modular (recommended) or standard pipeline?

### Step 2: Let Cursor scaffold the structure

In Cursor, type: **"I want to add a new pipeline called [model-name]"**

Use **Plan mode** for discovery (Phase 1), then **Agent mode** for file creation (Phase 2). The `04-onboarding-scaffold.mdc` rule walks you through:
1. Gathering context before any files are created
2. Creating files in the correct locations
3. Registering imports in `__init__.py` files
4. Implementing the model with correct patterns
5. Converting weights
6. Writing tests and running `make quality`

For Phases 3–6 on demand, invoke the **`implement-contribution`** skill (`.cursor/skills/`).

### Step 3: Follow convention guidance

As you write code, rules activate based on which files you're editing:
- `src/diffusers/models/` → `02-model-conventions.mdc`
- `src/diffusers/pipelines/` or `modular_pipelines/` → `01-pipeline-conventions.mdc`
- `tests/` → `03-testing-standards.mdc`

Upstream diffusers also ships `.ai/AGENTS.md` and `.ai/skills/` — use `self-review` before PR; it mirrors the `@claude` CI reviewer rubric.

### Step 4: Validate before submitting

```bash
make style && make quality
python -m pytest tests/pipelines/<your-model>/ -x
python -m pytest tests/models/transformers/test_models_transformer_<your-model>.py -x
```

Ask the agent: **"Review this file for convention violations"** before opening the PR.

After rollout Phase 2, a **hook** (`.cursor/hooks/quality-reminder.py`) nudges these gates when pipeline files are written.

### Step 5: Submit your PR

- Title format: `Add [ModelName] pipeline`
- Include: model description, reference repo link, parity test results
- Do NOT include: LoRA support, slow tests, quantization (follow-up PRs)

## How this team uses Cursor

| Situation | Mode | Why |
|-----------|------|-----|
| "I want to add a pipeline" | **Plan** → **Agent** | Discovery first; engineer approves diffs |
| "What does this pipeline do?" (PM) | **Ask** | Explain only — no file edits |
| "Review this PR" | **Agent** + reviewer rule | Checklist from `07-multi-role-reviewer.mdc` |
| Large ambiguous refactor | **Plan** | Confirm scope before edits |

**Agents may touch:** `src/`, `tests/`, `docs/source/en/api/`, `scripts/convert_*`  
**Agents must not touch:** CI workflows, `setup.py`, secrets, release scripts — see `.cursorignore`

## Common patterns by role

### ML researcher adding a model

Focus on parity, weight conversion, model implementation. See `06-multi-role-researcher.mdc`.

### Code reviewer

Checklist in `07-multi-role-reviewer.mdc` — architecture → conventions → tests → style.

### CI / platform (DevOps)

See `08-multi-role-ops.mdc` for CI stages and protected paths.

## Key things to remember

1. **Modular pipelines are the default** for new contributions
2. **Register imports in BOTH `__init__.py` files** — the #1 mistake
3. **No einops, no float64, no torch.empty** — hard blockers
4. **Tiny test configs** — 2 layers, 8-dim heads, 16px resolution
5. **Test models on `hf-internal-testing/`** — never personal repos
6. **No LoRA in initial PR** — follow-up PR

## Getting help

- `.cursor/rules/` — topic-specific guidance
- `05-code-review.mdc` — anti-patterns with fixes
- Ask Cursor: "What's the convention for [X]?"
