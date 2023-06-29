
import select

from core.utils.utils_thread import ThreadWrap
from core.utils.utils_logging import my_print
from core.utils.utils import obj2json2bytes, bytes2json2obj

class ConnectionThreadBase(ThreadWrap):
    def __init__(self, name="noname"):
        ThreadWrap.__init__(self, name)
        self.disconnect_flag = False
    
    def print(self, msg):
        msg_with_name = f"{self.name} {msg}"
        my_print(msg_with_name)

    def wrap_data(self, data_bytes):
        if data_bytes[-1] != b'\0':
            data_bytes += b'\0'

        data_bytes_num = len(data_bytes)
        len_bytes = data_bytes_num.to_bytes(4, 'little')
        data_to_send = len_bytes + data_bytes
        return data_to_send
    
    def unwrap_data(self, wrapped_bytes):
        unwrapped_bytes = wrapped_bytes[4:]
        return unwrapped_bytes

    def send(self, connection, obj_2_send, id=0):
        data_bytes = obj2json2bytes(obj_2_send)
        msg_bytes = self.wrap_data(data_bytes)
        connection.sendall(msg_bytes)
        # self.print(f"+++ wysłano {len(msg_bytes)}b")

    def revice_data(self, connection):
        len_bytes = connection.recv(4)
        if len_bytes is None:
            return None
        
        byte_size = int.from_bytes(len_bytes, byteorder="little")
        if byte_size == 0:
            return None
        
        rest_bytes = b''
        while len(rest_bytes) < byte_size:
            packet = connection.recv(byte_size - len(rest_bytes))
            if packet is None:
                return None
            rest_bytes += packet
        return len_bytes + rest_bytes

    def recive(self, connection):
        msg_bytes = self.revice_data(connection)
        # self.print(f"+++ odebrano {len(msg_bytes)}b")
        if msg_bytes is None:
            self.disconnect_flag = True
            return None
        data_bytes = self.unwrap_data(msg_bytes)
        new_data = bytes2json2obj(data_bytes)
        return new_data

    def recive_nb(self, connection):
        ready, _, _ = select.select([connection], [], [], 0)
        if ready:
            return self.recive(connection)

        return None