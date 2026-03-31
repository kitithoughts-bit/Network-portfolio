# WEEK 5 – Peer-to-Peer Networking

**Teaching Intent**: Week 5 breaks habits. There is **no server to blame, no client to obey**. Every node must listen and speak, often at the same time. Peer-to-peer networking teaches symmetry, decentralization, and responsibility.

## Overview

This lab introduces **peer-to-peer (P2P) communication** using Python sockets. Each node acts as both a **server and a client**, accepting incoming connections while initiating outbound ones.

There is no central authority—only cooperation.

## Learning Outcomes

By completing this week, you will:
- ✅ Explain the peer-to-peer communication model
- ✅ Implement a node that acts as both client and server
- ✅ Manage concurrent send/receive behavior
- ✅ Train traits: Systems thinking, decentralized reasoning, failure tolerance

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Symmetric Roles** | Client = Server (both listen and connect) |
| **No Central Hub** | No distinguished "server" node |
| **Listener Thread** | Background thread accepting incoming connections |
| **Sender Function** | Main thread initiating outbound connections |
| **Concurrency** | Two threads working simultaneously |
| **Decentralization** | Each node responsible for its own connections |

## Repository Structure

```
week05-peer-to-peer-basic/
├── README.md                    (← you are here)
├── peer.py                      (P2P node implementation)
├── config.py                    (Shared configuration)
└── docs/
    └── run_instructions.md      (Detailed execution guide)
```

## Quick Start

### 1. Configure

Edit `config.py`:

```python
HOST = "127.0.0.1"  # loopback
BASE_PORT = 9000    # Starting port for peers
BUFFER_SIZE = 1024
```

### 2. Run Peer 1 (Terminal 1)

```bash
python peer.py 1
```

Expected output:
```
[PEER 1] Listening on 9001
```

Peer 1 listens on port 9001 and waits for connections.

### 3. Run Peer 2 (Terminal 2)

```bash
python peer.py 2
```

Expected output:
```
[PEER 2] Listening on 9002
Send to peer ID: _
```

Peer 2 listens on port 9002 and is ready to send.

### 4. Send Message (Terminal 2)

```
Send to peer ID: 1
Message: Hello from peer 2
```

Expected output in Terminal 1:
```
[PEER 1] From ('127.0.0.1', XXXXX): Hello from peer 2
```

## Implementation Deep Dive

### Shared Configuration (config.py)

```python
HOST = "127.0.0.1"
BASE_PORT = 9000  # Peers use BASE_PORT + peer_id
BUFFER_SIZE = 1024
```

Peer 1 uses port 9001, peer 2 uses 9002, etc.

### Peer Implementation (peer.py)

The peer runs two concurrent tasks:
1. **Listener**: Background thread accepting incoming messages
2. **Sender**: Main thread sending messages to other peers

```python
import socket
import threading
import sys
from config import HOST, BASE_PORT, BUFFER_SIZE

# Get peer ID from command line
peer_id = int(sys.argv[1])
PORT = BASE_PORT + peer_id

# ============================================================
# TASK 1: LISTENER THREAD (accept incoming connections)
# ============================================================
def listen():
    """Accept messages from other peers."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)  # Queue up to 5 pending connections
    
    print(f"[PEER {peer_id}] Listening on {PORT}")

    while True:
        # Accept a connection from another peer
        conn, addr = server_socket.accept()
        
        # Receive message
        data = conn.recv(BUFFER_SIZE)
        message = data.decode()
        print(f"[PEER {peer_id}] From {addr}: {message}")
        
        # Close connection
        conn.close()

# ============================================================
# TASK 2: SENDER FUNCTION (initiate connections to peers)
# ============================================================
def send_message(target_peer_id, message):
    """Send message to a target peer."""
    target_port = BASE_PORT + target_peer_id
    
    try:
        # Initiate connection to target peer
        sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sender_socket.connect((HOST, target_port))
        
        # Send message
        sender_socket.sendall(message.encode())
        print(f"[PEER {peer_id}] Sent to peer {target_peer_id}: {message}")
        
        # Close connection
        sender_socket.close()
    except ConnectionRefusedError:
        print(f"[PEER {peer_id}] ERROR: Peer {target_peer_id} is not online")
    except Exception as e:
        print(f"[PEER {peer_id}] ERROR: {e}")

# ============================================================
# MAIN: Start listener in background, handle user input
# ============================================================
if __name__ == "__main__":
    # Start listener thread (background daemon)
    listener_thread = threading.Thread(target=listen, daemon=True)
    listener_thread.start()

    # Main thread: accept user input and send messages
    while True:
        try:
            target = int(input("Send to peer ID: "))
            msg = input("Message: ")
            send_message(target, msg)
        except ValueError:
            print("[PEER] Invalid input. Enter peer ID as integer.")
        except KeyboardInterrupt:
            print(f"\n[PEER {peer_id}] Shutting down")
            break
```

**Key Points**:
- **Threading**: Listener runs in background; sender in main thread
- **Symmetric**: Each peer listens on a port AND connects to other ports
- **Dynamic ports**: Peer ID determines port (no hardcoding)
- **Error handling**: Graceful failure if target peer is offline

## P2P Architecture

```
Peer 1 (port 9001)          Peer 2 (port 9002)
  |                           |
  |--- receiver thread -----  |--- receiver thread
  |    (listening for          |    (listening for
  |     incoming)              |     incoming)
  |                           |
  |  main thread -------- msg ---|> (accepted here)
  |  (user input,          
  |   sends messages)
  |
  |<---- msg --------------- main thread
       (accepted by        (user input,
        receiver)          sends messages)
```

