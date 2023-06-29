
from uniq.scripts.txt2Img import txt2img
from uniq.scripts.img2Img import img2img
from uniq.scripts.inpaint import inpaint
from uniq.scripts.callback_testing_txt2img import callback_testing_txt2img


class ScriptIndex():
    def __init__(self):
        self.scripts = {}
        self.scripts["txt2img"] = txt2img
        self.scripts["img2img"] = img2img
        self.scripts["inpaint"] = inpaint

        self.available_scripts = list(self.scripts.keys())

    def get_name_list(self):
        return self.available_scripts
    
    def detect_script_name(self, request):
        for key in self.scripts:
            if key in request:
                return key
            
        return None
    
    def has_script(self, request):
        return True if self.detect_script_name(request) else False
    
    def _script_callback(self, step, timestep, queue):
        progress = float(f"{(1000-timestep)/1000.0}") # value as string to get rid of tensor
        text = f"step: {step}, progress: {progress:.2f}%"
        msg = { "progress": {"text": text, "value": progress} }
        queue.queue_item(msg)
    
    def run_script(self, request, out_queue):
        script_name = self.detect_script_name(request)
        if script_name:
            script = self.scripts[script_name]
            cb = lambda step, timestep, _: self._script_callback(step, timestep, out_queue)
            script(request, out_queue, cb)
        return