---
name: validate-contribution
description: >
  Use when implementation and tests for a new pipeline or model are done and the engineer
  needs to pass local CI gates before opening a PR. Runs make style, make quality, and
  pytest with a fix-and-re-run loop. Invoke after implement-contribution — e.g.
  "/validate-contribution slug solarvision".
---

# Validate Contribution

**Pre-PR validation skill** — run the same gates CI runs, fix failures, re-run until green.

Complements `implement-contribution` (Phases 3–5). This skill owns validation only.

## Execution contract

Run all gates sequentially to completion. Do not stop or ask between steps. Do not declare
PR-ready until `make quality` passes and slug-scoped pytest passes (excluding known
environment-only failures). If a gate fails, apply the matching fix below and re-run that
gate before continuing.

## Before starting

Confirm:

1. **Slug** — e.g. `solarvision` (test paths, doc entries)
2. **Architecture** — modular (`tests/modular_pipelines/<slug>/`) vs standard (`tests/pipelines/<slug>/`)
3. **Environment** — use repo `.venv` if present:

```bash
source .venv/bin/activate
```

If `doc-builder` is missing: `pip install hf-doc-builder` (in `.venv`).

## Step 1 — Auto-fix formatting

```bash
make style
```

`make style` runs ruff fix/format, doc-builder (write mode), and `check_doc_toc.py --fix_and_overwrite`
(to sort `_toctree.yml` entries).

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
| Failure in files **outside** `<slug>` | Report as pre-existing; do not block if unrelated to this contribution | — |
| `doc-builder: command not found` | `pip install hf-doc-builder` in `.venv`, activate, retry | `make quality` |

Repeat until `make quality` exits 0.

## Step 3 — Tests

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

## Step 4 — PR checklist

Verify before declaring complete:

- [ ] Imports registered in sub-package and top-level `__init__.py`
- [ ] `make quality` passes (full repo)
- [ ] Slug-scoped pipeline + model tests pass
- [ ] No `einops`, `torch.float64`, or pipeline subclassing in `<slug>` files
- [ ] Docs in `_toctree.yml` (sorted — `make style` handles this)
- [ ] Conversion script exists (parity may be deferred if no real weights)

## How this fits the stack

| Layer | Role |
|-------|------|
| **Rules** | Passive conventions while editing |
| **`implement-contribution`** | Phases 3–5: implement model, pipeline, tests |
| **This skill** | Validation: `make quality` + pytest fix loop |
| **Hook** | `.cursor/hooks/quality-reminder.py` — nudge to run this after pipeline/model writes |
| **CI** | `pr_tests.yml` — hard merge gate on push |

## Do not

- Re-implement model or pipeline logic (that is `implement-contribution`)
- Replace CI with custom validators
- Skip the fix loop and declare PR-ready on partial passes
- Block on environment-only test failures that CI hardware handles
