WEEK 1 – BASIC: Client–Server Communication (TCP Unicast)

Teaching Intent (Instructor Note)
Week 1 is about protocol obedience. Students must feel TCP’s discipline: listen before talk, connect before speak, close when finished. No shortcuts, no abstractions.

Overview
This lab introduces socket programming through the most fundamental network model: client–server communication. One side listens. One side asks. Nobody panics.

Learning Outcome / Trait Assessment
Understand TCP client–server architecture
Implement blocking socket communication
Relate TCP reliability to application behavior
Traits trained: - Structured thinking - Protocol discipline - Debugging network state

Key Concepts
TCP sockets
bind(), listen(), accept(), connect()
Request–response pattern
Blocking I/O behavior

BASIC LAB — GitHub Scaffold (Student Starter Repo)
Repository Name
week01-tcp-client-server-basic
Directory Structure
week01-tcp-client-server-basic/
├── README.md
├── server.py
├── client.py
├── config.py
└── docs/
    └── run_instructions.md

BASIC LAB — Step-by-Step Implementation
Step 0: Shared Configuration
# config.py
HOST = "127.0.0.1"  # loopback
PORT = 5000
BUFFER_SIZE = 1024

Step 1–3: Create, Bind, and Listen (Server)
# server.py
import socket
from config import HOST, PORT, BUFFER_SIZE

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"[SERVER] Listening on {HOST}:{PORT}")

Step 4: Accept a Client Connection
conn, addr = server_socket.accept()
print(f"[SERVER] Connection from {addr}")

Step 5–6: Receive Data and Send Response
data = conn.recv(BUFFER_SIZE)
message = data.decode()
print(f"[SERVER] Received: {message}")

reply = f"ACK: {message}"
conn.sendall(reply.encode())

Step 7: Close the Connection
conn.close()
server_socket.close()
print("[SERVER] Closed connection")

Client Implementation
# client.py
import socket
from config import HOST, PORT, BUFFER_SIZE

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

message = "Hello Server"
client_socket.sendall(message.encode())

response = client_socket.recv(BUFFER_SIZE)
print(f"[CLIENT] Received: {response.decode()}")

client_socket.close()

Execution & Verification
Terminal 1: python server.py
Terminal 2: python client.py
Observe ACK message
Modify message content and repeat

Expected Output
Client sends text → Server responds with acknowledgment

Common Mistakes (and Why They Matter)
Missing listen() → server violates TCP ritual
Port already in use → OS-level resource contention
recv() blocks forever → protocol deadlock

BASIC EXTENSION OPTIONS (Same Repo, New Branches)
Extension A: Sequential Multiple Clients
Wrap accept() in a loop
Server stays alive
Extension B: Message Validation
Reject empty messages
Enforce message length
Extension C: Timeout Handling
Set socket timeout
Handle unresponsive peers

EXTRA LAB — ADVANCED: Mini Chat Server
Purpose
Introduce state, repetition, and responsibility while staying inside TCP.

Advanced Repository
week01-tcp-chat-server-advanced
Directory Structure
week01-tcp-chat-server-advanced/
├── README.md
├── server/
│   ├── server.py
│   ├── client_handler.py
│   └── logger.py
├── client/
│   └── client.py
└── config.py

Advanced Requirements
Server runs indefinitely
Handles multiple clients sequentially or via threads
Logs all messages with timestamps
Clean disconnect handling

Advanced Concepts Introduced
Server lifecycle management
Basic concurrency (threading)
Application-layer protocol design

Real-World Mapping
Call centers
Customer support systems
Ticketing backends

Forward Application Hooks
This lab becomes the foundation for: - Week 2: UDP contrast (no ACKs) - Week 5: Peer-to-peer nodes - Week 7: Store-and-forward servers - Security labs (auth, TLS, zero trust)

Instructor Truth
If students rush past Week 1, every future lab will collapse quietly.

EXTRA LAB: Mini Chat Server
Scenario: Build a helpdesk chat server where multiple clients can connect sequentially.
Real-world mapping: Call centers, ticketing systems

