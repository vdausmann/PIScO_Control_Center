from multiprocessing import Process, Queue, Value
from queue import Empty
import time


class ProcessPool:
    def __init__(self, func, running, max_tasks: int = 10) -> None:
        self.func = func
        if max_tasks > 0:
            self.tasks = Queue(max_tasks)
        else:
            self.tasks = Queue()
        self.running = running

    def add_task(self, task):
        self.tasks.put(task)

    def worker(self, index: int, name=''):
        while self.running.value == 1:
            try:
                task = self.tasks.get(timeout=1)
                if task == "quit":
                    self.running.value = 0
                    break
                self.func(task, index)
            except Empty:
                pass #muss hier vllt ein continue hin?
        print(f"{name} Process {index} finished")

    def start(self, n_processes, name=''):
        self.processes = []

        for i in range(n_processes):
            p = Process(target=self.worker, args=(i,name))
            p.start()
            self.processes.append(p)

    def stop(self, slow: bool = False):
        if slow:
            self.add_task("quit")
        else:
            self.running.value = 0

    def is_running(self):
        if self.running.value == 1:
            return True
        else:
            for p in self.processes:
                if p.is_alive():
                    return True
            return False


if __name__ == "__main__":
    import time

    def f(x, i):
        print(f"Process {i} has the task {x}")
        time.sleep(1)

    pool = ProcessPool(f, 100)
    for i in range(100):
        pool.add_task(i)

    pool.start(5)
    pool.stop(True)
