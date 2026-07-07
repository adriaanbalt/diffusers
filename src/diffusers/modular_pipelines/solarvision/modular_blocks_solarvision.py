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

from ...utils import logging
from ..modular_pipeline import SequentialPipelineBlocks
from ..modular_pipeline_utils import OutputParam
from .before_denoise import (
    SolarVisionPrepareLatentsStep,
    SolarVisionSetTimestepsStep,
    SolarVisionTextInputStep,
)
from .decoders import SolarVisionVaeDecoderStep
from .denoise import SolarVisionDenoiseStep
from .encoders import SolarVisionTextEncoderStep


logger = logging.get_logger(__name__)  # pylint: disable=invalid-name


class SolarVisionCoreDenoiseStep(SequentialPipelineBlocks):
    model_name = "solarvision"
    block_classes = [
        SolarVisionTextInputStep,
        SolarVisionSetTimestepsStep,
        SolarVisionPrepareLatentsStep,
        SolarVisionDenoiseStep,
    ]
    block_names = ["input", "set_timesteps", "prepare_latents", "denoise"]

    @property
    def description(self):
        return "Denoise block that takes encoded conditions and runs the denoising process for SolarVision."

    @property
    def outputs(self):
        return [OutputParam.template("latents")]


class SolarVisionAutoBlocks(SequentialPipelineBlocks):
    model_name = "solarvision"
    block_classes = [
        SolarVisionTextEncoderStep,
        SolarVisionCoreDenoiseStep,
        SolarVisionVaeDecoderStep,
    ]
    block_names = ["text_encoder", "denoise", "decode"]
    _workflow_map = {
        "text2image": {"prompt": True},
    }

    @property
    def description(self):
        return "Auto modular pipeline for SolarVision text-to-image generation."

    @property
    def outputs(self):
        return [OutputParam.template("images")]
