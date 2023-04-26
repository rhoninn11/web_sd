import time, socket, base64, signal
from PIL import Image
import asyncio


from core.utils.utils_thread import ThreadWrap
from core.threads.DiffusionClientThread import DiffusionClientThread
from core.threads.DiffusionServerThread import ServerThread
from core.utils.utils import pil2simple_data, simple_data2pil, pil2numpy, numpy2pil

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
            if in_queue.queue_len() < 2:
                in_queue.queue_item(command)
    
    def get_server_info(self):
        if self.client_thread:
            out_queue = self.client_thread.out_queue
            if out_queue.queue_len() == 0:
                return None
            
            return out_queue.dequeue_item()
        return None

class ClientLogicThread(ThreadWrap):
    def __init__(self, name="noname"):
        ThreadWrap.__init__(self, name)
        self.client_wrapper = None
        self.on_finish = None

        self.memory = 0
        

    def bind_wrapper(self, wrapper):
        self.client_wrapper = wrapper
    
    def bind_on_finish(self, callback):
        self.on_finish = callback

    def skip_frames(self, frame_skip_num):
        for _ in range(frame_skip_num):
            self.in_queue.dequeue_item()

    def get_td_image(self):
        inlen = self.in_queue.queue_len()
        outlen = self.out_queue.queue_len()
        # print(F"+++ inlen: {inlen}, outlen: {outlen}")
        if inlen:
            self.skip_frames(inlen-1)
            numpy_img = self.in_queue.dequeue_item()
            pil_img = numpy2pil(numpy_img)
            return pil_img

        return None

    def set_td_img(self, pil_img):
        nympy_img = pil2numpy(pil_img)
        self.out_queue.queue_item(nympy_img)

    def prepare_command(self):
        init_img = self.get_td_image()
        if init_img == None:
            return None

        command = { "inpt_img2img": {
                "img": pil2simple_data(init_img)  
            }}

        return command

    def process_result(self, result):
        simple_data_img = result["inpt_img2img"]["img"]
        pil_img = simple_data2pil(simple_data_img)
        self.set_td_img(pil_img)


    def passthrough_loop(self):
        while self.run_cond:            
            command = self.prepare_command()
            if command:
                self.process_result(command)
            
        return
    
    def loop(self):
        while self.run_cond:
            if self.client_wrapper == None:
                print("!!! client wrapper is missing")
                return
            
            progress = 0
            command = self.prepare_command()
            if command:
                self.client_wrapper.send_to_server(command)
                print("+++ frame sended")
                progress += 1
            
            result = self.client_wrapper.get_server_info()
            if result:
                self.process_result(result)
                print("+++ new frame")
                progress += 1

            if not progress:
                time.sleep(0.05)

        return

    def run(self):
        self.loop()
        if self.on_finish:
            self.on_finish()
        
class TouchDesignerClient(MultiThreadingApp):
    def __init__(self):
        MultiThreadingApp.__init__(self)
    
    def async_start(self, params):

        addres = params["address"]
        port = params["port"]
        client_thread = DiffusionClientThread(name="client")
        client_thread.config_host_dst(addres, port)
        logic_thread = ClientLogicThread(name="logic")

        client_wrapper = ClientWrapper()
        client_wrapper.bind_client_thread(client_thread)
        logic_thread.bind_wrapper(client_wrapper)
        logic_thread.bind_on_finish(self.exit_fn)

        threads = [client_thread, logic_thread]
        self.ayncio_thread_launch(threads)
        return [logic_thread.in_queue, logic_thread.out_queue]

    def async_stop(self):
        self.stop_threads()


import asyncio
async def run_from_td(address='localhost', port=6111):
    app = TouchDesignerClient()
    params = {"address": address, "port": port}
    pipes = app.async_start(params)

    result = [app]
    result.extend(pipes)
    return result
