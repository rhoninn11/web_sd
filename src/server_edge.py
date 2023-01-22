import torch, time

from core.threads.DiffusionServerThread import DiffusionServerThread
from core.threads.SDiffusionThread import SDiffusionThread
from core.threads.GradioInterface import GradioInterface

from core.system.MultiThreadingApp import MultiThreadingApp
 
from diffusers import (
    StableDiffusionImg2ImgPipeline,
    DDIMScheduler
)

# model_id = "stabilityai/stable-diffusion-2-base"
def init_pipeline(model_id):
    # Use the Euler scheduler here instead
    scheduler = DDIMScheduler.from_pretrained(model_id, subfolder="scheduler")
    pipe_img2img = StableDiffusionImg2ImgPipeline.from_pretrained(model_id, scheduler=scheduler, torch_dtype=torch.float16)
    pipe_img2img = pipe_img2img.to("cuda")
    return pipe_img2img

class EdgeServer(MultiThreadingApp):
    def __init__(self):
        MultiThreadingApp.__init__(self)
    
    def run(self):
        print(f"+++ app start")
        model_id = "stabilityai/stable-diffusion-2-base"
        pipeline = init_pipeline(model_id)
        print(f"+++ model loaded")

        stableD_thread = SDiffusionThread(pipeline)
        tcp_thread = DiffusionServerThread()

        tcp_thread.bind_worker(stableD_thread)

        # gradio thread block main thread - must be last on the list
        threads = [stableD_thread, tcp_thread]
        self.thread_launch(threads)

        print("+++ server exit")


def main():
    edge_server = EdgeServer()
    edge_server.run()

main()