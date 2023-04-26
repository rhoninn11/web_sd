
import select

from core.utils.utils_thread import ThreadWrap
from core.utils.utils_logging import my_print
from core.utils.utils import obj2json2bytes, bytes2json2obj

class ConnectionThreadBase(ThreadWrap):
    def __init__(self, name="noname"):
        ThreadWrap.__init__(self, name)
    
    def print(self, msg):
        msg_with_name = f"{self.name} {msg}"
        my_print(msg_with_name)

    def send(self, connection, obj_2_send):
        msg_bytes = obj2json2bytes(obj_2_send)
        connection.sendall(msg_bytes)
        # self.print(f"+++ wysłano {len(msg_bytes)}b")

    def revice_data(self, connection):
        data = connection.recv(4)
        if data is None:
            self.print("+++ recive None 1")
            return None
        byte_size = int.from_bytes(data, byteorder="little")

        data = b''
        while len(data) < byte_size:
            packet = connection.recv(byte_size - len(data))
            if packet is None:
                self.print("+++ recive None 2")
                return None
            data += packet

        return data

    def recive(self, connection):
        msg_bytes = self.revice_data(connection)
        # self.print(f"+++ odebrano {len(msg_bytes)}b")
        if msg_bytes is None:
            return None

        new_data = bytes2json2obj(msg_bytes)
        return new_data

    def recive_nb(self, connection):
        ready, _, _ = select.select([connection], [], [], 0)
        if ready:
            return self.recive(connection)

        return None