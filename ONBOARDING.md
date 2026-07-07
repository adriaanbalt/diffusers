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
6. Writing tests and docs

For Phases 3–6 on demand, invoke the **`implement-contribution`** skill (`.cursor/skills/`).

### Step 3: Follow convention guidance

As you write code, rules activate based on which files you're editing:
- `src/diffusers/models/` → `02-model-conventions.mdc`
- `src/diffusers/pipelines/` or `modular_pipelines/` → `01-pipeline-conventions.mdc`
- `tests/` → `03-testing-standards.mdc`
- Any review pass → `05-code-review.mdc` (anti-patterns) and `07-multi-role-reviewer.mdc` (checklist)

### Step 4: Validate before submitting

Run these in order after Phases 3–6:

**1. Convention review** — catches issues pytest won't (einops, missing `__init__.py` registration, modular anti-patterns). In Cursor, ask the agent:

```
Review slug <your-model> for convention violations. Use the checklists in
05-code-review.mdc and 07-multi-role-reviewer.mdc — architecture first, then
conventions, then tests. List blocking issues vs warnings. Report only; do not edit.
```

Fix blocking issues before running mechanical gates.

**2. Mechanical validation** — invoke **`validate-contribution`** (`.cursor/skills/`) — e.g. `/validate-contribution slug <your-model>`. It runs `make style`, `make quality`, repository consistency checks, slug-scoped pytest, and confirms a clean working tree.

Manual equivalent (non-Cursor or quick reference):

```bash
make style && make quality
make fix-copies && python utils/check_copies.py && python utils/check_dummies.py
python -m pytest tests/modular_pipelines/<your-model>/ -x    # modular
python -m pytest tests/pipelines/<your-model>/ -x            # standard
python -m pytest tests/models/transformers/test_models_transformer_<your-model>.py -x
```

See the `validate-contribution` skill for the full fix loop and known-failure tables.

**3. Upstream self-review** — run **`self-review`** (`.ai/skills/self-review`) on your full branch diff. It uses the same rubric as the `@claude` CI reviewer — dead code, ephemeral comments, upstream conventions.

The **quality-reminder** hook (`.cursor/hooks/quality-reminder.py`) nudges you toward `validate-contribution` when pipeline, model, or API doc files change.

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
| "Ready to open a PR" | **Agent** + skills | Convention review → `validate-contribution` → `self-review` |
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
- `.cursor/skills/implement-contribution` — Phases 3–6 implementation playbook
- `.cursor/skills/validate-contribution` — pre-PR mechanical gates
- `05-code-review.mdc` — anti-patterns with fixes
- `.ai/skills/self-review` — full-diff review against upstream rubric
- Ask Cursor: "What's the convention for [X]?"
