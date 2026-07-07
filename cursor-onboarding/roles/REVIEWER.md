# Code Reviewer — Quick Guide

**Cursor rule:** `07-multi-role-reviewer.mdc`  
**Opens when:** Reviewing any PR or editing `src/diffusers/**`

## Review order

1. **Architecture** — files in right place? Slug naming correct?
2. **Conventions** — patterns match library standards?
3. **Correctness** — numerical parity with reference?
4. **Tests** — coverage, tiny configs, no LoRA/slow in v1?
5. **Style** — `make quality` passing?

## Quick rejection criteria

- `import einops`
- `torch.float64` in model code
- Missing `__init__.py` registration
- `__call__` without `@torch.no_grad()`
- Pipeline subclassing another pipeline
- Test models not on `hf-internal-testing/`

## Cursor prompt

```
I'm reviewing this PR as a maintainer. Check [file path] for convention
violations. Use the reviewer checklist — architecture first, then conventions,
then tests. List blocking issues vs warnings.
```
