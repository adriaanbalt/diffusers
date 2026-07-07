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

import pytest
import torch
from transformers import AutoTokenizer, Gemma2Config, Gemma2Model

from diffusers import (
    AutoencoderKL,
    FlowMatchEulerDiscreteScheduler,
    SolarVisionAutoBlocks,
    SolarVisionModularPipeline,
    SolarVisionTransformer2DModel,
)

from ...testing_utils import enable_full_determinism
from ..test_modular_pipelines_common import ModularPipelineTesterMixin


enable_full_determinism()


SOLARVISION_TEXT2IMAGE_WORKFLOWS = {
    "text2image": [
        ("text_encoder", "SolarVisionTextEncoderStep"),
        ("denoise.input", "SolarVisionTextInputStep"),
        ("denoise.prepare_latents", "SolarVisionPrepareLatentsStep"),
        ("denoise.set_timesteps", "SolarVisionSetTimestepsStep"),
        ("denoise.denoise", "SolarVisionDenoiseStep"),
        ("decode", "SolarVisionVaeDecoderStep"),
    ],
}


def get_dummy_components():
    torch.manual_seed(0)
    transformer = SolarVisionTransformer2DModel(
        sample_size=4,
        patch_size=2,
        in_channels=4,
        hidden_size=8,
        num_layers=2,
        num_refiner_layers=1,
        num_attention_heads=1,
        num_kv_heads=1,
        multiple_of=2,
        ffn_dim_multiplier=None,
        norm_eps=1e-5,
        scaling_factor=1.0,
        axes_dim_rope=[4, 2, 2],
        axes_lens=(128, 128, 128),
        cap_feat_dim=8,
    )

    torch.manual_seed(0)
    vae = AutoencoderKL(
        sample_size=32,
        in_channels=3,
        out_channels=3,
        block_out_channels=(4,),
        layers_per_block=1,
        latent_channels=4,
        norm_num_groups=1,
        use_quant_conv=False,
        use_post_quant_conv=False,
        shift_factor=0.0609,
        scaling_factor=1.5035,
    )

    scheduler = FlowMatchEulerDiscreteScheduler()
    tokenizer = AutoTokenizer.from_pretrained("hf-internal-testing/dummy-gemma")

    torch.manual_seed(0)
    config = Gemma2Config(
        head_dim=4,
        hidden_size=8,
        intermediate_size=8,
        num_attention_heads=2,
        num_hidden_layers=2,
        num_key_value_heads=2,
        sliding_window=2,
    )
    text_encoder = Gemma2Model(config).eval()

    return {
        "transformer": transformer,
        "vae": vae.eval(),
        "scheduler": scheduler,
        "text_encoder": text_encoder,
        "tokenizer": tokenizer,
    }


class TestSolarVisionModularPipelineFast(ModularPipelineTesterMixin):
    pipeline_class = SolarVisionModularPipeline
    pipeline_blocks_class = SolarVisionAutoBlocks
    params = frozenset(["prompt", "height", "width", "negative_prompt", "guidance_scale"])
    batch_params = frozenset(["prompt", "negative_prompt"])
    optional_params = frozenset(["num_inference_steps", "num_images_per_prompt", "latents"])
    expected_workflow_blocks = SOLARVISION_TEXT2IMAGE_WORKFLOWS

    def get_pipeline(self, components_manager=None, torch_dtype=torch.float32):
        pipe = self.pipeline_blocks_class().init_pipeline(components_manager=components_manager)
        pipe.update_components(**get_dummy_components())
        pipe.to(dtype=torch_dtype)
        pipe.set_progress_bar_config(disable=None)
        return pipe

    def get_dummy_inputs(self, seed=0):
        generator = torch.Generator(device="cpu").manual_seed(seed)
        return {
            "prompt": "A painting of a squirrel eating a burger",
            "negative_prompt": "",
            "generator": generator,
            "num_inference_steps": 2,
            "height": 32,
            "width": 32,
            "guidance_scale": 4.0,
            "output_type": "pt",
        }

    @pytest.mark.skip(reason="SolarVision has no published modular pipeline checkpoint yet.")
    def test_load_expected_components_from_pretrained(self, tmp_path):
        pass

    @pytest.mark.skip(reason="auto_cpu_offload requires mem_get_info not available on all devices.")
    def test_components_auto_cpu_offload_inference_consistent(self):
        pass
