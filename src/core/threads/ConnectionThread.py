
import time

from core.utils.utils_thread import pipe_queue
from core.threads.ConnectionThreadBase import ConnectionThreadBase

class ConnectionThread(ConnectionThreadBase):
    def __init__(self, name="noname"):
        ConnectionThreadBase.__init__(self, name)
        self.connect_ack = False
        self.disconnect_ack = False

    def progress_balance(self, progress):
        if progress == 0:
            time.sleep(0.1)

    def process_information(self, information_obj, out_pipe: pipe_queue):
        is_disconnect = "disconnect" in information_obj    
        if is_disconnect and not self.disconnect_ack:
            self.print(f"+++ diconnect obj recived")
            self.disconnect_ack = True

        is_connect = "connect" in information_obj    
        if is_connect and not self.connect_ack:
            self.print(f"+++ connect obj recived")
            self.connect_ack = True

        operate_normal = not is_connect and not is_disconnect   
        if operate_normal:
            # self.print(f"+++ other obj recived")
            # self.print(f"+++ {information_obj}")
            
            out_pipe.queue_item(information_obj)
            

    def send_simple_obj(self, connection, key):
        simple_obj = { key:1 }
        try:
            self.send(connection, simple_obj, id=1)
            self.print(f"+++ {key} obj sended")
        except:
            self.print(f"!!! {key} obj send failed")


    def connection_loop(self, connection, conn_in_q: pipe_queue, conn_out_q: pipe_queue):
        
        self.connect_ack = False
        self.disconnect_ack = False
        self.disconnect_flag = False
        self.send_simple_obj(connection, "connect")
        while self.run_cond and not self.disconnect_ack and not self.disconnect_flag:
            
            progress = 0
            if conn_in_q.queue_len():
                obj_2_send = conn_in_q.dequeue_item()
                self.send(connection, obj_2_send)
                progress += 1
            
            recived_obj = self.recive_nb(connection)
            if recived_obj:
                self.process_information(recived_obj, conn_out_q)
                progress += 1

            self.progress_balance(progress)
        
        if self.connect_ack and not self.disconnect_ack:
            self.send_simple_obj(connection, "disconnect")
            self.disconnect_ack = True

