import time

from core.threads.DiffusionServerThread import ServerThread
from core.threads.SDiffusionThread import SDiffusionThread

from core.system.MultiThreadingApp import MultiThreadingApp
 
class EdgeServer(MultiThreadingApp):
    def __init__(self):
        MultiThreadingApp.__init__(self)
    
    def run(self):
        print(f"+++ app start")

        stableD_thread = SDiffusionThread()
        tcp_thread = ServerThread("edge_server")

        tcp_thread.bind_worker(stableD_thread)
        tcp_thread.config_host("localhost", 6203)

        # gradio thread block main thread - must be last on the list
        threads = [stableD_thread, tcp_thread]
        self.thread_launch(threads)

        print("+++ app exit")


def main():
    edge_server = EdgeServer()
    edge_server.run()

main()