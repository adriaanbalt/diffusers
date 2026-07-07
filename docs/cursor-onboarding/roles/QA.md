# QA Engineer — Quick Guide

**Cursor rule:** `03-testing-standards.mdc`  
**Opens when:** You edit `tests/**`

## Required for initial pipeline PR

1. **Pipeline tests** — always (`tests/pipelines/<slug>/test_<slug>.py`)
2. **Model tests** — if new model class (`test_models_transformer_<slug>.py`)

## Test shape

- Subclass `PipelineTesterMixin`
- `get_dummy_components` — **tiny** configs (2 layers, 16px)
- `get_dummy_inputs` — deterministic (`torch.manual_seed(0)`)
- Generate model tests: `python utils/generate_model_tests.py`

## Out of scope for v1

LoRA tests, `@slow` tests, integration tests, quantization tests

## Cursor prompt

```
I'm a QA engineer. We added [PipelineName] under [path]. What tests are
required for the initial PR, what should the test file look like, and
what's explicitly out of scope for v1?
```
