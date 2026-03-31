
WEEK 9 – ADVANCED: Bio-Inspired Networking
Overview
Ants and other social insects route better than we do, often under uncertainty. Students simulate pheromone-based routing, where each node adapts its path selection dynamically based on reinforcement feedback.
Learning Outcome / Trait Assessment
Implement reinforcement-inspired routing decisions
Maintain adaptive pheromone tables
Simulate dynamic path selection in a network
Traits trained:
Adaptive decision-making
Reinforcement reasoning in networks
Self-optimizing systems
Key Concepts
Pheromone-based routing tables
Reinforcement learning analogy
Dynamic path selection
Probabilistic forwarding

BASIC LAB — GitHub Scaffold (Student Starter Repo)
Repository Name:
week09-bio-routing-basic
Directory Structure:
week09-bio-routing-basic/
├── README.md
├── node.py
├── pheromone_table.py
├── config.py
└── docs/
    └── run_instructions.md

Step 0: Shared Configuration
# config.py
HOST = "127.0.0.1"
BASE_PORT = 10000
PEER_PORTS = [10001, 10002]  # Example peers
BUFFER_SIZE = 1024
INITIAL_PHEROMONE = 1.0
DECAY_FACTOR = 0.9
REINFORCEMENT = 0.1
FORWARD_THRESHOLD = 0.2
UPDATE_INTERVAL = 5  # seconds

Step 1: Pheromone Table
# pheromone_table.py
class PheromoneTable:
    def __init__(self):
        self.table = {}  # {peer_port: pheromone_value}

    def reinforce(self, peer, value):
        self.table[peer] = self.table.get(peer, 0) + value

    def decay(self):
        for peer in self.table:
            self.table[peer] *= DECAY_FACTOR

    def get_best_candidates(self, threshold):
        return [peer for peer, pher in self.table.items() if pher >= threshold]

Step 2: Node with Reinforcement-Based Forwarding
# node.py
import socket
import threading
import time
from config import HOST, BASE_PORT, PEER_PORTS, BUFFER_SIZE, FORWARD_THRESHOLD, UPDATE_INTERVAL, REINFORCEMENT, DECAY_FACTOR
from pheromone_table import PheromoneTable

pheromone_table = PheromoneTable()
message_queue = []

def send_message(peer_port, message):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((HOST, peer_port))
        s.sendall(message.encode())
        s.close()
        print(f"[NODE {BASE_PORT}] Sent: {message} to {peer_port}")
        pheromone_table.reinforce(peer_port, REINFORCEMENT)  # Reinforce successful path
        return True
    except (ConnectionRefusedError, socket.timeout):
        print(f"[NODE {BASE_PORT}] Failed to send to {peer_port}")
        return False

Step 3: Opportunistic Forwarding Loop with Decay
def forward_loop():
    while True:
        pheromone_table.decay()
        candidates = pheromone_table.get_best_candidates(FORWARD_THRESHOLD)
        for msg in message_queue[:]:
            for peer in candidates:
                if send_message(peer, msg):
                    message_queue.remove(msg)
                    break
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

    # Initialize pheromones for peers
    for peer in PEER_PORTS:
        pheromone_table.reinforce(peer, 1.0)

    # Initial message attempts
    for peer in PEER_PORTS:
        msg = f"Hello from node {BASE_PORT}"
        if not send_message(peer, msg):
            message_queue.append(msg)

    while True:
        time.sleep(1)

Execution & Verification
Launch multiple nodes on different BASE_PORT values
Messages should route along “best pheromone paths”
Observe reinforcement updates when messages succeed
Decay ensures stale paths become less attractive
Expected Output:
Messages preferentially forwarded to peers with higher pheromone
Queued messages sent opportunistically
Adaptive routing emerges over repeated trials

Common Mistakes (and Why They Matter)
Not decaying pheromones → old paths dominate indefinitely
Ignoring failed transmissions → reinforcement logic fails
Blocking loops → node cannot forward and receive simultaneously

BASIC EXTENSION OPTIONS (Same Repo, New Branches)
Extension A: Dynamic Learning
Update pheromone values based on round-trip success
Simulate congestion avoidance
Extension B: Multi-Hop Path Simulation
Extend table to store pheromones for paths beyond direct neighbors
Extension C: Logging & Visualization
Plot pheromone table evolution over time

EXTRA LAB — ADVANCED: Self-Healing Network Simulation
Purpose
Simulate a network that dynamically heals after failures, inspired by ant colony optimization.
Advanced Repository:
week09-bio-network-advanced
Directory Structure:
week09-bio-network-advanced/
├── README.md
├── node/
│   ├── node.py
│   ├── pheromone_table.py
│   └── encounter_simulator.py
├── utils/
│   └── logger.py
└── config.py
Advanced Requirements
Nodes adapt to broken links
Reinforcement and decay manage routing dynamically
Multiple simultaneous message flows
Logging for analysis and visualization
Advanced Concepts Introduced
Bio-inspired adaptive routing
Self-healing path selection
Emergent network optimization
Real-World Mapping
Sensor networks
Mobile ad-hoc disaster response networks
Dynamic IoT routing
Forward Application Hooks
Week 10: Conceptual quantum-inspired routing
Capstone: Bio-routing network simulator for research



