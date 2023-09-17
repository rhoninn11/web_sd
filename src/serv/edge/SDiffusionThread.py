
import time

from core.utils.utils_thread import ThreadWrap
from core.ScriptIndex import ScriptIndex


class SDiffusionThread(ThreadWrap):
    def __init__(self, device):
        ThreadWrap.__init__(self)
        self.script_index = ScriptIndex()
        self.script_index.set_device(device)

    def process_request(self, request):
        si = self.script_index
        if si.has_script(request):
            si.run_script(request, self.out_queue)

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
