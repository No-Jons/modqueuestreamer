import threading

from typing import Callable


class StreamHandler:
    def __init__(self, target: Callable, **kwargs):
        self.func = threading.Thread(target=target, **kwargs)

    def start(self):
        self.func.start()

    def kill(self):
        self.func.join(timeout=1.0)
        if not self.func.is_alive():
            return True
        return False
