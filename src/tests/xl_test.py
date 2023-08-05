import time
from diffusers import DiffusionPipeline
import torch

print(torch.__version__)
pipe = DiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16, use_safetensors=True, variant="fp16")
# pipe.unet = torch.compile(pipe.unet, mode="reduce-overhead", fullgraph=True)
pipe.to("cuda")

# if using torch < 2.0
# pipe.enable_xformers_memory_efficient_attention()

prompt = "An astronaut riding a green horse, hotorealistic dream"
print(f"+++ processing prompt: {prompt}")
tic = time.perf_counter()
image = pipe(prompt=prompt).images[0]
toc = time.perf_counter()
print(f"+++ processing time: {toc - tic:.2f}s")

image.save("fs/out/astronaut.png")