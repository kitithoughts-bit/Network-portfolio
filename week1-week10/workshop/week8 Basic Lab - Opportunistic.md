
WEEK 8 – BASIC: Opportunistic Routing
Overview
Forward packets based on probability, not certainty. Students simulate mobile nodes that maintain delivery probabilities for neighbors and forward messages opportunistically when a good encounter occurs.
Learning Outcome / Trait Assessment
Maintain delivery probability metrics per neighbor
Forward packets opportunistically based on these probabilities
Understand encounter-based routing logic
Traits trained:
Probabilistic reasoning in network forwarding
Adaptive decision-making
Mobile/ad-hoc network design
Key Concepts
Delivery probability tables
Encounter-based forwarding
Opportunistic decision-making
Probabilistic routing vs deterministic routing

BASIC LAB — GitHub Scaffold (Student Starter Repo)
Repository Name:
week08-opportunistic-routing-basic
Directory Structure:
week08-opportunistic-routing-basic/
├── README.md
├── node.py
├── delivery_table.py
├── config.py
└── docs/
    └── run_instructions.md

Step 0: Shared Configuration
# config.py
HOST = "127.0.0.1"
BASE_PORT = 9000
PEER_PORTS = [9001, 9002]  # Example peers
BUFFER_SIZE = 1024
FORWARD_THRESHOLD = 0.5  # Forward if delivery probability > threshold
UPDATE_INTERVAL = 5      # seconds

Step 1: Implement Delivery Probability Table
# delivery_table.py
class DeliveryTable:
    def __init__(self):
        self.table = {}  # {peer_port: probability}

    def update_probability(self, peer, prob):
        self.table[peer] = prob

    def get_probability(self, peer):
        return self.table.get(peer, 0.0)

    def get_best_candidates(self, threshold):
        return [peer for peer, prob in self.table.items() if prob >= threshold]

Step 2: Node Maintains Delivery Probabilities
# node.py
import socket
import threading
import time
from config import HOST, BASE_PORT, PEER_PORTS, BUFFER_SIZE, FORWARD_THRESHOLD, UPDATE_INTERVAL
from delivery_table import DeliveryTable

delivery_table = DeliveryTable()
message_queue = []

def send_message(peer_port, message):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((HOST, peer_port))
        s.sendall(message.encode())
        s.close()
        print(f"[NODE {BASE_PORT}] Sent: {message} to {peer_port}")
        return True
    except (ConnectionRefusedError, socket.timeout):
        return False

Step 3: Opportunistic Forwarding Loop
def forward_loop():
    while True:
        candidates = delivery_table.get_best_candidates(FORWARD_THRESHOLD)
        for msg in message_queue[:]:
            for peer in candidates:
                if send_message(peer, msg):
                    message_queue.remove(msg)
                    break  # Stop after successful forward
        time.sleep(UPDATE_INTERVAL)

Step 4: Node Server to Receive Messages
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, BASE_PORT))
    server.listen()
    print(f"[NODE {BASE_PORT}] Listening for incoming messages...")
    while True:
        conn, addr = server.accept()
        data = conn.recv(BUFFER_SIZE).decode()
        print(f"[NODE {BASE_PORT}] Received: {data} from {addr}")
        message_queue.append(data)
        conn.close()

Step 5: Run Node
if __name__ == "__main__":
    threading.Thread(target=start_server, daemon=True).start()
    threading.Thread(target=forward_loop, daemon=True).start()

    # Example: Initialize delivery probabilities
    for peer in PEER_PORTS:
        delivery_table.update_probability(peer, 0.6)  # Assume precomputed probabilities

    # Example: Send initial messages opportunistically
    for peer in PEER_PORTS:
        msg = f"Hello from node {BASE_PORT}"
        if not send_message(peer, msg):
            print(f"[NODE {BASE_PORT}] Could not deliver to {peer}, storing in queue")
            message_queue.append(msg)

    while True:
        time.sleep(1)

Execution & Verification
Run multiple nodes on different BASE_PORT values
Adjust delivery probabilities dynamically
Observe messages forwarded only when probability > threshold
Test message queue when peers are unavailable
Expected Output:
Messages sent opportunistically based on delivery probability
Queued messages wait until a “good” encounter occurs
Opportunistic forwarding logic demonstrated

Common Mistakes (and Why They Matter)
Ignoring delivery probabilities → messages forwarded blindly
Not handling queued messages → lost packets when peers unavailable
Blocking I/O → node cannot receive while forwarding

BASIC EXTENSION OPTIONS (Same Repo, New Branches)
Extension A: Dynamic Probability Updates
Update probabilities based on encounter history
Learn which peers are most reliable
Extension B: Message TTL
Messages expire if not delivered within a time window
Prevent indefinite storage
Extension C: Logging & Statistics
Track delivery attempts, successes, and failures
Visualize network performance

EXTRA LAB — ADVANCED: Wildlife Tracking Network
Purpose
Simulate mobile nodes (animals with sensors) that exchange data opportunistically when paths cross.
Advanced Repository:
week08-opportunistic-wildlife
Directory Structure:
week08-opportunistic-wildlife/
├── README.md
├── node/
│   ├── node.py
│   ├── delivery_table.py
│   └── encounter_simulator.py
├── utils/
│   └── logger.py
└── config.py
Advanced Requirements
Mobile nodes with random encounters
Dynamic delivery probability updates
Opportunistic forwarding when nodes meet
Logging for analysis
Advanced Concepts Introduced
Encounter-based opportunistic routing
Adaptive forwarding based on historical data
Probabilistic modeling for mobile networks
Real-World Mapping
Wildlife sensor networks
Mobile ad-hoc disaster networks
Opportunistic IoT systems
Forward Application Hooks
Week 9: Bio-inspired routing (reinforcement-based probability updates)
Capstone: Delay-tolerant sensor network simulations


