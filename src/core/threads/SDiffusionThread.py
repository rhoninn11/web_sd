
import time

from core.utils.utils_thread import ThreadWrap, pipe_queue
from core.scripts.txt2Img import txt2img
from core.scripts.img2Img import img2img
from core.scripts.inpt_img2Img import inpt_img2img

class SDiffusionThread(ThreadWrap):
    def __init__(self):
        ThreadWrap.__init__(self)
        self.config_pipe = pipe_queue("config")
        # config będzie przychodził wraz z
        self.config = {
            "prompt": "stone marble covered with floral patterns chilling in fantasy realm",
            "prompt_negative": "",
            "power": 0.8
        }
        
    def new_config(self, new_config):
        self.config_pipe.queue_item(new_config)
    
    def check_for_config_update(self):
        while self.config_pipe.queue_len():
            new_config = self.config_pipe.dequeue_item()
            self.config = new_config

    def process_request(self, request):
        if "txt2img" in request:
            txt2img(request, self.out_queue)
        if "img2img" in request:
            img2img(request, self.out_queue)
        if "inpt_img2img" in request:
            inpt_img2img(request, self.out_queue)
        return

    def run(self):
        print(f"+++ stable diffusion thread ready")
        in_queue = self.in_queue
        while self.run_cond:
            if in_queue.queue_len() == 0:
                time.sleep(0.1)
                continue
            
            new_request = in_queue.dequeue_item()
            self.process_request(new_request)
