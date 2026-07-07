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
from transformers import AutoTokenizer, Mistral3Model

from ...configuration_utils import FrozenDict
from ...guiders import ClassifierFreeGuidance
from ...utils import logging
from ...utils.import_utils import is_transformers_version
from ..modular_pipeline import ModularPipelineBlocks, PipelineState
from ..modular_pipeline_utils import ComponentSpec, InputParam, OutputParam
from .modular_pipeline import SolarVisionModularPipeline


if is_transformers_version("<", "5.0.0"):
    raise ImportError("`SolarVisionModularPipeline` requires `transformers>=5.0.0` for `Mistral3Model`.")


logger = logging.get_logger(__name__)  # pylint: disable=invalid-name


class SolarVisionTextEncoderStep(ModularPipelineBlocks):
    model_name = "solarvision"

    @property
    def description(self) -> str:
        return "Text encoder step that encodes prompts into variable-length hidden states for the SolarVision transformer."

    @property
    def expected_components(self) -> list[ComponentSpec]:
        return [
            ComponentSpec("text_encoder", Mistral3Model),
            ComponentSpec("tokenizer", AutoTokenizer),
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
            InputParam("prompt", type_hint=str, description="The prompt or prompts to guide image generation."),
            InputParam(
                "negative_prompt",
                type_hint=str,
                description="The prompt or prompts to avoid during image generation.",
            ),
        ]

    @property
    def intermediate_outputs(self) -> list[OutputParam]:
        return [
            OutputParam(
                "prompt_embeds",
                type_hint=list,
                kwargs_type="denoiser_input_fields",
                description="List of per-prompt text embeddings of shape (T, H).",
            ),
            OutputParam(
                "negative_prompt_embeds",
                type_hint=list,
                kwargs_type="denoiser_input_fields",
                description="List of per-prompt negative text embeddings for classifier-free guidance.",
            ),
        ]

    @staticmethod
    def _encode(
        text_encoder: Mistral3Model,
        tokenizer: AutoTokenizer,
        prompt: list[str],
        device: torch.device,
    ) -> list[torch.Tensor]:
        text_hiddens = []
        for p in prompt:
            ids = tokenizer(p, add_special_tokens=True, truncation=True, padding=False)["input_ids"]
            if len(ids) == 0:
                ids = [tokenizer.bos_token_id if tokenizer.bos_token_id is not None else 0]
            input_ids = torch.tensor([ids], device=device)
            outputs = text_encoder(input_ids=input_ids, output_hidden_states=True)
            text_hiddens.append(outputs.hidden_states[-2][0])
        return text_hiddens

    @torch.no_grad()
    def __call__(self, components: SolarVisionModularPipeline, state: PipelineState) -> PipelineState:
        block_state = self.get_block_state(state)
        device = components._execution_device

        prompt = block_state.prompt
        if prompt is None:
            prompt = [""]
        if isinstance(prompt, str):
            prompt = [prompt]

        block_state.prompt_embeds = self._encode(
            text_encoder=components.text_encoder,
            tokenizer=components.tokenizer,
            prompt=prompt,
            device=device,
        )

        if components.requires_unconditional_embeds:
            negative_prompt = block_state.negative_prompt
            if negative_prompt is None:
                negative_prompt = ""
            if isinstance(negative_prompt, str):
                negative_prompt = [negative_prompt] * len(prompt)
            if len(negative_prompt) != len(prompt):
                raise ValueError(
                    f"`negative_prompt` must have the same length as `prompt` ({len(prompt)}), "
                    f"got {len(negative_prompt)}."
                )
            block_state.negative_prompt_embeds = self._encode(
                text_encoder=components.text_encoder,
                tokenizer=components.tokenizer,
                prompt=negative_prompt,
                device=device,
            )
        else:
            block_state.negative_prompt_embeds = None

        self.set_block_state(state, block_state)
        return components, state
