
from core.utils.utils import pil2simple_data
from core.utils.utils import simple_data2pil

from serv.edge.scripts.common import init_generator
from diffusers import StableDiffusionXLImg2ImgPipeline, StableDiffusionXLPipeline


NAME = "txt2img"

def init_txt2img_pipeline(base_pipeline: StableDiffusionXLPipeline, refiner_pipeline: StableDiffusionXLPipeline, device):
    pipe_txt2img = base_pipeline
    pipe_txt2img.enable_vae_tiling()
    refiner_pipeline = refiner_pipeline
    refiner_pipeline.enable_vae_tiling()

    return pipe_txt2img, refiner_pipeline

pipeline = []


def pipeline_sync(base_pipeline: StableDiffusionXLPipeline, refiner_pipeline: StableDiffusionXLPipeline, device):
    if len(pipeline) == 0:
        print(f"+++ stub txt2img from base pipeline")
        new_pipeline = init_txt2img_pipeline(base_pipeline, refiner_pipeline, device)
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
        # for moe
        "output_type": "latent",
        "denoising_end": 0.75,
        }
    
    run_in_ref = { 
        "prompt": config["prompt"],
        "negative_prompt": config["prompt_negative"],
        
        "generator": init_generator(config["seed"] + run_it, device),
        "callback": step_callback,
        "num_inference_steps": config["steps"],
        # for moe
        "denoising_start": 0.75,
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

    return (run_in, run_in_ref), run_out

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

def txt2img(request_data, out_queue, step_callback=None, src_pipelines=None, device=None):
    pipeline_sync(src_pipelines[0], src_pipelines[1], device)
    
    txt2img = request_data[NAME]
    v_run_config = config_runs(txt2img, step_callback, device)

    pipeline_run, refiner_run = pipeline[0]
    for pipeline_ins, run_out in v_run_config:
        run_in, run_in_ref = pipeline_ins

        run_result = pipeline_run(**run_in)
        run_in_ref["image"] = run_result.images[0]

        run_result = refiner_run(**run_in_ref)
        out_img = run_result.images[0]

        run_out["bulk"]["img"] = pil2simple_data(out_img)
        result = { NAME: run_out }
        out_queue.queue_item(result)

    
