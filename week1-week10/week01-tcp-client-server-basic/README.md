# WEEK 1 – Client–Server Communication (TCP Unicast)

**Teaching Intent**: Protocol obedience. Students must feel TCP's discipline: listen before talk, connect before speak, close when finished. No shortcuts, no abstractions.

## Overview

This lab introduces socket programming through the most fundamental network model: **client–server communication**. One side listens. One side asks. Nobody panics.

## Learning Outcomes

By completing this week, you will:
- ✅ Understand TCP client–server architecture
- ✅ Implement blocking socket communication
- ✅ Relate TCP reliability to application behavior
- ✅ Train traits: Structured thinking, protocol discipline, debugging network state

## Key Concepts

| Concept | Description |
|---------|-------------|
| **TCP Sockets** | Ordered, reliable, connection-based communication |
| **bind()** | Attach socket to a local address:port |
| **listen()** | Mark socket as willing to accept connections |
| **accept()** | Wait for and establish a client connection |
| **connect()** | Initiate connection to a listening server |
| **Request–Response Pattern** | Client asks, server answers; fundamental protocol rhythm |
| **Blocking I/O** | Operations wait until complete (simple, synchronous) |

## Repository Structure

```
week01-tcp-client-server-basic/
├── README.md                    (← you are here)
├── server.py                    (TCP server implementation)
├── client.py                    (TCP client implementation)
├── server_threaded.py           (Multi-threaded variant)
├── config.py                    (Shared configuration)
├── logger.py                    (Logging utility)
├── test_concurrent.py           (Unit tests)
└── docs/
    └── run_instructions.md      (Detailed execution guide)
```

## Quick Start

### 1. Configure (if needed)

Edit `config.py` to adjust HOST, PORT, BUFFER_SIZE:

```python
HOST = "127.0.0.1"  # loopback (localhost)
PORT = 5000         # TCP port
BUFFER_SIZE = 1024  # max message size
```

### 2. Run Server (Terminal 1)

```bash
python server.py
```

Expected output:
```
[SERVER] Listening on 127.0.0.1:5000
[SERVER] Connection from ('127.0.0.1', XXXXX)
[SERVER] Received: Hello Server
[SERVER] Sent: ACK: Hello Server
[SERVER] Closed connection
```

### 3. Run Client (Terminal 2)

```bash
python client.py
```

Expected output:
```
[CLIENT] Connected to 127.0.0.1:5000
[CLIENT] Sending: Hello Server
[CLIENT] Received: ACK: Hello Server
[CLIENT] Closed connection
```

## Implementation Deep Dive

### Shared Configuration (config.py)

All scripts import from a single configuration file:

```python
HOST = "127.0.0.1"  # loopback
PORT = 5000
BUFFER_SIZE = 1024
```

**Why**: Changing behavior requires editing one file, not three.

---

### Server Implementation (server.py)

The server follows the TCP ritual in strict order:

```python
import socket
from config import HOST, PORT, BUFFER_SIZE

# Step 1: Create a TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Step 2: Bind to local address:port
server_socket.bind((HOST, PORT))

# Step 3: Listen (mark as willing to accept connections)
server_socket.listen(1)
print(f"[SERVER] Listening on {HOST}:{PORT}")

# Step 4: Accept a connection (BLOCKS until client arrives)
conn, addr = server_socket.accept()
print(f"[SERVER] Connection from {addr}")

# Step 5: Receive data
data = conn.recv(BUFFER_SIZE)
message = data.decode()
print(f"[SERVER] Received: {message}")

# Step 6: Send response
reply = f"ACK: {message}"
conn.sendall(reply.encode())

# Step 7: Close connection
conn.close()
server_socket.close()
print("[SERVER] Closed connection")
```

**Key Points**:
- `socket.AF_INET`: IPv4 addressing
- `socket.SOCK_STREAM`: TCP protocol
- `bind()`: Must happen before listen()
- `listen(1)`: Queue up to 1 pending connection
- `accept()`: **Blocking call** — waits for client
- `recv()`: **Blocking call** — waits for data
- Order matters. TCP is a ritual.

---

### Client Implementation (client.py)

The client is simpler but must respect the server's state:

```python
import socket
from config import HOST, PORT, BUFFER_SIZE

# Step 1: Create a TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Step 2: Connect to server (BLOCKS until connection accepted)
client_socket.connect((HOST, PORT))

# Step 3: Send message
message = "Hello Server"
client_socket.sendall(message.encode())

# Step 4: Receive response
response = client_socket.recv(BUFFER_SIZE)
print(f"[CLIENT] Received: {response.decode()}")

# Step 5: Close connection
client_socket.close()
```

**Key Points**:
- `connect()`: **Blocks until** server's accept() succeeds
- `sendall()`: Guarantees all bytes sent (or exception)
- `recv()`: **Blocks until** data arrives
- Handshake happens transparently (TCP 3-way handshake)

---

### Multi-Threaded Variant (server_threaded.py)

For handling multiple clients sequentially or concurrently:

```python
import socket
import threading
from config import HOST, PORT, BUFFER_SIZE

def handle_client(conn, addr):
    print(f"[SERVER] Connection from {addr}")
    data = conn.recv(BUFFER_SIZE)
    message = data.decode()
    print(f"[SERVER] Received: {message}")
    
    reply = f"ACK: {message}"
    conn.sendall(reply.encode())
    conn.close()
    print(f"[SERVER] Closed {addr}")

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f"[SERVER] Listening on {HOST}:{PORT}")

while True:
    conn, addr = server_socket.accept()
    # Spawn thread to handle this client
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.daemon = True
    thread.start()
```

