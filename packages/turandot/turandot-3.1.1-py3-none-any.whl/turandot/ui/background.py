import threading
from functools import wraps
from turandot import Singleton


def background(f):
    """Decorator: Push execution to background thread"""
    @wraps(f)
    def process(*args, **kwargs):
        processor = BackgroundProcessor()
        new_thread = threading.Thread(target=processor.run_task_blocking, args=[f, *args], kwargs=kwargs)
        new_thread.start()
    return process


class BackgroundProcessor(metaclass=Singleton):
    """Singleton executor to run threads in the background"""

    def __init__(self):
        self.semaphore = threading.Semaphore()

    def run_task_blocking(self, f, *args, **kwargs):
        """Run background tasks one after another"""
        self.semaphore.acquire()
        f(*args, **kwargs)
        self.semaphore.release()
