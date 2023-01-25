import time, socket, base64, signal
from PIL import Image
import asyncio


# from src.core.utils.utils_thread import ConnectionThread
from core.utils.utils_thread import ThreadWrap
from core.threads.DiffusionClientThread import DiffusionClientThread
from core.threads.DiffusionServerThread import DiffusionServerThread
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
            in_queue.queue_item(command)
    
    def get_server_info(self):
        if self.client_thread:
            out_queue = self.client_thread.out_queue
            if out_queue.queue_len() == 0:
                return {}
            
            return out_queue.dequeue_item()
        return {}

class ClientLogicThread(ThreadWrap):
    def __init__(self):
        ThreadWrap.__init__(self)
        self.client_wrapper = None
        self.on_finish = None
        self.frame_skip_num = 5
        

    def bind_wrapper(self, wrapper):
        self.client_wrapper = wrapper
    
    def bind_on_finish(self, callback):
        self.on_finish = callback

    def skip_frames(self, frame_skip_num):
        for i in range(frame_skip_num):
            self.in_queue.dequeue_item()

    def get_td_image(self):
        inlen = self.in_queue.queue_len()
        outlen = self.out_queue.queue_len()
        # print(F"+++ inlen: {inlen}, outlen: {outlen}")
        if inlen > self.frame_skip_num:
            self.skip_frames(self.frame_skip_num)
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

        command = { "img2img": {
                "img": pil2simple_data(init_img)  
            }}

        return command

    def process_result(self, result):
        simple_data_img = result["img2img"]["img"]
        pil_img = simple_data2pil(simple_data_img)
        self.set_td_img(pil_img)
    
    def loop(self):
        while self.run_cond:
            if self.client_wrapper == None:
                return
            
            command = self.prepare_command()
            if command == None:
                continue
            
            self.process_result(command)
            continue

            self.client_wrapper.send_to_server(command)
            
            result = self.client_wrapper.get_server_info()
            while not result:
                print("refresh")
                time.sleep(0.1)
                result = self.client_wrapper.get_server_info()
            

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
        client_thread = DiffusionClientThread()
        client_thread.config_host_dst('localhost', 6111)
        logic_thread = ClientLogicThread()

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
