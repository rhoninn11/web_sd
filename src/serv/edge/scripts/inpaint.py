
from core.utils.utils import pil2simple_data
from core.utils.utils import simple_data2pil

import torch, time
from PIL import Image, ImageDraw
from diffusers import StableDiffusionXLInpaintPipeline


DEVICE = "cuda"
NAME = "inpaint"

def init_inpt_img2img_pipeline(device=DEVICE):
    model_id = "stabilityai/stable-diffusion-xl-base-1.0"
    pipe_inpaint = StableDiffusionXLInpaintPipeline.from_pretrained(model_id, torch_dtype=torch.float16, use_safetensors=True, variant="fp16")
    pipe_inpaint = pipe_inpaint.to(device)
    return pipe_inpaint

pipeline = []

def init_generator(seed, device=DEVICE):
    g_cuda = torch.Generator(device=device)
    g_cuda.manual_seed(seed)
    return g_cuda

def pipeline_sync(device):
    if len(pipeline) == 0:
        print(f"+++ inpaint initialization")
        pipeline.append(init_inpt_img2img_pipeline(device))


def config_run(request, step_callback, device, src_data, run_it):
    bulk = request["bulk"]
    config = request["config"]
    metadata = request["metadata"]

    run_in = {
        "strength": config["power"],
        "image": simple_data2pil(bulk["img"]),
        "mask_image": simple_data2pil(bulk["mask"]),
        "prompt": config["prompt"],
        "negative_prompt": config["prompt_negative"],
        "generator": init_generator(config["seed"] + run_it, device),
        "callback": step_callback,
    }
    
    run_out = {
        "config": {
            "prompt": config["prompt"],
            "negative_prompt": config["prompt_negative"],
            "seed": config["seed"] + run_it,
            "power": config["power"],
            "samples": 1,
        },
        "metadata": metadata,
        "bulk":{},
    }

    return run_in, run_out

def config_runs(request, step_callback, device):
    config = request["config"]
    runs_count = 1
    if "samples" in config:
        runs_count = config["samples"]
    
    v_run_config = []
    for i in range(runs_count):
        run_in_out = config_run(request, step_callback, device, None, i)
        v_run_config.append(run_in_out)
    
    return v_run_config

def inpaint(request_data, out_queue, step_callback=None, device=DEVICE):
    pipeline_sync(device)

    inpaint = request_data[NAME]
    run_config_v = config_runs(inpaint, step_callback, device)

    pipeline_run = pipeline[0]
    for run_in, run_out in run_config_v:
        
        run_result = pipeline_run(**run_in)
        out_img = run_result.images[0]
        run_out["bulk"]["img"] = pil2simple_data(out_img)

        result = { NAME: run_out }
        out_queue.queue_item(result)