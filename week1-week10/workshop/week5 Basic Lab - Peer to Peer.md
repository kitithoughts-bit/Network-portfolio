WEEK 5 – BASIC: Peer-to-Peer Networking
Teaching Intent (Instructor Note)
Week 5 breaks habits. There is no server to blame, no client to obey. Every node must listen and speak, often at the same time.
Peer-to-peer networking teaches symmetry, decentralization, and responsibility.

Overview
This lab introduces peer-to-peer (P2P) communication using Python sockets. Each node acts as both a server and a client, accepting incoming connections while initiating outbound ones.
There is no central authority—only cooperation.

Learning Outcomes / Trait Assessment
Explain the peer-to-peer communication model
Implement a node that acts as both client and server
Manage concurrent send/receive behavior
Traits trained: - Systems thinking - Decentralized reasoning - Failure tolerance

Key Concepts
Symmetric roles (client = server)
Listening sockets + outbound connections
Peer discovery (manual)
Basic concurrency

BASIC LAB — Student Starter GitHub Repo
Repository Name
week05-peer-to-peer-basic
Repository Structure
week05-peer-to-peer-basic/
├── README.md
├── peer.py
├── config.py
└── docs/
    └── run_instructions.md

BASIC LAB — Step-by-Step
Step 0: Shared Configuration
# config.py
HOST = "127.0.0.1"
BASE_PORT = 9000
BUFFER_SIZE = 1024

Step 1: Create a Peer Node (Listener + Sender)
# peer.py
import socket
import threading
import sys
from config import HOST, BASE_PORT, BUFFER_SIZE

peer_id = int(sys.argv[1])
PORT = BASE_PORT + peer_id

Step 2: Listener Thread
def listen():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen(5)
    print(f"[PEER {peer_id}] Listening on {PORT}")

    while True:
        conn, addr = sock.accept()
        data = conn.recv(BUFFER_SIZE)
        print(f"[PEER {peer_id}] From {addr}: {data.decode()}")
        conn.close()

Step 3: Sender Function
def send_message(target_peer_id, message):
    target_port = BASE_PORT + target_peer_id
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, target_port))
    sock.sendall(message.encode())
    sock.close()

Step 4: Run Listener + Send Message
threading.Thread(target=listen, daemon=True).start()

while True:
    target = int(input("Send to peer ID: "))
    msg = input("Message: ")
    send_message(target, msg)

Execution & Verification
Open two terminals
Run python peer.py 1 and python peer.py 2
Send messages between peers
Observe symmetry: both listen and send

Expected Behavior
Each peer can send messages to any other peer while simultaneously receiving messages.

Common Errors (and What They Teach)
Forgetting to start listener thread → asymmetric failure
Port collisions → identity matters
Blocking input → concurrency issues

BASIC EXTENSIONS (Same Repo, Branch-Based)
Extension 1: Peer List Management
Maintain a list of known peers
Broadcast presence manually
Extension 2: Message Relay
Forward messages to another peer
Observe hop-based routing
Extension 3: Graceful Shutdown
Handle peer exit cleanly

EXTRA LAB — ADVANCED: Decentralized Chat Overlay
Advanced GitHub Repo
week05-p2p-chat-advanced
Repository Structure
week05-p2p-chat-advanced/
├── README.md
├── node.py
├── peer_table.py
├── router.py
├── config.py
└── utils/
    └── protocol.py

Advanced Lab Goals
Dynamic peer discovery
Message forwarding across peers
No central server

Advanced Concepts Introduced
Overlay networks
Decentralized routing
Partial network views

Later Application Context (Conceptual)
File-sharing networks
Blockchain peer layers
Decentralized messaging apps
Resilient mesh communication

Instructor Truth
In peer-to-peer systems, everyone is responsible—and no one is in charge.


