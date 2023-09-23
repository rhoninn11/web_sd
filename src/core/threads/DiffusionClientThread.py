
import socket, time
from core.threads.ConnectionThread import ConnectionThread
from core.utils.utils_except import traceback_info

class DiffusionClientThread(ConnectionThread):
    def __init__(self, name):
        ConnectionThread.__init__(self, name)
        self.host = 'localhost'
        self.port = None
        self.connected = False
        
        self.e_connect_cb = None

    def config_host_dst(self, host, port):
        self.host = host
        self.port = port

    def bind_e_connect_cb(self, e_connect_cb):
        self.e_connect_cb = e_connect_cb
        self.notify_e_connect()

    def on_connect(self):
        self.print(f"+++ connected to: {self.host}:{self.port}")
        self.connected = True
        self.notify_e_connect()

    def on_disconnect(self):
        self.print(f"+++ disconnected from: {self.host}:{self.port}")
        self.connected = False
        self.notify_e_connect()

    def notify_e_connect(self):
        if self.e_connect_cb:
            self.e_connect_cb(self.connected)

    def client_connect(self):
        tcp_socket = None

        if self.port is None:
            raise Exception("!!! port not set")

        print(f"+++ connecting to: {self.host}:{self.port}")
        try:
            tcp_socket = socket.create_connection((self.host, self.port))
            self.on_connect()
            self.connection_loop(tcp_socket, self.in_queue, self.out_queue)
        except Exception as e:
            # traceback_info(e)
            print("!!! there was error with connection")

        if tcp_socket:
            tcp_socket.close()
            self.on_disconnect()

    def run(self):
        while self.run_cond:
            time.sleep(0.1)
            self.client_connect()