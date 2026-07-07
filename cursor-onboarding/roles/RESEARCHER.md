# ML Researcher — Quick Guide

**Cursor rule:** `06-multi-role-researcher.mdc`  
**Opens when:** You edit `src/**/models/**`, pipelines, or `scripts/convert_*`

## Your priority order

1. Reference inference script — source of truth for behavior
2. Weight conversion — `scripts/convert_<slug>_to_diffusers.py`
3. Numerical parity — CPU/float32, tolerance < 1e-3 vs reference
4. Model implementation — `transformer_<slug>.py`
5. Pipeline — after parity verified
6. Tests — tiny configs only

## Defer to follow-up PRs

LoRA, slow/integration tests, quantization, context parallelism

## Common traps

- `einops` — rewrite with `reshape`/`permute`
- `torch.float64` — use float32
- Attention — use processor pattern + `dispatch_attention_fn`
- Full-size test models — CI needs 2 layers, 16px

## Cursor prompt

```
I'm an ML researcher integrating [ModelName]. I have a reference script and
converted weights. Help me verify parity before I touch the pipeline.
What should I do first, and what can I skip for v1?
```