**Why threads?** One server can now serve multiple clients at once.

---

## Common Mistakes & Interpretations

| Mistake | Why It Happens | How to Debug |
|---------|---|---|
| **Missing `listen()`** | Forget the server must advertise readiness | `socket error: (98) Address already in use` or immediate failure |
| **Port already in use** | Previous server didn't close cleanly | `netstat -ano` (Windows) or `lsof -i :5000` (Mac/Linux) to find PID |
| **`recv()` blocks forever** | Server waits for client that never comes | Check: Is server running? Did client actually connect? |
| **Empty message crashes** | Forgot to check `if data:` | Receive returns empty bytes `b''` when peer closes |
| **Encoding errors** | String ↔ bytes conversion | Use `.encode()` and `.decode()` consistently |

## Testing

Run unit tests:

```bash
python -m pytest test_concurrent.py -v
```

Or manually:

1. Start server
2. Send message via client
3. Verify ACK received
4. Modify message content
5. Repeat

---

## Extension Options (Try After Basics Work)

### Extension A: Sequential Multiple Clients

Wrap `accept()` in a loop so server stays alive:

```python
while True:
    conn, addr = server_socket.accept()
    # ... handle client ...
    conn.close()
```

**Result**: Kill server with Ctrl+C; clients can connect repeatedly.

### Extension B: Message Validation

Reject invalid messages:

```python
data = conn.recv(BUFFER_SIZE)
message = data.decode().strip()

if not message:
    conn.sendall(b"ERROR: Empty message")
    conn.close()
    continue

if len(message) > 100:
    conn.sendall(b"ERROR: Message too long")
    conn.close()
    continue

# ... process valid message ...
```

### Extension C: Timeout Handling

Prevent infinite hangs:

```python
client_socket.settimeout(5.0)  # 5 seconds

try:
    response = client_socket.recv(BUFFER_SIZE)
except socket.timeout:
    print("[CLIENT] Server did not respond in time")
```

### Extension D: Concurrent Clients

See `server_threaded.py` for full concurrent implementation.

---

## Advanced Lab: Mini Chat Server

### Purpose

Introduce **state, repetition, and responsibility** while staying inside TCP.

### Scenario

Build a *helpdesk chat server* where:
- Server runs indefinitely
- Each client can send multiple messages (session)
- Messages are logged with timestamps
- Server acknowledges each message
- Clients disconnect cleanly

### Real-World Mapping

- **Call centers**: Operator (server) handles caller (client) inquiry
- **Ticketing systems**: Customer submits request; system acknowledges
- **Chat platforms**: Client connects, exchanges multiple messages, disconnects

### Requirements

1. Server accepts single connection
2. Loop: receive message → log → echo response
3. Client: send 3 messages, then disconnect
4. Timestamps on server logs

### Starter Code (Advanced)

**server.py (chat version)**:
```python
import socket
import time
from config import HOST, PORT, BUFFER_SIZE

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)
print(f"[SERVER] Listening on {HOST}:{PORT}")

conn, addr = server_socket.accept()
print(f"[SERVER] @{time.strftime('%H:%M:%S')} Connection from {addr}")

while True:
    data = conn.recv(BUFFER_SIZE)
    if not data:
        break
    
    message = data.decode()
    timestamp = time.strftime('%H:%M:%S')
    print(f"[SERVER] @{timestamp} Client: {message}")
    
    reply = f"[ACK @{timestamp}] {message}"
    conn.sendall(reply.encode())

conn.close()
server_socket.close()
```

**client.py (chat version)**:
```python
import socket
from config import HOST, PORT, BUFFER_SIZE

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

messages = [
    "Hello, can you help?",
    "I have a problem with my account",
    "Thank you, goodbye"
]

for message in messages:
    client_socket.sendall(message.encode())
    response = client_socket.recv(BUFFER_SIZE)
    print(f"[CLIENT] {response.decode()}")

client_socket.close()
```

---

## Forward Application Hooks

This lab becomes the foundation for:

- **Week 2**: UDP contrast (no ACKs, unreliable)
- **Week 5**: Peer-to-peer nodes (symmetric roles)
- **Week 7**: Store-and-forward servers (message persistence)
- **Security labs**: Authentication, TLS, zero trust

---

## Instructor Truth

> If students rush past Week 1, every future lab will collapse quietly.

The TCP ritual is not busywork. It is **protocol obedience**. Students who internalize this week understand why reliability matters, why order matters, and why closing properly matters.

---

## Debugging Checklist

- [ ] Server running in Terminal 1?
- [ ] Client can reach HOST:PORT?
- [ ] `listen(1)` before `accept()`?
- [ ] `recv()` handles empty messages?
- [ ] `sendall()` not just `send()`?
- [ ] Sockets closed before exit?
- [ ] No encoding/decoding errors?

---

## Resources

- Python socket docs: https://docs.python.org/3/library/socket.html
- TCP/IP sockets tutorial: https://realpython.com/python-sockets/
- Wireshark (packet analysis): https://www.wireshark.org/

---

**Status**: ✅ Implemented. Ready for learning.  
**Last Updated**: 2025  
**Next**: Week 2 – UDP Unicast (Connectionless, Unreliable)
