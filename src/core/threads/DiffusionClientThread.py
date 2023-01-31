
import socket, time
from core.utils.utils_thread import ConnectionThread
from core.utils.utils_except import traceback_info
from core.globals import get_server_port

class DiffusionClientThread(ConnectionThread):
    def __init__(self, name):
        ConnectionThread.__init__(self, name)
        self.host = 'localhost'
        self.port = get_server_port()

    def config_host_dst(self, host, port):
        self.host = host
        self.port = port

    def client_connect(self):
        tcp_socket = None

        print(f"+++ client connecting to: {self.host}:{self.port}")
        try:
            tcp_socket = socket.create_connection((self.host, self.port))
            print("+++ join server")
            self.connection_loop(tcp_socket, self.in_queue, self.out_queue)
            print("+++ leave server")
        except Exception as e:
            traceback_info(e)

        if tcp_socket:
            tcp_socket.close()

    def run(self):
        while self.run_cond:
            time.sleep(0.1)
            self.client_connect()