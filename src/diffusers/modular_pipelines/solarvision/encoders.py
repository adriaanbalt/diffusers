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
from transformers import Gemma2PreTrainedModel, GemmaTokenizerFast

from ...configuration_utils import FrozenDict
from ...guiders import ClassifierFreeGuidance
from ...utils import logging
from ..modular_pipeline import ModularPipelineBlocks, PipelineState
from ..modular_pipeline_utils import ComponentSpec, InputParam, OutputParam
from .modular_pipeline import SolarVisionModularPipeline


logger = logging.get_logger(__name__)


def _get_gemma_prompt_embeds(
    text_encoder: Gemma2PreTrainedModel,
    tokenizer: GemmaTokenizerFast,
    prompt: list[str],
    device: torch.device,
    max_sequence_length: int,
) -> tuple[torch.Tensor, torch.Tensor]:
    text_inputs = tokenizer(
        prompt,
        padding="max_length",
        max_length=max_sequence_length,
        truncation=True,
        return_tensors="pt",
    )

    text_input_ids = text_inputs.input_ids.to(device)
    prompt_attention_mask = text_inputs.attention_mask.to(device)
    prompt_embeds = text_encoder(
        text_input_ids, attention_mask=prompt_attention_mask, output_hidden_states=True
    ).hidden_states[-2]
    prompt_embeds = prompt_embeds.to(dtype=text_encoder.dtype, device=device)
    return prompt_embeds, prompt_attention_mask


class SolarVisionTextEncoderStep(ModularPipelineBlocks):
    model_name = "solar-vision"

    @property
    def description(self) -> str:
        return "Text encoder step that encodes prompts into Gemma hidden states for SolarVision."

    @property
    def expected_components(self) -> list[ComponentSpec]:
        return [
            ComponentSpec("text_encoder", Gemma2PreTrainedModel),
            ComponentSpec("tokenizer", GemmaTokenizerFast),
            ComponentSpec(
                "guider",
                ClassifierFreeGuidance,
                config=FrozenDict({"guidance_scale": 4.0}),
                default_creation_method="from_config",
            ),
        ]

    @property
    def inputs(self) -> list[InputParam]:
        return [
            InputParam("prompt", type_hint=str | list[str], description="The prompt or prompts to guide generation."),
            InputParam(
                "negative_prompt",
                type_hint=str | list[str],
                description="The prompt or prompts not to guide generation.",
            ),
            InputParam(
                "system_prompt",
                type_hint=str,
                description="Optional system prompt prepended to each user prompt.",
            ),
            InputParam(
                "max_sequence_length",
                type_hint=int,
                default=256,
                description="Maximum sequence length to use with the prompt.",
            ),
        ]

    @property
    def intermediate_outputs(self) -> list[OutputParam]:
        return [
            OutputParam(
                "prompt_embeds",
                type_hint=torch.Tensor,
                kwargs_type="denoiser_input_fields",
                description="Prompt embeddings for the transformer.",
            ),
            OutputParam(
                "prompt_attention_mask",
                type_hint=torch.Tensor,
                kwargs_type="denoiser_input_fields",
                description="Attention mask for prompt embeddings.",
            ),
            OutputParam(
                "negative_prompt_embeds",
                type_hint=torch.Tensor,
                kwargs_type="denoiser_input_fields",
                description="Negative prompt embeddings for classifier-free guidance.",
            ),
            OutputParam(
                "negative_prompt_attention_mask",
                type_hint=torch.Tensor,
                kwargs_type="denoiser_input_fields",
                description="Attention mask for negative prompt embeddings.",
            ),
        ]

    @torch.no_grad()
    def __call__(self, components: SolarVisionModularPipeline, state: PipelineState) -> PipelineState:
        block_state = self.get_block_state(state)
        device = components._execution_device

        prompt = block_state.prompt
        if prompt is None:
            raise ValueError("Provide `prompt` for text-to-image generation.")
        if isinstance(prompt, str):
            prompt = [prompt]

        system_prompt = block_state.system_prompt or components.system_prompt
        prompt = [system_prompt + " <Prompt Start> " + p for p in prompt]

        block_state.prompt_embeds, block_state.prompt_attention_mask = _get_gemma_prompt_embeds(
            components.text_encoder,
            components.tokenizer,
            prompt,
            device,
            block_state.max_sequence_length,
        )

        if components.guider.guidance_scale > 1:
            negative_prompt = block_state.negative_prompt if block_state.negative_prompt is not None else ""
            if isinstance(negative_prompt, str):
                negative_prompt = [negative_prompt] * len(prompt)
            block_state.negative_prompt_embeds, block_state.negative_prompt_attention_mask = _get_gemma_prompt_embeds(
                components.text_encoder,
                components.tokenizer,
                negative_prompt,
                device,
                block_state.max_sequence_length,
            )
        else:
            block_state.negative_prompt_embeds = None
            block_state.negative_prompt_attention_mask = None

        self.set_block_state(state, block_state)
        return components, state
