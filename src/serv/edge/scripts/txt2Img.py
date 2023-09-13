
from core.utils.utils import pil2simple_data
from core.utils.utils import simple_data2pil

from serv.edge.scripts.common import init_generator
from diffusers import StableDiffusionXLPipeline


NAME = "txt2img"

def init_txt2img_pipeline(base_pipeline: StableDiffusionXLPipeline, device):
    pipe_txt2img = StableDiffusionXLPipeline(
        vae=base_pipeline.vae,
        unet=base_pipeline.unet,
        tokenizer=base_pipeline.tokenizer,
        tokenizer_2=base_pipeline.tokenizer_2,
        text_encoder=base_pipeline.text_encoder,
        text_encoder_2=base_pipeline.text_encoder_2,
        scheduler=base_pipeline.scheduler,
    )
    pipe_txt2img = pipe_txt2img.to(device)
    return pipe_txt2img

pipeline = []


def pipeline_sync(base_pipeline: StableDiffusionXLPipeline, device):
    if len(pipeline) == 0:
        print(f"+++ stub txt2img from base pipeline")
        new_pipeline = init_txt2img_pipeline(base_pipeline, device)
        pipeline.append(new_pipeline)

def config_run(request, step_callback, device, src_data, run_it):
    config = request["config"]
    metadata = request["metadata"]

    run_in = { 
        "prompt": config["prompt"],
        "negative_prompt": config["prompt_negative"],
        
        "generator": init_generator(config["seed"] + run_it, device),
        "callback": step_callback,
        "num_inference_steps": config["steps"],
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
        "bulk": {}
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

def txt2img(request_data, out_queue, step_callback=None, base_pipeline=None, device=None):
    pipeline_sync(base_pipeline, device)
    
    txt2img = request_data[NAME]
    v_run_config = config_runs(txt2img, step_callback, device)

    pipeline_run = pipeline[0]
    for run_in, run_out in v_run_config:

        run_result = pipeline_run(**run_in)
        out_img = run_result.images[0]
        run_out["bulk"]["img"] = pil2simple_data(out_img)

        result = { NAME: run_out }
        out_queue.queue_item(result)

    
