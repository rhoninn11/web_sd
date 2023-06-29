
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

def init_inpt_img2img_pipeline(device=DEVICE):
    model_id = "stabilityai/stable-diffusion-2-inpainting"
    scheduler = DDIMScheduler.from_pretrained(model_id, subfolder="scheduler")
    pipe_img2img = StableDiffusionInpaintPipeline.from_pretrained(model_id, scheduler=scheduler, torch_dtype=torch.float16)
    pipe_img2img = pipe_img2img.to(device)
    return pipe_img2img

pipeline = []

def init_generator(seed, device=DEVICE):
    g_cuda = torch.Generator(device=device)
    g_cuda.manual_seed(seed)
    return g_cuda

def inpaint(request_data, out_queue, step_callback=None, device=DEVICE):
    
    if len(pipeline) == 0:
        print(f"+++ inpaint initialization")
        pipeline.append(init_inpt_img2img_pipeline(device))
    
    tic = time.perf_counter()

    config = request_data[NAME]["config"]
    init_img = simple_data2pil(request_data[NAME]["img"])
    mask_of_img = simple_data2pil(request_data[NAME]["img_mask"])

    pipeline_params = {
        "image": init_img,
        "prompt": config["prompt"],
        "mask_image": mask_of_img,
        # "strength": config["power"],
        "generator": init_generator(config["seed"], device),
        "negative_prompt": config["prompt_negative"],
        "callback": step_callback,
    }

    pipe_result = pipeline[0](**pipeline_params)
    out_img = pipe_result.images[0]
    

    request_data[NAME] = { "img": pil2simple_data(out_img) }
    toc = time.perf_counter()
    processing_time = toc - tic
    # later add to timing

    out_queue.queue_item(request_data)