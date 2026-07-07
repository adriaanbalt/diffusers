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

import torch

from ...configuration_utils import FrozenDict
from ...guiders import ClassifierFreeGuidance
from ...models import SolarVisionTransformer2DModel
from ...schedulers import FlowMatchEulerDiscreteScheduler
from ...utils import logging
from ..modular_pipeline import (
    BlockState,
    LoopSequentialPipelineBlocks,
    ModularPipelineBlocks,
    PipelineState,
)
from ..modular_pipeline_utils import ComponentSpec, InputParam, OutputParam
from .modular_pipeline import SolarVisionModularPipeline


logger = logging.get_logger(__name__)


class SolarVisionLoopDenoiser(ModularPipelineBlocks):
    model_name = "solar-vision"

    @property
    def expected_components(self) -> list[ComponentSpec]:
        return [
            ComponentSpec(
                "guider",
                ClassifierFreeGuidance,
                config=FrozenDict({"guidance_scale": 4.0}),
                default_creation_method="from_config",
            ),
            ComponentSpec("transformer", SolarVisionTransformer2DModel),
        ]

    @property
    def description(self) -> str:
        return "Step within the denoising loop that runs the SolarVision transformer."

    @property
    def inputs(self) -> list[InputParam]:
        return [
            InputParam("latents", required=True, type_hint=torch.Tensor),
            InputParam("prompt_embeds", required=True, type_hint=torch.Tensor),
            InputParam("prompt_attention_mask", required=True, type_hint=torch.Tensor),
            InputParam("negative_prompt_embeds", type_hint=torch.Tensor),
            InputParam("negative_prompt_attention_mask", type_hint=torch.Tensor),
            InputParam("num_inference_steps", required=True, type_hint=int),
            InputParam("guidance_scale", type_hint=float),
            InputParam("cfg_trunc_ratio", default=1.0, type_hint=float),
            InputParam("cfg_normalization", default=True, type_hint=bool),
            InputParam("attention_kwargs", type_hint=dict),
        ]

    @torch.no_grad()
    def __call__(
        self,
        components: SolarVisionModularPipeline,
        block_state: BlockState,
        i: int,
        t: torch.Tensor,
    ):
        guidance_scale = block_state.guidance_scale
        if guidance_scale is None:
            guidance_scale = components.guider.guidance_scale

        do_classifier_free_guidance = guidance_scale > 1 and block_state.negative_prompt_embeds is not None
        do_classifier_free_truncation = (i + 1) / block_state.num_inference_steps > block_state.cfg_trunc_ratio

        current_timestep = 1 - t / components.scheduler.config.num_train_timesteps
        current_timestep = current_timestep.expand(block_state.latents.shape[0])

        noise_pred_cond = components.transformer(
            hidden_states=block_state.latents,
            timestep=current_timestep,
            encoder_hidden_states=block_state.prompt_embeds,
            encoder_attention_mask=block_state.prompt_attention_mask,
            return_dict=False,
            attention_kwargs=block_state.attention_kwargs,
        )[0]

        if do_classifier_free_guidance and not do_classifier_free_truncation:
            noise_pred_uncond = components.transformer(
                hidden_states=block_state.latents,
                timestep=current_timestep,
                encoder_hidden_states=block_state.negative_prompt_embeds,
                encoder_attention_mask=block_state.negative_prompt_attention_mask,
                return_dict=False,
                attention_kwargs=block_state.attention_kwargs,
            )[0]
            noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_cond - noise_pred_uncond)
            if block_state.cfg_normalization:
                cond_norm = torch.norm(noise_pred_cond, dim=-1, keepdim=True)
                noise_norm = torch.norm(noise_pred, dim=-1, keepdim=True)
                noise_pred = noise_pred * (cond_norm / noise_norm)
        else:
            noise_pred = noise_pred_cond

        block_state.noise_pred = -noise_pred
        return components, block_state


class SolarVisionLoopAfterDenoiser(ModularPipelineBlocks):
    model_name = "solar-vision"

    @property
    def expected_components(self) -> list[ComponentSpec]:
        return [ComponentSpec("scheduler", FlowMatchEulerDiscreteScheduler)]

    @property
    def intermediate_outputs(self) -> list[OutputParam]:
        return [OutputParam("latents", type_hint=torch.Tensor)]

    @torch.no_grad()
    def __call__(
        self,
        components: SolarVisionModularPipeline,
        block_state: BlockState,
        i: int,
        t: torch.Tensor,
    ):
        latents_dtype = block_state.latents.dtype
        block_state.latents = components.scheduler.step(
            block_state.noise_pred,
            t,
            block_state.latents,
            return_dict=False,
        )[0]
        if block_state.latents.dtype != latents_dtype:
            block_state.latents = block_state.latents.to(latents_dtype)
        return components, block_state


class SolarVisionDenoiseLoopWrapper(LoopSequentialPipelineBlocks):
    model_name = "solar-vision"

    @property
    def loop_expected_components(self) -> list[ComponentSpec]:
        return [
            ComponentSpec("scheduler", FlowMatchEulerDiscreteScheduler),
            ComponentSpec("transformer", SolarVisionTransformer2DModel),
        ]

    @property
    def loop_inputs(self) -> list[InputParam]:
        return [
            InputParam("timesteps", required=True, type_hint=torch.Tensor),
            InputParam("num_inference_steps", required=True, type_hint=int),
        ]

    @torch.no_grad()
    def __call__(self, components: SolarVisionModularPipeline, state: PipelineState) -> PipelineState:
        block_state = self.get_block_state(state)
        block_state.num_warmup_steps = max(
            len(block_state.timesteps) - block_state.num_inference_steps * components.scheduler.order,
            0,
        )

        with self.progress_bar(total=block_state.num_inference_steps) as progress_bar:
            for i, t in enumerate(block_state.timesteps):
                components, block_state = self.loop_step(components, block_state, i=i, t=t)
                if i == len(block_state.timesteps) - 1 or (
                    (i + 1) > block_state.num_warmup_steps and (i + 1) % components.scheduler.order == 0
                ):
                    progress_bar.update()

        self.set_block_state(state, block_state)
        return components, state


class SolarVisionDenoiseStep(SolarVisionDenoiseLoopWrapper):
    block_classes = [SolarVisionLoopDenoiser, SolarVisionLoopAfterDenoiser]
    block_names = ["denoiser", "after_denoiser"]
