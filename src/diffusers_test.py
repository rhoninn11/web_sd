import torch
from PIL import Image
from diffusers import (
    StableDiffusionPipeline,
    StableDiffusionImg2ImgPipeline,
    DDIMScheduler
)

model_id = "stabilityai/stable-diffusion-2-base"

# Use the Euler scheduler here instead
scheduler = DDIMScheduler.from_pretrained(model_id, subfolder="scheduler")
pipe_img2img = StableDiffusionImg2ImgPipeline.from_pretrained(model_id, scheduler=scheduler, torch_dtype=torch.float16)
pipe_img2img = pipe_img2img.to("cuda")

prompt = "steve carell chilling while he is in fantasy realm"
init_img_name = "inputs/init_img_512_512.png"
init_img = Image.open(init_img_name)
init_img_size = init_img.size
print(f"+++ image size: {init_img_size}")

out_img_name = "outputs/out_img.png"
pipe_result = pipe_img2img(prompt, init_img, strength=0.8)
out_img = pipe_result.images[0]   
out_img.save(out_img_name)