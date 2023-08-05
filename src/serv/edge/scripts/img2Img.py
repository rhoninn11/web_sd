
from core.utils.utils import pil2simple_data
from core.utils.utils import simple_data2pil

import torch, time
from diffusers import StableDiffusionXLImg2ImgPipeline

# ale będzie trzeba rozwarzyć co zrobić jak są DWA
DEVICE = "cuda"
NAME = "img2img"

def init_img2img_pipeline(device=DEVICE):
    model_id = "stabilityai/stable-diffusion-xl-base-1.0"
    pipe_img2img = StableDiffusionXLImg2ImgPipeline.from_pretrained(model_id, torch_dtype=torch.float16, use_safetensors=True, variant="fp16")
    pipe_img2img = pipe_img2img.to(device)
    return pipe_img2img

pipeline = []

def init_generator(seed, device=DEVICE):
    g_cuda = torch.Generator(device=device)
    g_cuda.manual_seed(seed)
    return g_cuda

def pipeline_sync(device):
    if len(pipeline) == 0:
        print(f"+++ img2img initialization")
        pipeline.append(init_img2img_pipeline(device))


def config_run(request, step_callback, device, src_data, run_it):
    bulk = request["bulk"]
    config = request["config"]
    metadata = request["metadata"]

    run_in = {
        "strength": config["power"],
        "image": simple_data2pil(bulk["img"]),
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

def img2img(request_data, out_queue, step_callback=None, device=DEVICE):
    pipeline_sync(device)

    img2img = request_data[NAME]
    run_config_v = config_runs(img2img, step_callback, device)

    pipeline_run = pipeline[0]
    for run_in, run_out in run_config_v:
        
        run_result = pipeline_run(**run_in)
        out_img = run_result.images[0]
        run_out["bulk"]["img"] = pil2simple_data(out_img)

        result = { NAME: run_out }
        out_queue.queue_item(result)