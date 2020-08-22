from concurrent.futures import ProcessPoolExecutor
from threading import Lock


class JobWorker:
    def __init__(self):
        self.task_set = set()
        self.lock = Lock()
        self.executor = ProcessPoolExecutor(max_workers=32)

    def submit_job(self, id, func, *args):
        self.lock.acquire()
        if id in self.task_set:
            self.lock.release()
            return
        self.task_set.add(id)
        self.lock.release()

        self.executor.submit(func, *args)
