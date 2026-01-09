from multiprocessing import Process
import time, os

def cpu_task(task_id):
    """Simulate CPU-intensive task."""
    print(f"[PID {os.getpid()}] Starting task {task_id}")
    pow(365, 1000000)  # Heavy computation, take about 1s
    print(f"[PID {os.getpid()}] Finished task {task_id}")

def multiprocessing_run():
    processes = []
    start = time.time()

    for i in range(5):
        p = Process(target=cpu_task, args=(i,))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    print(f"\n[Multiprocessing] Total time: {time.time() - start:.2f} seconds")

# This part is critical on macOS/Windows:
# Prevents recursive process spawning
if __name__ == '__main__':
    multiprocessing_run()