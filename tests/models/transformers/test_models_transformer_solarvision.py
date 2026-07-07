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

from diffusers import SolarVisionTransformer2DModel
from diffusers.utils.torch_utils import randn_tensor

from ...testing_utils import enable_full_determinism, require_torch_gpu, torch_device
from ..testing_utils import (
    BaseModelTesterConfig,
    ModelTesterMixin,
    TorchCompileTesterMixin,
    TrainingTesterMixin,
)


enable_full_determinism()


class SolarVisionTransformerTesterConfig(BaseModelTesterConfig):
    @property
    def model_class(self):
        return SolarVisionTransformer2DModel

    @property
    def main_input_name(self) -> str:
        return "hidden_states"

    @property
    def output_shape(self) -> tuple:
        return (4, 16, 16)

    @property
    def input_shape(self) -> tuple:
        return (4, 16, 16)

    @property
    def generator(self):
        return torch.Generator("cpu").manual_seed(0)

    def get_init_dict(self) -> dict:
        return {
            "sample_size": 16,
            "patch_size": 2,
            "in_channels": 4,
            "hidden_size": 24,
            "num_layers": 2,
            "num_refiner_layers": 1,
            "num_attention_heads": 3,
            "num_kv_heads": 1,
            "multiple_of": 2,
            "ffn_dim_multiplier": None,
            "norm_eps": 1e-5,
            "scaling_factor": 1.0,
            "axes_dim_rope": (4, 2, 2),
            "axes_lens": (128, 128, 128),
            "cap_feat_dim": 32,
        }

    def get_dummy_inputs(self, batch_size: int = 2) -> dict[str, torch.Tensor]:
        num_channels = 4
        height = width = 16
        embedding_dim = 32
        sequence_length = 16

        return {
            "hidden_states": randn_tensor(
                (batch_size, num_channels, height, width), generator=self.generator, device=torch_device
            ),
            "encoder_hidden_states": randn_tensor(
                (batch_size, sequence_length, embedding_dim), generator=self.generator, device=torch_device
            ),
            "encoder_attention_mask": torch.ones(batch_size, sequence_length, dtype=torch.bool, device=torch_device),
            "timestep": torch.tensor([1.0] * batch_size, device=torch_device),
        }


class TestSolarVisionTransformer(SolarVisionTransformerTesterConfig, ModelTesterMixin):
    pass


class TestSolarVisionTransformerTraining(SolarVisionTransformerTesterConfig, TrainingTesterMixin):
    def test_gradient_checkpointing_is_applied(self):
        super().test_gradient_checkpointing_is_applied(expected_set={"SolarVisionTransformer2DModel"})


class TestSolarVisionTransformerCompile(SolarVisionTransformerTesterConfig, TorchCompileTesterMixin):
    @property
    def different_shapes_for_compilation(self):
        return [(16, 16), (16, 32), (32, 32)]

    @pytest.mark.skip(
        reason="Variable-length text conditioning uses data-dependent sequence lengths, so fullgraph "
        "compilation with error_on_recompile=True is not supported."
    )
    def test_torch_compile_recompilation_and_graph_break(self):
        super().test_torch_compile_recompilation_and_graph_break()

    @pytest.mark.skip(reason="SolarVisionTransformer2DModel has no `_repeated_blocks` set.")
    def test_torch_compile_repeated_blocks(self, recompile_limit=1):
        super().test_torch_compile_repeated_blocks(recompile_limit)

    @require_torch_gpu
    def test_compile_with_group_offloading(self):
        super().test_compile_with_group_offloading()

    @pytest.mark.skip(reason="Fullgraph AoT is broken.")
    def test_compile_works_with_aot(self, tmp_path):
        super().test_compile_works_with_aot(tmp_path)

    @pytest.mark.skip(reason="Variable-length text conditioning is not compatible with fullgraph dynamic shapes.")
    def test_compile_on_different_shapes(self):
        super().test_compile_on_different_shapes()
