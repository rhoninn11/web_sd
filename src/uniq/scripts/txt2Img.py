
from core.utils.utils import pil2simple_data
from core.utils.utils import simple_data2pil

import torch, time
from diffusers import (
    StableDiffusionPipeline,
    DDIMScheduler
)

# ale będzie trzeba rozwarzyć co zrobić jak są DWA
DEVICE = "cuda"
NAME = "txt2img"

def init_txt2img_pipeline(device=DEVICE):
    model_id = "stabilityai/stable-diffusion-2-1-base"
    scheduler = DDIMScheduler.from_pretrained(model_id, subfolder="scheduler")
    pipe_txt2img = StableDiffusionPipeline.from_pretrained(model_id, scheduler=scheduler, torch_dtype=torch.float16)
    pipe_txt2img = pipe_txt2img.to(device)
    return pipe_txt2img

pipeline = []

def init_generator(seed, device=DEVICE):
    g_cuda = torch.Generator(device=device)
    g_cuda.manual_seed(seed)
    return g_cuda

def txt2img(request_data, out_queue, step_callback=None, device=DEVICE):
    
    if len(pipeline) == 0:
        print(f"+++ txt2img initialization")
        pipeline.append(init_txt2img_pipeline(device))
    
    tic = time.perf_counter()
     
    config = request_data[NAME]["config"]
    print(f"+++ txt2img config: {config}")
    pipe_parameters = { 
        "prompt": config["prompt"],
        "negative_prompt": config["prompt_negative"],
        "generator": init_generator(config["seed"], device),
        "callback": step_callback,
        }

    script_pipeline = pipeline[0]
    pipe_result = script_pipeline(**pipe_parameters)

    out_img = pipe_result.images[0]
    request_data[NAME] = { "img": pil2simple_data(out_img) }
    
    toc = time.perf_counter()
    processing_time = toc - tic
    # later add to timing

    out_queue.queue_item(request_data)