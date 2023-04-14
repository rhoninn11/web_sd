
from core.utils.utils import pil2simple_data
from core.utils.utils import simple_data2pil

import torch, time
from PIL import Image, ImageDraw
from diffusers import (
    StableDiffusionInpaintPipeline,
    DDIMScheduler
)

DEVICE = "cuda"
NAME = "inpaint"

def init_inpt_img2img_pipeline():
    model_id = "stabilityai/stable-diffusion-2-inpainting"
    scheduler = DDIMScheduler.from_pretrained(model_id, subfolder="scheduler")
    pipe_img2img = StableDiffusionInpaintPipeline.from_pretrained(model_id, scheduler=scheduler, torch_dtype=torch.float16)
    pipe_img2img = pipe_img2img.to(DEVICE)
    return pipe_img2img

pipeline = []

def init_generator(seed):
    g_cuda = torch.Generator(device=DEVICE)
    g_cuda.manual_seed(seed)
    return g_cuda

def mask_image(img):
    width, height = img.size
    
    mask_image = Image.new('RGB', (width, height), color='black')
    mask_draw_proxy = ImageDraw.Draw(mask_image)

    size = int(width/2)
    x0 = int(width/2) - size
    x1 = int(width/2) + size
    y0 = int(height/2) - size
    y1 = int(height/2) + size
    c_shape = (x0, y0, x1, y1)
    mask_draw_proxy.ellipse(c_shape, fill='white')

    return mask_image

def inpaint(request_data, out_queue):
    
    if len(pipeline) == 0:
        print(f"+++ inpaint initialization")
        pipeline.append(init_inpt_img2img_pipeline())
    
    tic = time.perf_counter()

    config = request_data[NAME]["config"]
    init_img = simple_data2pil(request_data[NAME]["img"])

    pipeline_params = {
        "image": init_img,
        "prompt": config["prompt"],
        # "strength": config["power"],
        "mask_image": mask_image(init_img),
        "negative_prompt": config["prompt_negative"],
    }

    pipe_result = pipeline[0](**pipeline_params)
    out_img = pipe_result.images[0]
    

    request_data[NAME] = { "img": pil2simple_data(out_img) }
    toc = time.perf_counter()
    processing_time = toc - tic
    # later add to timing

    out_queue.queue_item(request_data)