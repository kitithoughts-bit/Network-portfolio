# test_concurrent.py
import threading
from client import send_message

def client_task(i):
    send_message(f"Concurrent Client {i}")

if __name__ == "__main__":
    threads = []
    for i in range(5):
        t = threading.Thread(target=client_task, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
