
from core.utils.utils import pil2simple_data
from core.utils.utils import simple_data2pil

import torch, time
from diffusers import (
    StableDiffusionPipeline,
    DDIMScheduler
)

# ale będzie trzeba rozwarzyć co zrobić jak są DWA
DEVICE = "cuda"

def init_txt2img_pipeline(model_id):
    model_id = "stabilityai/stable-diffusion-2-1-base"
    scheduler = DDIMScheduler.from_pretrained(model_id, subfolder="scheduler")
    pipe_img2img = StableDiffusionPipeline.from_pretrained(model_id, scheduler=scheduler, torch_dtype=torch.float16)
    pipe_img2img = pipe_img2img.to(DEVICE)
    return pipe_img2img

pipeline = []

def init_generator(seed):
    g_cuda = torch.Generator(device=DEVICE)
    g_cuda.manual_seed(seed)
    return g_cuda

def init_generator(seeds):
    generators = []
    for seed in seeds:
        generators.append(init_generator(seed))
    return generators

def txt2img(request_data, out_queue):
    
    if len(pipeline) == 0:
        print(f"+++ img2img initialization")
        pipeline.append(init_txt2img_pipeline())
    
    tic = time.perf_counter()
    img2img_data = request_data["txt2img"]
    config_data = img2img_data["config"]

    config = { 
        "prompt": config_data["prompt"],
        "negative_prompt": config_data["prompt_negative"],
        "generator": init_generator(42),
        }

    script_pipeline = pipeline[0]
    pipe_result = script_pipeline(**config)

    out_img = pipe_result.images[0]
    request_data["config"] = { "img": pil2simple_data(out_img) }
    
    toc = time.perf_counter()
    processing_time = toc - tic
    # later add to timing

    out_queue.queue_item(request_data)