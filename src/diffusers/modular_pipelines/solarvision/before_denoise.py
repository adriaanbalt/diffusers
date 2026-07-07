# Copyright 2026 The HuggingFace Team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import inspect

import numpy as np
import torch

from ...schedulers import FlowMatchEulerDiscreteScheduler
from ...utils import logging
from ...utils.torch_utils import randn_tensor
from ..modular_pipeline import ModularPipelineBlocks, PipelineState
from ..modular_pipeline_utils import ComponentSpec, InputParam, OutputParam
from .modular_pipeline import SolarVisionModularPipeline


logger = logging.get_logger(__name__)


# Copied from diffusers.pipelines.flux.pipeline_flux.calculate_shift
def calculate_shift(
    image_seq_len,
    base_seq_len: int = 256,
    max_seq_len: int = 4096,
    base_shift: float = 0.5,
    max_shift: float = 1.15,
):
    m = (max_shift - base_shift) / (max_seq_len - base_seq_len)
    b = base_shift - m * base_seq_len
    mu = image_seq_len * m + b
    return mu


# Copied from diffusers.pipelines.stable_diffusion.pipeline_stable_diffusion.retrieve_timesteps
def retrieve_timesteps(
    scheduler,
    num_inference_steps: int | None = None,
    device: str | torch.device | None = None,
    timesteps: list[int] | None = None,
    sigmas: list[float] | None = None,
    **kwargs,
):
    r"""
    Calls the scheduler's `set_timesteps` method and retrieves timesteps from the scheduler after the call. Handles
    custom timesteps. Any kwargs will be supplied to `scheduler.set_timesteps`.

    Args:
        scheduler (`SchedulerMixin`):
            The scheduler to get timesteps from.
        num_inference_steps (`int`):
            The number of diffusion steps used when generating samples with a pre-trained model. If used, `timesteps`
            must be `None`.
        device (`str` or `torch.device`, *optional*):
            The device to which the timesteps should be moved to. If `None`, the timesteps are not moved.
        timesteps (`list[int]`, *optional*):
            Custom timesteps used to override the timestep spacing strategy of the scheduler. If `timesteps` is passed,
            `num_inference_steps` and `sigmas` must be `None`.
        sigmas (`list[float]`, *optional*):
            Custom sigmas used to override the timestep spacing strategy of the scheduler. If `sigmas` is passed,
            `num_inference_steps` and `timesteps` must be `None`.

    Returns:
        `tuple[torch.Tensor, int]`: A tuple where the first element is the timestep schedule from the scheduler and the
        second element is the number of inference steps.
    """
    if timesteps is not None and sigmas is not None:
        raise ValueError("Only one of `timesteps` or `sigmas` can be passed. Please choose one to set custom values")
    if timesteps is not None:
        accepts_timesteps = "timesteps" in set(inspect.signature(scheduler.set_timesteps).parameters.keys())
        if not accepts_timesteps:
            raise ValueError(
                f"The current scheduler class {scheduler.__class__}'s `set_timesteps` does not support custom"
                f" timestep schedules. Please check whether you are using the correct scheduler."
            )
        scheduler.set_timesteps(timesteps=timesteps, device=device, **kwargs)
        timesteps = scheduler.timesteps
        num_inference_steps = len(timesteps)
    elif sigmas is not None:
        accept_sigmas = "sigmas" in set(inspect.signature(scheduler.set_timesteps).parameters.keys())
        if not accept_sigmas:
            raise ValueError(
                f"The current scheduler class {scheduler.__class__}'s `set_timesteps` does not support custom"
                f" sigmas schedules. Please check whether you are using the correct scheduler."
            )
        scheduler.set_timesteps(sigmas=sigmas, device=device, **kwargs)
        timesteps = scheduler.timesteps
        num_inference_steps = len(timesteps)
    else:
        scheduler.set_timesteps(num_inference_steps, device=device, **kwargs)
        timesteps = scheduler.timesteps
    return timesteps, num_inference_steps


