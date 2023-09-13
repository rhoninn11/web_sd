
from serv.edge.scripts.txt2Img import txt2img
from serv.edge.scripts.img2Img import img2img
from serv.edge.scripts.inpaint import inpaint
from serv.edge.base_pipeline import load_base_pipeline
import time

DEVICE = "cuda"

def dummy_script(self, request, out_queue, step_callback=None):
    pass

class ScriptIndex():
    def __init__(self):
        self.scripts = {}
        self.scripts["txt2img"] = txt2img
        self.scripts["img2img"] = img2img
        self.scripts["inpaint"] = inpaint
        self.scripts["progress"] = dummy_script

        self.available_scripts = list(self.scripts.keys())
        self.pipeline_src = None
        self.pipeline_device = None
        

    def get_name_list(self):
        return self.available_scripts
    
    def detect_script_name(self, request):
        for key in self.scripts:
            if key in request:
                return key
            
        return None
    
    def has_script(self, request):
        return True if self.detect_script_name(request) else False
    
    def _script_callback(self, step, timestep, metadata, queue):
        progress = float(f"{(1000-timestep)/1000.0}") # value as string to get rid of tensor
        msg = { 
            "progress": {
                "metadata": metadata,
                "value": progress
            }
        }
        queue.queue_item(msg)

    def get_base_pipeline(self):
        device = "cuda"
        model_id = "stabilityai/stable-diffusion-xl-base-1.0"

        if self.pipeline_src is None:
            self.pipeline_src = load_base_pipeline(model_id, device)
            self.pipeline_device = device

        return self.pipeline_src,  self.pipeline_device

    def run_script(self, request, out_queue):
        script_name = self.detect_script_name(request)
        if script_name:
            script = self.scripts[script_name]
            metadata =  request[script_name]["metadata"]
            cb = lambda step, timestep, _: self._script_callback(step, timestep, metadata, out_queue)
            base_pipe, device = self.get_base_pipeline()
            script(request, out_queue, cb, base_pipe, device)
        return