Both peers are simultaneously listening and sending.

## Comparison: Client-Server vs Peer-to-Peer

### Client-Server (Week 1)
```
    CLIENT              SERVER
      |                   |
      |--- connect ------->|
      |                   |
      |<-- accept ---------|
      |                   |
      |--- send ---------->|
      |<-- reply ---------|
```
- **Asymmetric roles**: One listener, many clients
- **Centralized**: Server is authority
- **Simple**: Clear flow of communication

### Peer-to-Peer (Week 5)
```
    PEER 1              PEER 2
      |                   |
      |--- listen ---      |--- listen ---
      |                   |
      |<-- connect -------|--> connect ---
      |                   |
      |--- send <--------- send -------->|
```
- **Symmetric roles**: All nodes equal
- **Decentralized**: No central hub
- **Complex**: Bidirectional communication

## Common Mistakes & Interpretations

| Mistake | Why It Happens | Solution |
|---------|---|---|
| **Listener blocks sender** | Forgot `daemon=True` | Make listener thread a daemon |
| **Port collisions** | Multiple nodes same port | Use `BASE_PORT + peer_id` |
| **Peer "not online"** | Didn't start target peer | Start both peers before sending |
| **Sender waits forever** | No timeout set | Add timeout to connect() |
| **Race condition** | Peers try to connect simultaneously | Asynchronous design handles this |

## Testing Scenarios

### Test 1: Two Peers, Bidirectional Communication

Terminal 1:
```bash
python peer.py 1
```

Terminal 2:
```bash
python peer.py 2
Send to peer ID: 1
Message: Hello from peer 2
```

Terminal 1 receives:
```
[PEER 1] From ('127.0.0.1', XXXXX): Hello from peer 2
Send to peer ID: 2
Message: Reply from peer 1
```

Terminal 2 receives:
```
[PEER 2] From ('127.0.0.1', XXXXX): Reply from peer 1
```

**Result**: True bidirectional P2P communication.

### Test 2: Three Peers

Terminal 1: `python peer.py 1`
Terminal 2: `python peer.py 2`
Terminal 3: `python peer.py 3`

Each peer can send to any other:
- Peer 1 → Peer 2
- Peer 2 → Peer 3
- Peer 3 → Peer 1

**Result**: Full mesh network topology.

### Test 3: Peer Offline During Send

Terminal 1: `python peer.py 1`
Terminal 2: `python peer.py 2`

Terminal 2 sends to peer 3 (doesn't exist):
```
Send to peer ID: 3
Message: Will this work?
[PEER 2] ERROR: Peer 3 is not online
```

**Result**: Graceful error, no crash.

## Real-World Applications

| System | Uses P2P | Why |
|---|---|---|
| **BitTorrent** | Yes | All peers share upload/download |
| **IPFS** | Yes | Decentralized file storage |
| **Ethereum** | Yes | No central server; consensus via peers |
| **Discord** | Partially | Voice uses P2P overlay |
| **Skype** | Partially | Some traffic overlayed peer-to-peer |

## Extension Options

### Extension A: Peer List Management

Maintain list of known peers:

```python
# peer_with_registry.py
KNOWN_PEERS = [1, 2, 3, 4, 5]  # In real P2P, discover dynamically

def list_peers():
    """Show all known peers."""
    print(f"[PEER {peer_id}] Known peers: {KNOWN_PEERS}")

def broadcast_message(message):
    """Send same message to all known peers."""
    for target_id in KNOWN_PEERS:
        if target_id != peer_id:
            send_message(target_id, message)

# In main loop:
#   "broadcast" command → calls broadcast_message()
```

**Result**: Send to multiple peers at once.

### Extension B: Message Relay

Forward messages to another peer:

```python
def relay_message(target_peer_id, message):
    """Receive message, forward to another peer."""
    send_message(target_peer_id, f"[relayed] {message}")

# In listen():
#   if message.startswith("relay"):
#       relay_message(...)
```

**Result**: Messages can traverse multiple hops.

### Extension C: Graceful Shutdown

Handle cleanup on exit:

```python
import atexit

def shutdown():
    """Clean shutdown."""
    print(f"\n[PEER {peer_id}] Closing connections...")
    # Save state, notify other peers, etc.

atexit.register(shutdown)
```

**Result**: Proper resource cleanup.

### Extension D: Persistent Peer Discovery

Discover peers dynamically instead of hardcoding:

```python
# In addition to direct connections, query a directory service
def discover_peers():
    """Connect to directory to find active peers."""
    # Could be centralized (directory server)
    # or distributed (broadcast ping)
    pass
```

**Result**: Self-healing peer list.

## Threading Deep Dive

### Why Background Thread?

```python
listener_thread = threading.Thread(target=listen, daemon=True)
listener_thread.start()
```

- **Non-blocking**: Main thread continues to `input()` loop
- **Simultaneous**: Listener runs while user types commands
- **daemon=True**: Thread stops when main thread exits

### Communication Between Threads

The listener and sender share:
- Peer ID
- Port number
- Message buffer

No explicit synchronization needed (each uses different sockets).

## Key Takeaway

> In P2P, every node is responsible. No server to hide behind, no client to blame. You cooperate or you fail.

It's harder than client-server, but far more resilient.

---

**Status**: ✅ Implemented. Ready for learning.  
**Last Updated**: 2025  
**Previous**: Week 4 – UDP Multicast  
**Next**: Week 6 – Ad-Hoc Networking (MANET)
