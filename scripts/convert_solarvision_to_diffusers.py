"""
Convert SolarVision checkpoints to Diffusers format.

Example:
```bash
python scripts/convert_solarvision_to_diffusers.py \
    --transformer_ckpt_path path/to/solarvision_transformer.safetensors \
    --text_encoder_ckpt_path path/to/text_encoder.safetensors \
    --vae_ckpt_path path/to/vae.safetensors \
    --tokenizer_path path/to/tokenizer \
    --output_path path/to/solarvision-diffusers \
    --save_pipeline
```
"""

import argparse
import pathlib


def parse_args():
    parser = argparse.ArgumentParser(description="Convert SolarVision checkpoints to Diffusers format.")
    parser.add_argument("--transformer_ckpt_path", type=str, required=True)
    parser.add_argument("--text_encoder_ckpt_path", type=str, required=True)
    parser.add_argument("--vae_ckpt_path", type=str, required=True)
    parser.add_argument("--tokenizer_path", type=str, required=True)
    parser.add_argument("--output_path", type=str, required=True)
    parser.add_argument(
        "--save_pipeline",
        action="store_true",
        help="Save a full SolarVisionModularPipeline directory in addition to individual components.",
    )
    return parser.parse_args()


def rename_transformer_keys(state_dict: dict) -> dict:
    raise NotImplementedError("SolarVision transformer key renaming is not implemented yet.")


def rename_text_encoder_keys(state_dict: dict) -> dict:
    raise NotImplementedError("SolarVision text encoder key renaming is not implemented yet.")


def rename_vae_keys(state_dict: dict) -> dict:
    raise NotImplementedError("SolarVision VAE key renaming is not implemented yet.")


def main():
    args = parse_args()
    output_path = pathlib.Path(args.output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    raise NotImplementedError(
        "SolarVision checkpoint conversion is scaffolded. Parity verification is deferred until reference weights are available."
    )


if __name__ == "__main__":
    main()
