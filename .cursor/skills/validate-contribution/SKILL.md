---
name: validate-contribution
description: >
  Use when implementation and tests for a new pipeline or model are done and the engineer
  needs to pass local CI gates before opening a PR. Runs make style, make quality, repository
  consistency checks, and pytest with a fix-and-re-run loop. Invoke after
  implement-contribution — e.g. "/validate-contribution slug solarvision".
---

# Validate Contribution

**Pre-PR validation skill** — run the same gates CI runs, fix failures, re-run until green.

Complements `implement-contribution` (Phases 3–6). This skill owns validation only.

## Execution contract

Run all gates sequentially to completion. Do not stop or ask between steps. Do not declare
PR-ready until **all** of the following pass:

1. `make quality`
2. Repository consistency (matches CI `check_repository_consistency`)
3. Slug-scoped pytest (excluding known environment-only failures)
4. Working tree clean (`git diff --quiet`)

If a gate fails, apply the matching fix below and re-run that gate before continuing.

**Validation applies only to the exact commit set being pushed.** If any file changes after
a gate passes — especially `docs/source/en/_toctree.yml`, `docs/source/en/api/**`, or
`src/diffusers/__init__.py` — re-run from Step 1. Do not declare PR-ready twice without
re-running all gates.

## Before starting

Confirm:

1. **Slug** — e.g. `solarvision` (test paths, doc entries)
2. **Architecture** — modular (`tests/modular_pipelines/<slug>/`) vs standard (`tests/pipelines/<slug>/`)
3. **Docs already committed** — API stubs and `_toctree.yml` entries must exist before
   validation starts (Phase 6 of `implement-contribution`). Do not add docs after this skill.
4. **Environment** — use repo `.venv` if present:

```bash
source .venv/bin/activate
pip install -e ".[quality]"
```

If `doc-builder` is missing: `pip install hf-doc-builder` (in `.venv`).

### Fork prerequisites (one-time, not code)

On a personal fork (not `huggingface/diffusers`):

- Create GitHub labels `size/S`, `size/M`, `size/L` if missing (PR Labeler workflow)
- Org-runner jobs (Fast CPU/GPU matrix) may not run on a fork — upstream CI is the bar for those
- **Do not patch `.github/workflows/`** to pass CI — contribution code must pass existing workflows

## Step 1 — Auto-fix formatting

```bash
make style
```

`make style` runs ruff fix/format, doc-builder (write mode), dependency table update, and
`check_doc_toc.py --fix_and_overwrite` (sorts `_toctree.yml` by `local` path).

### `_toctree.yml` rule

Never manually sort entries by display title. Append new `local:` entries anywhere in the
section, then run `make style` — CI sorts alphabetically by `local` path string.

## Step 2 — Quality gates (fix loop)

```bash
make quality
```

`make quality` runs, in order:

1. `ruff check` — lint
2. `ruff format --check` — formatting
3. `doc-builder style ... --check_only` — doc line length (119 chars)
4. `python utils/check_doc_toc.py` — TOC sort order

### Known failures → fixes

| Error | Fix | Then re-run |
|-------|-----|-------------|
| `N files should be restyled` (doc-builder) | `doc-builder style src/diffusers docs/source --max_len 119` | `make quality` |
| `table of content is not properly sorted` (check_doc_toc) | `make style` | `make quality` |
| `ruff check` / `ruff format` on `<slug>` files | Fix the reported file(s) or run `make style` | `make quality` |
| Failure in files **outside** `<slug>` that you modified | Fix or revert — do not leave unrelated formatting in the PR | `make quality` |
| `doc-builder: command not found` | `pip install hf-doc-builder` in `.venv`, activate, retry | `make quality` |

Repeat until `make quality` exits 0.

## Step 3 — Repository consistency (matches CI)

Runs the same checks as `check_repository_consistency` in `pr_tests.yml`:

```bash
make fix-copies
python utils/check_copies.py
python utils/check_dummies.py
python utils/check_support_list.py
python utils/check_forward_call_docstrings.py
make deps_table_check_updated
```

`make fix-copies` updates `dummy_pt_objects.py` when new classes are registered in
`__init__.py`. Commit any files it modifies, then re-run the check commands until all exit 0.

### Known failures → fixes

| Error | Fix | Then re-run |
|-------|-----|-------------|
| `objects that are not present in dummy_pt_objects.py` | `make fix-copies`, commit generated files | Step 3 checks |
| `dependency table is outdated` | `make style`, commit | `make deps_table_check_updated` |
| `check_copies.py` / `check_support_list.py` failure | Fix reported file or run `make fix-copies` | Step 3 checks |

## Step 4 — Tests

```bash
python -m pytest tests/modular_pipelines/<slug>/ -x -q    # modular
python -m pytest tests/pipelines/<slug>/ -x -q            # standard (if applicable)
python -m pytest tests/models/transformers/test_models_transformer_<slug>.py -x -q
```

### Environment-only failures (non-blocking)

Note but do not block PR-ready on:

- MPS: `mem_get_info` / CPU offload tests (`test_components_auto_cpu_offload_inference_consistent`)
- MPS/CUDA: group-offloading memory tests requiring CUDA streams
- Skipped dtype/sharding variant tests

Confirm test logic is correct; CI on Linux CPU/CUDA is the merge bar.

## Step 5 — PR checklist

Verify before declaring complete:

- [ ] Imports registered in sub-package and top-level `__init__.py`
- [ ] `make quality` passes (full repo)
- [ ] Repository consistency checks pass (Step 3)
- [ ] Slug-scoped pipeline + model tests pass
- [ ] No `einops`, `torch.float64`, or pipeline subclassing in `<slug>` files
- [ ] API doc stubs exist and `_toctree.yml` entries are sorted (`make style` handles sort)
- [ ] `dummy_pt_objects.py` updated if new lazy-import classes were added
- [ ] Conversion script exists (parity may be deferred if no real weights)
- [ ] `git diff --quiet` — no uncommitted changes after validation

```bash
git diff --quiet || { echo "Uncommitted changes — commit or re-run validation"; exit 1; }
```

## What this skill does not replicate

`make quality` does **not** run `build_pr_documentation` (full multi-language autodoc build).
That CI job builds the entire doc site. Failures in unrelated existing pages on a personal
fork are environment/infra issues — not contribution defects. Do not patch workflows to fix
them. Against `huggingface/diffusers`, upstream CI is the doc-build gate.

## How this fits the stack

| Layer | Role |
|-------|------|
| **Rules** | Passive conventions while editing |
| **`implement-contribution`** | Phases 3–6: model, pipeline, tests, docs |
| **This skill** | Validation: quality + repo consistency + pytest |
| **Hook** | `.cursor/hooks/quality-reminder.py` — nudge after pipeline/model/doc writes |
| **CI** | `pr_tests.yml` — hard merge gate on push |

## Do not

- Re-implement model or pipeline logic (that is `implement-contribution`)
- Patch `.github/workflows/` to pass CI
- Add or edit docs / `_toctree.yml` after declaring PR-ready without re-running all steps
- Manually sort `_toctree.yml` by title
- Replace CI with custom validators
- Skip the fix loop and declare PR-ready on partial passes
- Block on environment-only test failures that CI hardware handles
