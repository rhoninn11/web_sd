
from serv.central.EdgeStats import EdgeStats

class EdgeWrapper():
    def __init__(self, **kwargs):
        self.client_thread = None
        self.edge_stats = EdgeStats()

    def bind_client_thread(self, thread):
        self.client_thread = thread


    def send_to_edge(self, request):
        if self.client_thread:
            self.edge_stats.track_request(request)
            print(f"+++ send_to_edge: {request}")

            in_queue = self.client_thread.in_queue
            in_queue.queue_item(request)

    def get_edge_result(self):
        if self.client_thread:
            out_queue = self.client_thread.out_queue
            if out_queue.queue_len() == 0:
                return None
            
            edge_result = out_queue.dequeue_item()
            self.edge_stats.summarize_result(edge_result)
            return edge_result
        return None

    def is_edge_processing(self):
        return self.edge_stats.get_request_in_process_num() > 0
