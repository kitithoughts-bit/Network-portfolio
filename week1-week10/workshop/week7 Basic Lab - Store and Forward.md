
WEEK 7 – BASIC: Store-and-Forward Communication
Overview
When links fail, memory becomes the network. Students simulate nodes that detect unavailable peers, store messages, and forward them later when connectivity is restored.
Learning Outcome / Trait Assessment
Implement message queues
Retry message delivery
Handle temporary link failures
Traits trained:
Patience and persistence in network programming
Queue management
Reliability engineering
Key Concepts
Message queuing
Link availability detection
Retry logic and backoff
Asynchronous forwarding

BASIC LAB — GitHub Scaffold (Student Starter Repo)
Repository Name:
week07-store-forward-basic
Directory Structure:
week07-store-forward-basic/
├── README.md
├── node.py
├── message_queue.py
├── config.py
└── docs/
    └── run_instructions.md

Step 0: Shared Configuration
# config.py
HOST = "127.0.0.1"
BASE_PORT = 8000
PEER_PORTS = [8001, 8002]  # Example peers
BUFFER_SIZE = 1024
RETRY_INTERVAL = 5  # seconds

Step 1: Implement a Message Queue
# message_queue.py
import time
from collections import deque

class MessageQueue:
    def __init__(self):
        self.queue = deque()

    def add_message(self, message, peer_port):
        self.queue.append({"message": message, "peer": peer_port, "timestamp": time.time()})

    def get_messages(self):
        return list(self.queue)

    def remove_message(self, msg):
        self.queue.remove(msg)

Step 2: Node Detects Link Availability and Stores Messages
# node.py
import socket
import threading
import time
from config import HOST, BASE_PORT, PEER_PORTS, BUFFER_SIZE, RETRY_INTERVAL
from message_queue import MessageQueue

queue = MessageQueue()

def send_message(peer_port, message):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((HOST, peer_port))
        s.sendall(message.encode())
        s.close()
        return True
    except (ConnectionRefusedError, socket.timeout):
        return False

def forward_loop():
    while True:
        for msg in queue.get_messages():
            success = send_message(msg["peer"], msg["message"])
            if success:
                print(f"[NODE {BASE_PORT}] Sent stored message to {msg['peer']}")
                queue.remove_message(msg)
        time.sleep(RETRY_INTERVAL)

Step 3: Node Receives Messages and Stores Undeliverable Messages
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, BASE_PORT))
    server.listen()
    print(f"[NODE {BASE_PORT}] Listening for messages...")
    while True:
        conn, addr = server.accept()
        data = conn.recv(BUFFER_SIZE).decode()
        print(f"[NODE {BASE_PORT}] Received: {data} from {addr}")
        conn.close()

Step 4: Send Initial Messages
if __name__ == "__main__":
    threading.Thread(target=start_server, daemon=True).start()
    threading.Thread(target=forward_loop, daemon=True).start()

    # Send initial messages
    for peer in PEER_PORTS:
        msg = f"Hello from node {BASE_PORT}"
        if not send_message(peer, msg):
            print(f"[NODE {BASE_PORT}] Peer {peer} unavailable, storing message")
            queue.add_message(msg, peer)

    while True:
        time.sleep(1)

Execution & Verification
Run multiple nodes with different BASE_PORT values
Stop one node temporarily and send messages
Restart the stopped node and observe queued messages being delivered
Adjust RETRY_INTERVAL to test message persistence
Expected Output:
Messages sent to available peers immediately
Messages stored when peers are unavailable
Queued messages automatically forwarded when peers come back online

Common Mistakes (and Why They Matter)
Forgetting to remove delivered messages → duplicate deliveries
Ignoring retry interval → message starvation
Using blocking I/O incorrectly → node cannot serve peers while waiting

BASIC EXTENSION OPTIONS (Same Repo, New Branches)
Extension A: Persistent Storage
Save message queue to disk
Messages survive node restarts
Extension B: Retry Backoff Strategy
Exponential backoff for retries
Avoid network flooding
Extension C: Prioritized Queues
High-priority messages forwarded first
Simulate emergency vs normal traffic

EXTRA LAB — ADVANCED: Planetary Email System
Purpose
Simulate a network where messages may take minutes or hours to arrive, mimicking interplanetary communication.
Advanced Repository:
week07-store-forward-planetary
Directory Structure:
week07-store-forward-planetary/
├── README.md
├── node/
│   ├── node.py
│   ├── message_queue.py
│   └── link_manager.py
├── utils/
│   └── retry_policy.py
└── config.py
Advanced Requirements
Persistent queue storage
Delivery timestamps and hop tracking
Variable link availability
Retry with backoff and logging
Advanced Concepts Introduced
Delay-tolerant networking (DTN)
Queue prioritization
Simulated inter-node link failures
Real-World Mapping
Deep-space communication (Mars missions)
Remote disaster message networks
Delay-tolerant IoT networks
Forward Application Hooks
Week 8: Opportunistic routing
Week 9: Bio-inspired routing strategies
Capstone: Planetary Email System



