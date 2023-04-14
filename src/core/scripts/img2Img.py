
from core.utils.utils import pil2simple_data
from core.utils.utils import simple_data2pil

import torch, time
from diffusers import (
    StableDiffusionImg2ImgPipeline,
    DDIMScheduler
)

# ale będzie trzeba rozwarzyć co zrobić jak są DWA
DEVICE = "cuda"
NAME = "img2img"

def init_img2img_pipeline():
    model_id = "stabilityai/stable-diffusion-2-base"
    scheduler = DDIMScheduler.from_pretrained(model_id, subfolder="scheduler")
    pipe_img2img = StableDiffusionImg2ImgPipeline.from_pretrained(model_id, scheduler=scheduler, torch_dtype=torch.float16)
    pipe_img2img = pipe_img2img.to(DEVICE)
    return pipe_img2img

pipeline = []

def init_generator(seed):
    g_cuda = torch.Generator(device=DEVICE)
    g_cuda.manual_seed(seed)
    return g_cuda

def img2img(request_data, out_queue):
    
    if len(pipeline) == 0:
        print(f"+++ img2img initialization")
        pipeline.append(init_img2img_pipeline())
    
    tic = time.perf_counter()
    config = request_data[NAME]["config"]

    pipe_parameters = { 
        "image": simple_data2pil(request_data[NAME]["img"]),
        "prompt": config["prompt"],
        "strength": config["power"],
        "negative_prompt": config["prompt_negative"],
        "generator": init_generator(42),
        }

    script_pipeline = pipeline[0]
    pipe_result = script_pipeline(**pipe_parameters)
    
    out_img = pipe_result.images[0]

    request_data[NAME] = { "img": pil2simple_data(out_img) }
    toc = time.perf_counter()
    processing_time = toc - tic
    # later add to timing

    out_queue.queue_item(request_data)