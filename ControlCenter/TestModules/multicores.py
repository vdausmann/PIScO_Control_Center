from multiprocessing import Process
import time
import random

def f():
    time_to_sleep = random.randint(1, 5)
    print(f"Sleeping for {time_to_sleep}s")
    time.sleep(time_to_sleep)


if __name__ == '__main__':
    processes = []
    for i in range(5):
        p = Process(target=f)
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
