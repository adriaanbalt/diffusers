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


# auto_docstring
class SolarVisionCoreDenoiseStep(SequentialPipelineBlocks):
    """
    Denoise block that takes encoded SolarVision text inputs and runs the denoising process.
    """

    model_name = "solar-vision"
    block_classes = [
        SolarVisionTextInputStep,
        SolarVisionPrepareLatentsStep,
        SolarVisionSetTimestepsStep,
        SolarVisionDenoiseStep,
    ]
    block_names = ["input", "prepare_latents", "set_timesteps", "denoise"]

    @property
    def description(self) -> str:
        return "Denoise block that takes encoded SolarVision text inputs and runs the denoising process."

    @property
    def outputs(self):
        return [OutputParam.template("latents")]


# auto_docstring
class SolarVisionAutoBlocks(SequentialPipelineBlocks):
    """
    Auto modular pipeline for text-to-image generation using SolarVision.
    """

    model_name = "solar-vision"
    block_classes = [
        SolarVisionTextEncoderStep,
        SolarVisionCoreDenoiseStep,
        SolarVisionVaeDecoderStep,
    ]
    block_names = ["text_encoder", "denoise", "decode"]
    _workflow_map = {"text2image": {"prompt": True}}

    @property
    def description(self) -> str:
        return "Auto modular pipeline for text-to-image generation using SolarVision."

    @property
    def outputs(self):
        return [OutputParam.template("images")]
