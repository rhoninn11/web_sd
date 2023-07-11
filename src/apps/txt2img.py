import time
import numpy
from PIL import Image

from core.utils.utils_thread import ThreadWrap
from core.threads.DiffusionClientThread import DiffusionClientThread
from core.utils.utils import pil2simple_data, simple_data2pil

from core.system.MultiThreadingApp import MultiThreadingApp

class ClientWrapper():
    def __init__(self, **kwargs):
        self.client_thread = None
        self.server_stats = None

    def bind_client_thread(self, thread):
        self.client_thread = thread

    def send_to_server(self, command):
        if self.client_thread:
            in_queue = self.client_thread.in_queue
            in_queue.queue_item(command)
    
    def get_server_info(self):
        if self.client_thread:
            out_queue = self.client_thread.out_queue
            if out_queue.queue_len() == 0:
                return {}
            
            return out_queue.dequeue_item()
        return {}

class ClientLogicThread(ThreadWrap):
    def __init__(self, **kwargs):
        ThreadWrap.__init__(self)
        self.client_wrapper = None
        self.on_finish = None
        self.name = "txt2img"

        self.sample_num = 1
        self.result_count = 0

    def bind_wrapper(self, wrapper):
        self.client_wrapper = wrapper
    
    def bind_on_finish(self, callback):
        self.on_finish = callback

    def prepare_command(self):
        command = { self.name: { 
            "config": {
                "prompt": "Sunny day over the sea, pastel painting",
                "prompt_negative": "boring skyscape",
                "seed": 0,
                "samples": self.sample_num,
            },
            "metadata": { "id": "osiedle xd"},
        } }
        return command
    
    def process_result(self, result):
        if result:
            if "progress" in result:
                print("Progress: ", result["progress"])
                return False

            if self.name in result:
                metadata = result[self.name]["metadata"]
                print(f"+++ eee yoo {metadata}")

                simple_data_img = result[self.name]["img"]
                pil_img = simple_data2pil(simple_data_img)
                pil_img.save(f"fs/out/{self.name}_{self.result_count}.png")
                return True

        return False
    def loop_cond(self, result):
        if self.process_result(result):
            self.result_count += 1

        finished = self.result_count >= self.sample_num
        return not finished and self.run_cond
    
    def script(self):
        if self.client_wrapper == None:
            return

        command = self.prepare_command()
        self.client_wrapper.send_to_server(command)
        
        result = None
        while self.loop_cond(result):
            result = self.client_wrapper.get_server_info()
            time.sleep(0.01)

        print("+++ task finished +++")

    def run(self):
        self.script()
        if self.on_finish:
            self.on_finish()
        
class ExampleClient(MultiThreadingApp):
    def __init__(self):
        MultiThreadingApp.__init__(self)
    
    def run(self):
        client_thread = DiffusionClientThread(name="client-central")
        client_thread.config_host_dst('localhost', 6500)
        logic_thread = ClientLogicThread()

        client_wrapper = ClientWrapper()
        client_wrapper.bind_client_thread(client_thread)
        logic_thread.bind_wrapper(client_wrapper)
        logic_thread.bind_on_finish(self.exit_fn)

        threads = [client_thread, logic_thread]
        self.thread_launch(threads) 

def main():
    app = ExampleClient()
    app.run()

main()


