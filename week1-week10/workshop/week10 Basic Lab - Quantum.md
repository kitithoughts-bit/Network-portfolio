
WEEK 10 – ADVANCED: Quantum-Inspired Networking (Conceptual)
Overview
Quantum networking principles inspire new ways to think about communication: messages may be read once, cannot be cloned, and network state may “collapse” on access. Students simulate one-time-read message tokens and observe how state-aware routing can be built conceptually without quantum hardware.
Learning Outcome / Trait Assessment
Implement one-time-read message tokens
Model network state collapse upon access
Simulate probabilistic message delivery and access constraints
Traits trained:
Security-conscious thinking
Probabilistic and conceptual modeling
Minimalism in message handling
Key Concepts
No-cloning principle (messages cannot be copied)
State collapse (reading changes availability)
One-time-read tokens
Conceptual quantum-safe messaging

BASIC LAB — GitHub Scaffold (Student Starter Repo)
Repository Name:
week10-quantum-network-basic
Directory Structure:
week10-quantum-network-basic/
├── README.md
├── node.py
├── token.py
├── config.py
└── docs/
    └── run_instructions.md

Step 0: Shared Configuration
# config.py
HOST = "127.0.0.1"
BASE_PORT = 11000
PEER_PORTS = [11001, 11002]  # Example peers
BUFFER_SIZE = 1024
TOKEN_EXPIRY = 10  # seconds until token invalid
UPDATE_INTERVAL = 5

Step 1: Define One-Time-Read Token
# token.py
import time

class Token:
    def __init__(self, message):
        self.message = message
        self.read = False
        self.timestamp = time.time()

    def read_token(self):
        if self.read or time.time() - self.timestamp > 10:
            return None  # Cannot read again
        self.read = True
        return self.message

Step 2: Node for Sending/Receiving Tokens
# node.py
import socket
import threading
import time
from config import HOST, BASE_PORT, PEER_PORTS, BUFFER_SIZE, UPDATE_INTERVAL
from token import Token

token_queue = []

def send_token(peer_port, token):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((HOST, peer_port))
        s.sendall(token.message.encode())
        s.close()
        print(f"[NODE {BASE_PORT}] Sent token to {peer_port}")
        return True
    except (ConnectionRefusedError, socket.timeout):
        print(f"[NODE {BASE_PORT}] Failed to send to {peer_port}")
        return False

Step 3: Forwarding Loop with One-Time-Read Enforcement
def forward_loop():
    while True:
        for token in token_queue[:]:
            for peer in PEER_PORTS:
                if send_token(peer, token):
                    token_queue.remove(token)
                    break
        time.sleep(UPDATE_INTERVAL)

Step 4: Node Server to Receive Tokens
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, BASE_PORT))
    server.listen()
    print(f"[NODE {BASE_PORT}] Listening for incoming tokens...")
    while True:
        conn, addr = server.accept()
        data = conn.recv(BUFFER_SIZE).decode()
        token = Token(data)
        message = token.read_token()
        if message:
            print(f"[NODE {BASE_PORT}] Received token: {message}")
            token_queue.append(token)
        else:
            print(f"[NODE {BASE_PORT}] Token invalid or already read from {addr}")
        conn.close()

Step 5: Run Node
if __name__ == "__main__":
    threading.Thread(target=start_server, daemon=True).start()
    threading.Thread(target=forward_loop, daemon=True).start()

    # Send initial token
    initial_token = Token(f"Quantum token from {BASE_PORT}")
    token_queue.append(initial_token)

    while True:
        time.sleep(1)

Execution & Verification
Launch multiple nodes on different BASE_PORT values
Observe tokens being sent, received, and consumed exactly once
Attempt to read or forward tokens again; verify that access is denied
Track token state in logs for verification
Expected Output:
Tokens delivered only once per node
Reading a token marks it consumed
Token expiry prevents stale message use

Common Mistakes (and Why They Matter)
Ignoring token state → violates one-time-read principle
Not using expiry → stale tokens circulate indefinitely
Blocking loops → token forwarding is delayed or lost

BASIC EXTENSION OPTIONS (Same Repo, New Branches)
Extension A: Token Expiry Management
Add configurable expiry times per token
Implement cleanup of expired tokens
Extension B: Multi-Hop Token Routing
Forward tokens to multiple nodes before consumption
Track history to prevent re-delivery
Extension C: Logging & Analytics
Log token state transitions
Visualize message collapse over network

EXTRA LAB — ADVANCED: Quantum-Secure Messenger Simulation
Purpose
Simulate a secure messaging system inspired by quantum principles: no-cloning, ephemeral messages, and probabilistic network state.
Advanced Repository:
week10-quantum-messenger-advanced
Directory Structure:
week10-quantum-messenger-advanced/
├── README.md
├── node/
│   ├── node.py
│   ├── token.py
│   └── state_manager.py
├── utils/
│   └── logger.py
└── config.py
Advanced Requirements
Nodes handle multiple ephemeral tokens
Token history prevents duplication
Probabilistic delivery models network collapse
Logging and visualization for teaching state collapse
Advanced Concepts Introduced
Quantum-inspired ephemeral messaging
Network state collapse simulation
Security-aware conceptual modeling
Real-World Mapping
Quantum key distribution concepts
Secure ephemeral messaging systems
Privacy-first IoT or messaging networks
Forward Application Hooks
Capstone: Delay-tolerant quantum-inspired network simulator
Optional integration with Week 9 bio-routing for hybrid simulation



