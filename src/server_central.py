import time

from core.utils.utils_thread import ThreadWrap, pipe_queue
from core.threads.DiffusionServerThread import DiffusionServerThread
from core.threads.DiffusionClientThread import DiffusionClientThread
from core.threads.GradioCentralInterface import CentralGradioInterface
from core.utils.utils import pil2simple_data

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

class CentralLogicThread(ThreadWrap):
    def __init__(self, **kwargs):
        ThreadWrap.__init__(self)
        self.edge_list = {}
        edge_config = { "edge_host": {} }
        sd_config = {
                "prompt": "stone marble covered with floral patterns chilling in fantasy realm",
                "prompt_negative": "",
                "power": 0.8
            }

        self.config_pipe = pipe_queue("config")
        self.config = { 
            "edge_config": edge_config,
            "sd_config": sd_config
        }
        
    def new_config(self, new_config):
        self.config_pipe.queue_item(new_config)
    
    def manage_config_update(self):
        while self.config_pipe.queue_len():
            new_config = self.config_pipe.dequeue_item()
            edge_config = new_config["edge_config"]
            self.manage_edge(edge_config)
            self.config = new_config
            print(f"+++ new config applied")
            return 1

        return 0

    def manage_edge(self, edge_config):
        # porównać z obecnym konfigiem
        # to co zniknęło zatrzymać
        # to co się pojawiło zatrzymać
        hosts_to_add = {}
        hosts_to_remove = {}

        # sprawdzić czy coś nowego się pojawiło, zanotować
        for key in edge_config:
            if not key in self.edge_list:
                hosts_to_add[key] = edge_config[key]

        # sprawdzić czy coś starego zniknęło, zanotować
        for key in self.edge_list:
            if not key in edge_config:
                hosts_to_remove[key] = self.edge_list[key]



        for key in hosts_to_add:
            host, port = hosts_to_add[key]
            new_client_thread = DiffusionClientThread()
            new_client_thread.config_host_dst(host, port)
            new_client_thread.start()

            new_client_wrapper = ClientWrapper()
            new_client_wrapper.bind_client_thread(new_client_thread)

            self.edge_list[key] = { "wrapper":new_client_wrapper, "thread":new_client_thread }
            print(f"+++ spawned new client {key}")

    def probe(self):
        if self.in_queue.queue_len():
            print(f"in_queue")

        if self.out_queue.queue_len():
            print(f"out_queue")

    def manage_flow(self):
        if len(self.edge_list) == 0:
            return 0
        
        progress = 0
        
        thread, wrapper = (None, None)
        for key in self.edge_list:
            edge = self.edge_list[key]
            wrapper = edge["wrapper"]
            thread = edge["thread"]
            break

        if self.in_queue.queue_len():
            print("+++ new frame")
            sd_config = self.config["sd_config"]
            command = self.in_queue.dequeue_item()
            command["img2img"]["config"] = sd_config
            wrapper.send_to_server(command)
            progress += 1

        result = wrapper.get_server_info()
        if result:
            self.out_queue.queue_item(result)
            progress += 1

        return progress

        
    
    def loop(self):
        # logika jest workerem serwera
        # logika powinna być konfigurowana za pomocą gradio
        # z konfiguracji gradio wynika do jakich edge'y powinna się połączyć logika
        while self.run_cond:
            progress = 0
            progress += self.manage_config_update()
            progress += self.manage_flow()

            if not progress:
                time.sleep(0.1)

    def run(self):
        self.loop()

from core.system.MultiThreadingApp import MultiThreadingApp
class CentralServerApp(MultiThreadingApp):
    def __init__(self):
        MultiThreadingApp.__init__(self)
    
    def run(self):
        print("+++ app start")
        logic_thread = CentralLogicThread()
        server_thread = DiffusionServerThread()
        server_thread.config_host('192.168.2.113', 6500)
        gradio_thread = CentralGradioInterface() 

        server_thread.bind_worker(logic_thread)
        gradio_thread.bind_config_reciver(logic_thread)

        # gradio thread block main thread - must be last on the list
        threads = [server_thread, logic_thread, gradio_thread]
        self.thread_launch(threads)

        print("+++ server exit")

def main():
    sever_app = CentralServerApp()
    sever_app.run()

main()