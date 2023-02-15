import PIL
import requests
import torch
import os

from io import BytesIO
from diffusers import StableDiffusionInpaintPipeline

def download_image(url):
    response = requests.get(url)
    return PIL.Image.open(BytesIO(response.content)).convert("RGB")

img_url = "https://raw.githubusercontent.com/CompVis/latent-diffusion/main/data/inpainting_examples/overture-creations-5sI6fQgYIuo.png"
mask_url = "https://raw.githubusercontent.com/CompVis/latent-diffusion/main/data/inpainting_examples/overture-creations-5sI6fQgYIuo_mask.png"

init_image = download_image(img_url).resize((512, 512))
mask_image = download_image(mask_url).resize((512, 512))

pipe = StableDiffusionInpaintPipeline.from_pretrained("runwayml/stable-diffusion-inpainting", torch_dtype=torch.float16)
pipe = pipe.to("cuda")

prompt = "Face of a yellow cat, high resolution, sitting on a park bench"

image = pipe(prompt=prompt, image=init_image, mask_image=mask_image).images[0]
if not os.path.isdir("./tmp"):
    os.mkdir("./tmp")

print(f"init size: {init_image.size} {init_image.mode}")
print(f"mask size: {mask_image.size} {mask_image.mode}")
init_image.save("./tmp/init_img.png")
mask_image.save("./tmp/mask_img.png")
image.save("./tmp/result_png.png")