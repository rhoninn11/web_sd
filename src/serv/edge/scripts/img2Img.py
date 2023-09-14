
from core.utils.utils import pil2simple_data
from core.utils.utils import simple_data2pil

from serv.edge.scripts.common import init_generator
from diffusers import StableDiffusionXLImg2ImgPipeline, StableDiffusionXLPipeline


NAME = "img2img"

def init_img2img_pipeline(base_pipeline: StableDiffusionXLPipeline, device):
    pipe_img2img = StableDiffusionXLImg2ImgPipeline(
        vae=base_pipeline.vae,
        unet=base_pipeline.unet,
        tokenizer=base_pipeline.tokenizer,
        tokenizer_2=base_pipeline.tokenizer_2,
        text_encoder=base_pipeline.text_encoder,
        text_encoder_2=base_pipeline.text_encoder_2,
        scheduler=base_pipeline.scheduler,
    )
    pipe_img2img = pipe_img2img.to(device)
    pipe_img2img.enable_vae_tiling()
    return pipe_img2img

pipeline = []


def pipeline_sync(base_pipeline: StableDiffusionXLPipeline, device):
    if len(pipeline) == 0:
        print(f"+++ stub img2img pipeline from base pipeline")
        new_pipeline = init_img2img_pipeline(base_pipeline, device)
        pipeline.append(new_pipeline)


def config_run(request, step_callback, device, src_data, run_it):
    bulk = request["bulk"]
    config = request["config"]
    metadata = request["metadata"]
    print(f"+++ img2img config_run: {config}")
    run_in = {
        "strength": config["power"],
        "image": simple_data2pil(bulk["img"]),
        
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

def img2img(request_data, out_queue, step_callback=None, base_pipeline=None, device=None):
    pipeline_sync(base_pipeline, device)

    img2img = request_data[NAME]
    run_config_v = config_runs(img2img, step_callback, device)

    pipeline_run = pipeline[0]
    for run_in, run_out in run_config_v:
        
        run_result = pipeline_run(**run_in)
        out_img = run_result.images[0]
        run_out["bulk"]["img"] = pil2simple_data(out_img)

        result = { NAME: run_out }
        out_queue.queue_item(result)