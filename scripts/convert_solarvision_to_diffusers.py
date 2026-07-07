"""
Convert SolarVision checkpoints to Diffusers format.

Example:
```bash
python scripts/convert_solarvision_to_diffusers.py \
    --transformer_ckpt_path path/to/transformer.safetensors \
    --text_encoder_ckpt_path path/to/text_encoder.safetensors \
    --vae_ckpt_path path/to/vae.safetensors \
    --tokenizer_path path/to/tokenizer \
    --output_path path/to/solarvision-diffusers \
    --save_pipeline
```
"""

import argparse
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Convert SolarVision checkpoints to Diffusers format.")
    parser.add_argument(
        "--transformer_ckpt_path",
        type=str,
        required=True,
        help="Path to the SolarVision transformer checkpoint.",
    )
    parser.add_argument(
        "--text_encoder_ckpt_path",
        type=str,
        default=None,
        help="Path to the SolarVision text encoder checkpoint.",
    )
    parser.add_argument(
        "--vae_ckpt_path",
        type=str,
        default=None,
        help="Path to the SolarVision VAE checkpoint.",
    )
    parser.add_argument(
        "--tokenizer_path",
        type=str,
        default=None,
        help="Path to the tokenizer directory.",
    )
    parser.add_argument(
        "--output_path",
        type=str,
        required=True,
        help="Directory where the converted Diffusers checkpoint will be saved.",
    )
    parser.add_argument(
        "--save_pipeline",
        action="store_true",
        help="Save a full modular pipeline index alongside converted components.",
    )
    return parser.parse_args()


def rename_transformer_key(key: str) -> str:
    """Map upstream SolarVision transformer keys to Diffusers module names."""
    return key


def convert_transformer_state_dict(state_dict: dict) -> dict:
    return {rename_transformer_key(key): value for key, value in state_dict.items()}


def save_converted_checkpoint(output_path: Path) -> None:
    output_path.mkdir(parents=True, exist_ok=True)


def main():
    args = parse_args()
    output_path = Path(args.output_path)

    # Parity verification is deferred until official SolarVision weights are available.
    save_converted_checkpoint(output_path)

    raise NotImplementedError(
        "SolarVision weight conversion is scaffolded but not implemented yet. "
        f"Received transformer_ckpt_path={args.transformer_ckpt_path!r}, output_path={args.output_path!r}. "
        "Add key-renaming and save_pretrained logic once upstream checkpoints are available."
    )


if __name__ == "__main__":
    main()
