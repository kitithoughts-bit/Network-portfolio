
WEEK 6 – BASIC: Ad-Hoc Networking (MANET Simulation)
Overview
Infrastructure disappears. Nodes improvise. Students simulate mobile nodes that discover neighbors and forward messages probabilistically.
Learning Outcome / Trait Assessment
Maintain a neighbor table dynamically
Forward packets with TTL and probability
Understand the basics of MANET routing
Traits trained:
Adaptive thinking
Probabilistic reasoning
Debugging dynamic network states
Key Concepts
Ad-hoc neighbor discovery
Probabilistic packet forwarding
TTL (Time-To-Live) for loop prevention
Node mobility simulation (optional)

BASIC LAB — GitHub Scaffold (Student Starter Repo)
Repository Name:
week06-manet-basic
Directory Structure:
week06-manet-basic/
├── README.md
├── node.py
├── config.py
└── docs/
    └── run_instructions.md
Step 0: Shared Configuration
# config.py
HOST = "127.0.0.1"
BASE_PORT = 7000
BUFFER_SIZE = 1024
NEIGHBORS = [7001, 7002]  # Example peer ports
FORWARD_PROBABILITY = 0.5  # 50% chance to forward
TTL = 3  # Max hops for message

Step 1: Node Maintains a Neighbor Table
# node.py
import socket
import threading
import random
from config import HOST, BASE_PORT, BUFFER_SIZE, NEIGHBORS, FORWARD_PROBABILITY, TTL

neighbor_table = set(NEIGHBORS)

def handle_incoming(conn, addr):
    data = conn.recv(BUFFER_SIZE).decode()
    msg, ttl = data.split('|')
    ttl = int(ttl)
    print(f"[NODE {BASE_PORT}] Received from {addr}: {msg} (TTL={ttl})")
    conn.close()
    
    # Forward probabilistically
    if ttl > 0 and random.random() < FORWARD_PROBABILITY:
        forward_message(msg, ttl - 1, exclude=addr[1])

def start_server(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, port))
    server.listen()
    print(f"[NODE {port}] Listening for neighbors...")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_incoming, args=(conn, addr)).start()

Step 2: Node Forwards Messages with TTL
def forward_message(message, ttl, exclude=None):
    for peer_port in neighbor_table:
        if peer_port == exclude:
            continue
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((HOST, peer_port))
            s.sendall(f"{message}|{ttl}".encode())
            s.close()
        except ConnectionRefusedError:
            print(f"[NODE {BASE_PORT}] Peer {peer_port} unreachable")

Step 3: Node Sends Initial Message
if __name__ == "__main__":
    threading.Thread(target=start_server, args=(BASE_PORT,), daemon=True).start()
    
    # Send a test message to neighbors
    test_message = f"Hello from node {BASE_PORT}"
    forward_message(test_message, TTL)

Execution & Verification
Open multiple terminals, assign different BASE_PORT values for each node
Run python node.py in each terminal
Observe message propagation with TTL and probabilistic forwarding
Modify FORWARD_PROBABILITY to test network robustness
Expected Output:
Nodes print incoming messages with TTL
Messages may not reach all nodes depending on forwarding probability
TTL prevents infinite loops

Common Mistakes (and Why They Matter)
Using same port for multiple nodes → port conflict
Forgetting TTL → messages may loop forever
Ignoring exclude parameter → nodes send messages back to sender

BASIC EXTENSION OPTIONS (Same Repo, New Branches)
Extension A: Neighbor Discovery Protocol
Nodes periodically ping ports in a range
Update neighbor_table dynamically
Extension B: Mobility Simulation
Randomly remove/add neighbors to simulate moving nodes
Observe network resilience
Extension C: Probabilistic Routing Metrics
Track message delivery rate
Adjust FORWARD_PROBABILITY based on success

EXTRA LAB — ADVANCED: Disaster Response Mesh
Purpose
Simulate a temporary rescue network with mobile devices that form an ad-hoc mesh and forward messages intelligently.
Advanced Repository:
week06-manet-disaster-advanced
Directory Structure:
week06-manet-disaster-advanced/
├── README.md
├── node/
│   ├── node.py
│   ├── neighbor_manager.py
│   └── message_forwarder.py
├── utils/
│   └── routing_metrics.py
└── config.py
Advanced Requirements
Dynamic neighbor discovery
Probabilistic packet forwarding with metrics
TTL and hop count management
Optional mobility simulation
Advanced Concepts Introduced
MANET routing basics (AODV/OLSR conceptual)
Real-time topology adaptation
Failure tolerance and self-healing network
Real-World Mapping
Disaster recovery communication
Search and rescue coordination
Mobile mesh networks
Forward Application Hooks
Week 7: Store-and-forward networks
Week 8: Opportunistic routing
Capstone: Disaster Mesh Network



