
from core.system.MultiThreadingApp import MultiThreadingApp
from core.threads.DiffusionServerThread import ServerThread

from uniq.threads.CentralGradioInterface import CentralGradioInterface

from serv.central.CentralLogicThread import CentralLogicThread

class CentralServerApp(MultiThreadingApp):
    def __init__(self):
        MultiThreadingApp.__init__(self)
    
    def run(self):
        print("+++ app start")
        logic_thread = CentralLogicThread(name="client-logic")
        server_thread = ServerThread(name="central-server")
        server_thread.config_host('localhost', 6500)
        gradio_thread = CentralGradioInterface() 

        server_thread.bind_worker(logic_thread)
        gradio_thread.bind_config_reciver(logic_thread)

        # gradio thread block main thread - must be last on the list
        threads = [server_thread, logic_thread, gradio_thread]
        self.thread_launch(threads)

        print("+++ central server exit")

def main():
    sever_app = CentralServerApp()
    sever_app.run()

main()