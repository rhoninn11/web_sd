
import time

from core.utils.utils_thread import ThreadWrap, pipe_queue
from core.scripts.index import get_index_scripts

scripts = get_index_scripts()

class SDiffusionThread(ThreadWrap):
    def __init__(self):
        ThreadWrap.__init__(self)

    def process_request(self, request):
        for key in scripts:
            if key in request:
                script = scripts[key]
                script(request, self.out_queue)
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
