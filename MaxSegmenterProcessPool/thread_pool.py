import threading
import time


class ThreadPool:
    SLOW_STOP_KEY = "stop_pool"

    def __init__(self, func, max_todo_len: int = 10) -> None:
        self.todo = []
        self.lock = threading.Lock()
        self.threads = []
        self.run = True
        self.func = func
        self.max_todo_len = max_todo_len
        self.max_sleep_counter = 10000000

    def worker(self, index: int):
        sleep_counter = 0
        while True:
            if sleep_counter > self.max_sleep_counter or not self.run:
                print(f"Reader {index} quitting due to inactivity")
                break
            self.lock.acquire()
            if len(self.todo) == 0:
                self.lock.release()
                sleep_counter += 1
                time.sleep(0.01)
            else:
                sleep_counter = 0
                job = self.todo.pop(0)
                if job == self.SLOW_STOP_KEY:
                    self.run = False
                    print(f"Reader {index} stopped")
                    break
                self.lock.release()
                self.func(job, index)

        #print(f"Reader {index} quitting")

    def start(self, n_threads: int):
        for i in range(n_threads):
            t = threading.Thread(target=self.worker, args=(i,))
            t.start()
            self.threads.append(t)

    def add_task(self, job):
        while True:
            self.lock.acquire()
            if len(self.todo) < self.max_todo_len:
                self.todo.append(job)
                self.lock.release()
                break
            self.lock.release()
            time.sleep(0.01)

    def stop(self, slow: bool = False):
        if slow:
            self.todo.append(self.SLOW_STOP_KEY)
        else:
            self.run = False

    def is_running(self):
        if self.run:
            return True
        else:
            for t in self.threads:
                if t.is_alive():
                    return True
            return False
