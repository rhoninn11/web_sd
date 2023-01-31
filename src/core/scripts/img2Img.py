
from core.utils.utils import pil2simple_data
from core.utils.utils import simple_data2pil

import time

# model_id = "stabilityai/stable-diffusion-2-base"
def img2img(pipeline, request_data, out_queue):
    
    
    tic = time.perf_counter()
    img2img_data = request_data["img2img"]
    init_img = simple_data2pil(img2img_data["img"])
    config_data = img2img_data["config"]

    prompt = config_data["prompt"]
    neg_prompt = config_data["prompt_negative"]
    power = config_data["power"]
    pipe_result = pipeline(prompt, init_img, 
        strength=power, negative_prompt=neg_prompt)
    
    out_img = pipe_result.images[0]

    request_data["img2img"] = { "img": pil2simple_data(out_img) }
    toc = time.perf_counter()
    processing_time = toc - tic
    # later add to timing

    out_queue.queue_item(request_data)