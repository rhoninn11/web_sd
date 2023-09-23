
from core.utils.utils import pil2simple_data
from core.utils.utils import simple_data2pil

from serv.edge.scripts.common import init_generator
from diffusers import StableDiffusionXLInpaintPipeline, StableDiffusionXLPipeline, AutoPipelineForInpainting


NAME = "inpaint"

def init_inpaint_img2img_pipeline(base_pipeline: StableDiffusionXLPipeline, refiner_pipeline: StableDiffusionXLPipeline, device):
    pipe_inpaint = StableDiffusionXLInpaintPipeline(
        vae=base_pipeline.vae,
        unet=base_pipeline.unet,
        tokenizer=base_pipeline.tokenizer,
        tokenizer_2=base_pipeline.tokenizer_2,
        text_encoder=base_pipeline.text_encoder,
        text_encoder_2=base_pipeline.text_encoder_2,
        scheduler=base_pipeline.scheduler,
    )
    pipe_inpaint.enable_vae_tiling()

    pipe_inpaint_refiner = AutoPipelineForInpainting.from_pipe(refiner_pipeline)
    pipe_inpaint_refiner.enable_vae_tiling()
    return pipe_inpaint, pipe_inpaint_refiner

pipeline = []

def pipeline_sync(base_pipeline: StableDiffusionXLPipeline, refiner_pipeline: StableDiffusionXLPipeline, device):
    if len(pipeline) == 0:
        print(f"+++ stub inpaint from base pipeline")
        inpaint_pipes = init_inpaint_img2img_pipeline(base_pipeline, refiner_pipeline, device)
        pipeline.append(inpaint_pipes)

def config_run(request, step_callback, device, src_data, run_it):
    bulk = request["bulk"]
    config = request["config"]
    metadata = request["metadata"]

    expert_switch = 0.75
    config_power = config["power"]
    if config_power < (1.0 - expert_switch):
        expert_switch = 1 - config_power

    mask = simple_data2pil(bulk["mask"])

    run_in = {
        "strength": config_power,
        "image": simple_data2pil(bulk["img"]),
        "mask_image": mask,

        
        "prompt": config["prompt"],
        "negative_prompt": config["prompt_negative"],

        "generator": init_generator(config["seed"] + run_it, device),
        "callback": step_callback,
        "num_inference_steps": config["steps"],
        # for moe 
        "output_type": "latent",
        "denoising_end": expert_switch,
    }
    
    run_in_ref = {
        "strength": config_power,
        "image": "blanc yet",
        "mask_image": mask,

        "prompt": config["prompt"],
        "negative_prompt": config["prompt_negative"],
        
        "generator": init_generator(config["seed"] + run_it, device),
        "callback": step_callback,
        "num_inference_steps": config["steps"],
        #for moe
        "denoising_start": expert_switch,
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

    return (run_in, run_in_ref), run_out

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

def inpaint(request_data, out_queue, step_callback=None, src_pipelines=None, device=None):
    pipeline_sync(src_pipelines[0], src_pipelines[1], device)

    inpaint = request_data[NAME]
    run_config_v = config_runs(inpaint, step_callback, device)

    pipeline_run, refiner_run = pipeline[0]
    for pipeline_ins, run_out in run_config_v:
        run_in, run_in_ref = pipeline_ins
        
        run_result = pipeline_run(**run_in)
        run_in_ref["image"] = run_result.images[0]

        run_result = refiner_run(**run_in_ref)
        out_img = run_result.images[0]
        run_out["bulk"]["img"] = pil2simple_data(out_img)

        result = { NAME: run_out }
        out_queue.queue_item(result)