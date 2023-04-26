
import time

from core.utils.utils_thread import ThreadWrap, pipe_queue
from core.threads.DiffusionClientThread import DiffusionClientThread

from serv.central.EdgeWrapper import EdgeStats
from serv.central.EdgeWrapper import EdgeWrapper

from uniq.scripts.ScriptIndex import ScriptIndex

from core.utils.utils_logging import my_print
SI = ScriptIndex()

class EdgeManager():
    def __init__(self):
        self.edge_list = {}
        self.edge_config = {}
        self.no_config = {}

    def spawn_edge(self, key, host, port):
        new_client_thread = DiffusionClientThread(name=f"conn-{key}")
        new_client_thread.config_host_dst(host, port)
        new_client_thread.start()

        new_client_wrapper = EdgeWrapper()
        new_client_wrapper.bind_client_thread(new_client_thread)

        edge_instance = { 
            "wrapper": new_client_wrapper,
            "thread": new_client_thread,
            "stats": EdgeStats()
        }
        return edge_instance

class CentralLogicThread(ThreadWrap):
    def __init__(self, name="noname"):
        ThreadWrap.__init__(self, name)
        self.edge_list = {}
        edge_config = { "edge_host": {} }
        no_config = {
                "prompt": "stone marble covered with floral patterns chilling in fantasy realm",
                "prompt_negative": "",
                "power": 0.8
            }

        self.config_pipe = pipe_queue("config")
        self.config = { 
            "edge_config": edge_config,
            "no_config": no_config
        }
        # istnieje potencjał na stworzenie klasy edge manager
        self.edge_manager = EdgeManager()
        # istnieje potencjał na stworzenie klasy flow manager
        
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

    def edges_to_add(self, edge_config):
        edges_to_add = {}

        # looking for new edges
        for key in edge_config:
            if not key in self.edge_list:
                edges_to_add[key] = edge_config[key]

        return edges_to_add

    def edges_to_remove(self, edge_config):
        edges_to_remove = {}

        # looking for edges to remove
        for key in self.edge_list:
            if not key in edge_config:
                edges_to_remove[key] = self.edge_list[key]

        return edges_to_remove
    
    def add_edges(self, edges_to_add):
        for key in edges_to_add:
            host, port = edges_to_add[key]
            new_edge = self.edge_manager.spawn_edge(key, host, port)

            self.edge_list[key] = new_edge
            print(f"+++ spawned edge spawned {key}")

    def pass_wrapper_work(self, wrapper):
        progress = 0
        while True:
            edge_result = wrapper.get_edge_result()
            if edge_result is None:
                break
            
            self.out_queue.queue_item(edge_result)
            progress += 1
        return progress

    def try_return_edge_result(self):
        progress = 0
        for key in self.edge_list:
            edge = self.edge_list[key]
            wrapper = edge["wrapper"]
            progress += self.pass_wrapper_work(wrapper)

        return 0
    
    def select_edge(self):
        if len(self.edge_list) == 0:
            return None
        
        for key in self.edge_list:
            edge = self.edge_list[key]
            wrapper = edge["wrapper"]
            if not wrapper.is_edge_processing():
                return wrapper

        return None
    
    def select_request(self, drop=False):
        new_frame_num = self.in_queue.queue_len()
        if new_frame_num:
            if drop:
                for _ in range(new_frame_num-1):
                    request2drop = self.in_queue.dequeue_item()

            return self.in_queue.dequeue_item()
        
        return None
    
    def manage_edge(self, edge_config):
        hosts_to_add = self.edges_to_add(edge_config)
        hosts_to_remove = self.edges_to_remove(edge_config)

        self.add_edges(hosts_to_add)
        self.remove_edges(hosts_to_remove)

    def manage_flow(self):
        progress = 0
        wrapper = self.select_edge()
        if wrapper:
            request = self.select_request()
            if request:
                fn_name = SI.detect_script_name(request)
                if fn_name:
                    if "config" not in request[fn_name]:
                        request[fn_name]["config"] = self.config["no_config"]
                    wrapper.send_to_edge(request)
                    progress += 1

        progress += self.try_return_edge_result()
        return progress
    
    def remove_edges(self, edges_to_remove):
        key_list = list(edges_to_remove.keys())
        for key in key_list:
            edge_obj = self.edge_list[key]
            thread = edge_obj["thread"]
            thread.stop()

        for key in key_list:
            del self.edge_list[key]

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

        self.remove_edges(self.edge_list)

    def run(self):
        self.loop()