
from core.utils.utils import pil2simple_data
from core.utils.utils import simple_data2pil

# model_id = "stabilityai/stable-diffusion-2-base"
def img2img(pipeline, realtime_data, out_queue):
    
    init_img = simple_data2pil(realtime_data["img"])
    config_data = realtime_data["config"]

    prompt = config_data["prompt"]
    neg_prompt = config_data["prompt_negative"]
    power = config_data["power"]
    pipe_result = pipeline(prompt, init_img, 
        strength=power, negative_prompt=neg_prompt)
    
    out_img = pipe_result.images[0]   

    out_queue.queue_item({"img2img": {
        "img": pil2simple_data(out_img)
    }})