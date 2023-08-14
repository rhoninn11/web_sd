
from core.utils.utils import pil2simple_data
from core.utils.utils import simple_data2pil

import os
import torch, time
from diffusers import StableDiffusionXLPipeline


# ale będzie trzeba rozwarzyć co zrobić jak są DWA
DEVICE = "cuda"
NAME = "txt2img"

def init_txt2img_pipeline(device=DEVICE):
    access_token = os.getenv('HF_TOKEN')
    print(f'HF_TOKEN: {access_token}')
    model_id = "stabilityai/stable-diffusion-xl-base-1.0"
    pipe_txt2img = StableDiffusionXLPipeline.from_pretrained(model_id, torch_dtype=torch.float16, use_safetensors=True, variant="fp16")
    pipe_txt2img = pipe_txt2img.to(device)
    return pipe_txt2img

pipeline = []

def init_generator(seed, device=DEVICE):
    g_cuda = torch.Generator(device=device)
    seed = seed % 100
    g_cuda.manual_seed(seed)
    return g_cuda

def pipeline_sync(device):
    if len(pipeline) == 0:
        print(f"+++ txt2img initialization")
        pipeline.append(init_txt2img_pipeline(device))

def config_run(request, step_callback, device, src_data, run_it):
    config = request["config"]
    metadata = request["metadata"]

    run_in = { 
        "prompt": config["prompt"],
        "negative_prompt": config["prompt_negative"],
        "generator": init_generator(config["seed"] + run_it, device),
        "callback": step_callback,
        "num_inference_steps": 10,
        }
    
    run_out = {
        "config": {
            "prompt": config["prompt"],
            "negative_prompt": config["prompt_negative"],
            "seed": config["seed"] + run_it,
        },
        "metadata": metadata
    }

    return run_in, run_out

def config_runs(request, step_callback, device):
    config = request["config"]
    runs_count = 4
    if "samples" in config:
        runs_count = config["samples"]
    
    v_run_config = []
    for i in range(runs_count):
        run_in_out = config_run(request, step_callback, device, None, i)
        v_run_config.append(run_in_out)
    
    return v_run_config

def txt2img(request_data, out_queue, step_callback=None, device=DEVICE):
    pipeline_sync(device)
    
    txt2img = request_data[NAME]
    v_run_config = config_runs(txt2img, step_callback, device)

    pipeline_run = pipeline[0]
    for run_in, run_out in v_run_config:

        run_result = pipeline_run(**run_in)
        out_img = run_result.images[0]
        run_out["img"] = pil2simple_data(out_img)

        result = { NAME: run_out }
        out_queue.queue_item(result)

    
