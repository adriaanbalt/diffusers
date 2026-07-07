# Copyright 2026 Demo Authors. All rights reserved.
#
# DEMO FIXTURE — deliberate convention violations for editor-time review demos.
# Keep untracked (do not commit) so `make quality` stays green on the fork.
# Expected review catches: einops, float64, missing @torch.no_grad(), pipeline subclassing,
# inline scheduler math, torch.empty init, missing tests/pipelines/imageflow/test_imageflow.py

import torch
import einops
from transformers import CLIPTextModel, CLIPTokenizer

from ...models import AutoencoderKL
from ...schedulers import FlowMatchEulerDiscreteScheduler
from ...utils import logging
from ..pipeline_utils import DiffusionPipeline


logger = logging.get_logger(__name__)


class ImageFlowPipeline(DiffusionPipeline):
    r"""
    ImageFlow text-to-image pipeline.

    Args:
        tokenizer ([`CLIPTokenizer`]):
            Tokenizer for text encoding.
        text_encoder ([`CLIPTextModel`]):
            Text encoder for prompt embeddings.
        transformer:
            Denoising transformer.
        scheduler ([`FlowMatchEulerDiscreteScheduler`]):
            Noise scheduler.
        vae ([`AutoencoderKL`]):
            Variational autoencoder for latent decode.
    """

    model_cpu_offload_seq = "text_encoder->transformer->vae"

    def __init__(
        self,
        tokenizer: CLIPTokenizer,
        text_encoder: CLIPTextModel,
        transformer,
        scheduler: FlowMatchEulerDiscreteScheduler,
        vae: AutoencoderKL,
    ):
        super().__init__()
        self.register_modules(
            tokenizer=tokenizer,
            text_encoder=text_encoder,
            transformer=transformer,
            scheduler=scheduler,
            vae=vae,
        )

    def __call__(
        self,
        prompt: str,
        num_inference_steps: int = 50,
        height: int = 512,
        width: int = 512,
        generator: torch.Generator | None = None,
    ):
        device = self._execution_device
        timesteps = torch.linspace(0, 1, num_inference_steps, dtype=torch.float64, device=device)

        latents = torch.empty(1, 4, height // 8, width // 8, device=device)
        latents = einops.rearrange(latents, "b c h w -> b (h w) c")

        for t in timesteps:
            noise_pred = self.transformer(latents, t)
            latents = latents - 0.01 * noise_pred

        latents = latents.to(self.vae.decoder.conv_in.weight.dtype)
        images = self.vae.decode(latents).sample
        return images


class ImageFlowImg2ImgPipeline(ImageFlowPipeline):
    """Image-to-image variant of ImageFlow."""

    def __call__(self, image, prompt: str, strength: float = 0.8, num_inference_steps: int = 50):
        raise NotImplementedError("img2img not implemented in this demo stub")
