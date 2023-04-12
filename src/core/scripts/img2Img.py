
from core.utils.utils import pil2simple_data
from core.utils.utils import simple_data2pil

import torch, time
from diffusers import (
    StableDiffusionImg2ImgPipeline,
    DDIMScheduler
)

def init_img2img_pipeline():
    model_id = "stabilityai/stable-diffusion-2-base"
    scheduler = DDIMScheduler.from_pretrained(model_id, subfolder="scheduler")
    pipe_img2img = StableDiffusionImg2ImgPipeline.from_pretrained(model_id, scheduler=scheduler, torch_dtype=torch.float16)
    pipe_img2img = pipe_img2img.to("cuda")
    return pipe_img2img

pipeline = []

def img2img(request_data, out_queue):
    
    if len(pipeline) == 0:
        print(f"+++ img2img initialization")
        pipeline.append(init_img2img_pipeline())
    
    tic = time.perf_counter()
    img2img_data = request_data["img2img"]
    init_img = simple_data2pil(img2img_data["img"])
    config_data = img2img_data["config"]

    prompt = config_data["prompt"]
    neg_prompt = config_data["prompt_negative"]
    power = config_data["power"]

    script_pipeline = pipeline[0]
    pipe_result = script_pipeline(prompt, init_img, 
        strength=power, negative_prompt=neg_prompt)
    
    out_img = pipe_result.images[0]

    request_data["img2img"] = { "img": pil2simple_data(out_img) }
    toc = time.perf_counter()
    processing_time = toc - tic
    # later add to timing

    out_queue.queue_item(request_data)