
from serv.central.EdgeStats import EdgeStats

class EdgeWrapper():
    def __init__(self, **kwargs):
        self.client_thread = None
        self.edge_stats = EdgeStats()

    def bind_client_thread(self, thread):
        self.client_thread = thread

    def send_to_edge(self, edge_request):
        if self.client_thread:
            in_queue = self.client_thread.in_queue
            self.edge_stats.frame_timeing_init(edge_request)
            in_queue.queue_item(edge_request)

    def get_edge_result(self):
        if self.client_thread:
            out_queue = self.client_thread.out_queue
            if out_queue.queue_len() == 0:
                return None
            edge_result = out_queue.dequeue_item()
            self.edge_stats.scan_freame(edge_result)
            return edge_result
        return None

    def is_edge_processing(self):
        return self.edge_stats.get_frame_in_process_num() > 0
