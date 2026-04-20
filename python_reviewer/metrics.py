import time
import threading

class MetricsTracker:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MetricsTracker, cls).__new__(cls)
                cls._instance.reset()
        return cls._instance

    def reset(self):
        self.start_time = None
        self.end_time = None
        self.input_tokens = 0
        self.output_tokens = 0

    def start_timer(self):
        self.start_time = time.time()

    def stop_timer(self):
        self.end_time = time.time()

    def add_tokens(self, input_tok: int, output_tok: int):
        self.input_tokens += input_tok
        self.output_tokens += output_tok

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    @property
    def elapsed_time(self) -> float:
        if self.start_time is None:
            return 0.0
        if self.end_time is None:
            return time.time() - self.start_time
        return self.end_time - self.start_time

def get_metrics_tracker() -> MetricsTracker:
    return MetricsTracker()