class SolarVisionTextInputStep(ModularPipelineBlocks):
    model_name = "solar-vision"

    @property
    def description(self) -> str:
        return "Input processing step that expands prompt embeddings for batch generation."

    @property
    def inputs(self) -> list[InputParam]:
        return [
            InputParam("num_images_per_prompt", default=1, type_hint=int),
            InputParam("prompt_embeds", required=True, type_hint=torch.Tensor),
            InputParam("prompt_attention_mask", required=True, type_hint=torch.Tensor),
            InputParam("negative_prompt_embeds", type_hint=torch.Tensor),
            InputParam("negative_prompt_attention_mask", type_hint=torch.Tensor),
        ]

    @property
    def intermediate_outputs(self) -> list[OutputParam]:
        return [
            OutputParam("batch_size", type_hint=int),
            OutputParam("dtype", type_hint=torch.dtype),
            OutputParam("prompt_embeds", type_hint=torch.Tensor),
            OutputParam("prompt_attention_mask", type_hint=torch.Tensor),
            OutputParam("negative_prompt_embeds", type_hint=torch.Tensor),
            OutputParam("negative_prompt_attention_mask", type_hint=torch.Tensor),
        ]

    @torch.no_grad()
    def __call__(self, components: SolarVisionModularPipeline, state: PipelineState) -> PipelineState:
        block_state = self.get_block_state(state)

        block_state.batch_size = block_state.prompt_embeds.shape[0]
        block_state.dtype = block_state.prompt_embeds.dtype

        _, seq_len, _ = block_state.prompt_embeds.shape
        prompt_embeds = block_state.prompt_embeds.repeat(1, block_state.num_images_per_prompt, 1)
        prompt_embeds = prompt_embeds.view(block_state.batch_size * block_state.num_images_per_prompt, seq_len, -1)
        prompt_attention_mask = block_state.prompt_attention_mask.repeat(block_state.num_images_per_prompt, 1)
        prompt_attention_mask = prompt_attention_mask.view(
            block_state.batch_size * block_state.num_images_per_prompt, -1
        )

        if block_state.negative_prompt_embeds is not None:
            _, neg_seq_len, _ = block_state.negative_prompt_embeds.shape
            negative_prompt_embeds = block_state.negative_prompt_embeds.repeat(1, block_state.num_images_per_prompt, 1)
            negative_prompt_embeds = negative_prompt_embeds.view(
                block_state.batch_size * block_state.num_images_per_prompt, neg_seq_len, -1
            )
            negative_prompt_attention_mask = block_state.negative_prompt_attention_mask.repeat(
                block_state.num_images_per_prompt, 1
            )
            negative_prompt_attention_mask = negative_prompt_attention_mask.view(
                block_state.batch_size * block_state.num_images_per_prompt, -1
            )
            block_state.negative_prompt_embeds = negative_prompt_embeds
            block_state.negative_prompt_attention_mask = negative_prompt_attention_mask
        else:
            block_state.negative_prompt_embeds = None
            block_state.negative_prompt_attention_mask = None

        block_state.prompt_embeds = prompt_embeds
        block_state.prompt_attention_mask = prompt_attention_mask

        self.set_block_state(state, block_state)
        return components, state


class SolarVisionPrepareLatentsStep(ModularPipelineBlocks):
    model_name = "solar-vision"

    @property
    def description(self) -> str:
        return "Prepare latents step for SolarVision text-to-image."

    @property
    def inputs(self) -> list[InputParam]:
        return [
            InputParam("height", type_hint=int),
            InputParam("width", type_hint=int),
            InputParam("latents", type_hint=torch.Tensor),
            InputParam("num_images_per_prompt", default=1, type_hint=int),
            InputParam("generator"),
            InputParam("batch_size", required=True, type_hint=int),
            InputParam("dtype", type_hint=torch.dtype),
        ]

    @property
    def intermediate_outputs(self) -> list[OutputParam]:
        return [OutputParam("latents", type_hint=torch.Tensor)]

    @torch.no_grad()
    def __call__(self, components: SolarVisionModularPipeline, state: PipelineState) -> PipelineState:
        block_state = self.get_block_state(state)
        device = components._execution_device
        batch_size = block_state.batch_size * block_state.num_images_per_prompt

        block_state.height = block_state.height or components.default_height
        block_state.width = block_state.width or components.default_width

        height = 2 * (int(block_state.height) // (components.vae_scale_factor * 2))
        width = 2 * (int(block_state.width) // (components.vae_scale_factor * 2))

        if block_state.latents is not None:
            block_state.latents = block_state.latents.to(device=device, dtype=block_state.dtype)
        else:
            shape = (batch_size, components.num_channels_latents, height, width)
            block_state.latents = randn_tensor(
                shape,
                generator=block_state.generator,
                device=device,
                dtype=block_state.dtype,
            )

        self.set_block_state(state, block_state)
        return components, state


class SolarVisionSetTimestepsStep(ModularPipelineBlocks):
    model_name = "solar-vision"

    @property
    def expected_components(self) -> list[ComponentSpec]:
        return [ComponentSpec("scheduler", FlowMatchEulerDiscreteScheduler)]

    @property
    def description(self) -> str:
        return "Step that sets the scheduler timesteps for SolarVision inference."

    @property
    def inputs(self) -> list[InputParam]:
        return [
            InputParam("num_inference_steps", default=30, type_hint=int),
            InputParam("sigmas"),
            InputParam("height", type_hint=int),
            InputParam("width", type_hint=int),
            InputParam("latents", required=True, type_hint=torch.Tensor),
        ]

    @property
    def intermediate_outputs(self) -> list[OutputParam]:
        return [
            OutputParam("timesteps", type_hint=torch.Tensor),
            OutputParam("num_inference_steps", type_hint=int),
        ]

    @torch.no_grad()
    def __call__(self, components: SolarVisionModularPipeline, state: PipelineState) -> PipelineState:
        block_state = self.get_block_state(state)
        device = components._execution_device

        sigmas = block_state.sigmas
        if sigmas is None:
            sigmas = np.linspace(1.0, 1 / block_state.num_inference_steps, block_state.num_inference_steps).tolist()

        height = 2 * (int(block_state.height) // (components.vae_scale_factor * 2))
        width = 2 * (int(block_state.width) // (components.vae_scale_factor * 2))
        image_seq_len = (height // components.patch_size) * (width // components.patch_size)
        mu = calculate_shift(
            image_seq_len,
            components.scheduler.config.get("base_image_seq_len", 256),
            components.scheduler.config.get("max_image_seq_len", 4096),
            components.scheduler.config.get("base_shift", 0.5),
            components.scheduler.config.get("max_shift", 1.15),
        )

        timesteps, num_inference_steps = retrieve_timesteps(
            components.scheduler,
            block_state.num_inference_steps,
            device,
            sigmas=sigmas,
            mu=mu,
        )

        block_state.timesteps = timesteps
        block_state.num_inference_steps = num_inference_steps
        self.set_block_state(state, block_state)
        return components, state
