# coding=utf-8
# Copyright 2026 HuggingFace Inc.
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
from transformers import AutoTokenizer, Mistral3Config, Mistral3Model

from diffusers import (
    AutoencoderKLFlux2,
    FlowMatchEulerDiscreteScheduler,
    SolarVisionAutoBlocks,
    SolarVisionModularPipeline,
    SolarVisionTransformer2DModel,
)
from diffusers.guiders import ClassifierFreeGuidance
from diffusers.image_processor import VaeImageProcessor
from tests.modular_pipelines.test_modular_pipelines_common import ModularPipelineTesterMixin


SOLARVISION_WORKFLOWS = {
    "text2image": [
        ("text_encoder", "SolarVisionTextEncoderStep"),
        ("denoise.input", "SolarVisionTextInputStep"),
        ("denoise.set_timesteps", "SolarVisionSetTimestepsStep"),
        ("denoise.prepare_latents", "SolarVisionPrepareLatentsStep"),
        ("denoise.denoise", "SolarVisionDenoiseStep"),
        ("decode", "SolarVisionVaeDecoderStep"),
    ],
}


def get_dummy_components():
    from diffusers.modular_pipelines.solarvision.modular_pipeline import SolarVisionPachifier

    torch.manual_seed(0)
    transformer = SolarVisionTransformer2DModel(
        hidden_size=16,
        num_attention_heads=1,
        num_layers=1,
        ffn_hidden_size=16,
        in_channels=64,
        out_channels=64,
        patch_size=1,
        text_in_dim=16,
        rope_theta=256,
        rope_axes_dim=(8, 4, 4),
        eps=1e-6,
        qk_layernorm=True,
    )

    config = Mistral3Config(
        text_config={
            "model_type": "mistral",
            "vocab_size": 131072,
            "hidden_size": 16,
            "intermediate_size": 37,
            "max_position_embeddings": 512,
            "num_attention_heads": 4,
            "num_hidden_layers": 1,
            "num_key_value_heads": 2,
            "rms_norm_eps": 1e-05,
            "rope_theta": 1000000000.0,
            "sliding_window": None,
            "bos_token_id": 2,
            "eos_token_id": 3,
            "pad_token_id": 4,
        },
        vision_config={
            "model_type": "pixtral",
            "hidden_size": 16,
            "num_hidden_layers": 1,
            "num_attention_heads": 4,
            "intermediate_size": 37,
            "image_size": 30,
            "patch_size": 6,
            "num_channels": 3,
        },
        bos_token_id=2,
        eos_token_id=3,
        pad_token_id=4,
        model_dtype="mistral3",
        image_seq_length=4,
        vision_feature_layer=-1,
        image_token_index=1,
    )
    torch.manual_seed(0)
    text_encoder = Mistral3Model(config)
    tokenizer = AutoTokenizer.from_pretrained("hf-internal-testing/Mistral-Small-3.1-24B-Instruct-2503-only-processor")

    torch.manual_seed(0)
    vae = AutoencoderKLFlux2(
        sample_size=32,
        in_channels=3,
        out_channels=3,
        down_block_types=("DownEncoderBlock2D",),
        up_block_types=("UpDecoderBlock2D",),
        block_out_channels=(4,),
        layers_per_block=1,
        latent_channels=16,
        patch_size=(2, 2),
        norm_num_groups=1,
        use_quant_conv=False,
        use_post_quant_conv=False,
    )

    scheduler = FlowMatchEulerDiscreteScheduler()
    guider = ClassifierFreeGuidance.from_config({"guidance_scale": 4.0})
    pachifier = SolarVisionPachifier.from_config({"patch_size": 2})
    image_processor = VaeImageProcessor.from_config({"vae_scale_factor": 16})

    return {
        "transformer": transformer,
        "text_encoder": text_encoder,
        "tokenizer": tokenizer,
        "vae": vae,
        "scheduler": scheduler,
        "guider": guider,
        "pachifier": pachifier,
        "image_processor": image_processor,
    }


class TestSolarVisionModularPipelineFast(ModularPipelineTesterMixin):
    pipeline_class = SolarVisionModularPipeline
    pipeline_blocks_class = SolarVisionAutoBlocks
    pretrained_model_name_or_path = "hf-internal-testing/tiny-solarvision-modular-pipe"

    params = frozenset(["prompt", "height", "width"])
    batch_params = frozenset(["prompt"])
    optional_params = frozenset(["num_inference_steps", "num_images_per_prompt", "latents"])
    expected_workflow_blocks = SOLARVISION_WORKFLOWS

    def get_pipeline(self, components_manager=None, torch_dtype=torch.float32):
        pipe = self.pipeline_blocks_class().init_pipeline(components_manager=components_manager)
        pipe.update_components(**get_dummy_components())
        pipe.to(dtype=torch_dtype)
        pipe.set_progress_bar_config(disable=None)
        return pipe

    def get_dummy_inputs(self, seed=0):
        generator = self.get_generator(seed)
        return {
            "prompt": "A painting of a squirrel eating a burger",
            "generator": generator,
            "num_inference_steps": 2,
            "height": 32,
            "width": 32,
            "output_type": "pt",
        }

    def test_inference_batch_single_identical(self):
        super().test_inference_batch_single_identical(expected_max_diff=5e-3)
