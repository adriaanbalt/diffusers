<!--Copyright 2026 The HuggingFace Team. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
-->

# SolarVision

SolarVision is a modular text-to-image pipeline built around a flow-matching diffusion transformer, Gemma text encoder, and VAE decoder.

```python
import torch
from diffusers import SolarVisionAutoBlocks, SolarVisionModularPipeline

blocks = SolarVisionAutoBlocks()
pipe = blocks.init_pipeline("path/to/solarvision-diffusers")
pipe.to("cuda", torch_dtype=torch.bfloat16)

images = pipe(
    prompt="A painting of a squirrel eating a burger",
    height=1024,
    width=1024,
    num_inference_steps=30,
    guidance_scale=4.0,
    generator=torch.Generator("cuda").manual_seed(0),
).images
```

## SolarVisionModularPipeline

[[autodoc]] SolarVisionModularPipeline

## SolarVisionAutoBlocks

[[autodoc]] SolarVisionAutoBlocks
