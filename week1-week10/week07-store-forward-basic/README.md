# WEEK 7 – Store-and-Forward Communication

**Teaching Intent**: When links fail, memory becomes the network. Students simulate nodes that detect unavailable peers, store messages, and forward them later when connectivity is restored. This is the foundation of **delay-tolerant networks**.

## Overview

This lab introduces **store-and-forward (also called delay-tolerant) networking**. Nodes maintain a message queue, detect when peers are unreachable, store messages locally, and retry delivery when connectivity is restored.

Memory is a weapon against uncertainty.

## Learning Outcomes

By completing this week, you will:
- ✅ Implement message queues
- ✅ Retry message delivery with backoff
- ✅ Handle temporary link failures gracefully
- ✅ Train traits: Patience, persistence in network programming, queue management

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Message Queue** | Local storage for messages awaiting delivery |
| **Link Availability** | Test if target peer is reachable before sending |
| **Retry Logic** | Attempt resend after delay if delivery fails |
| **Soft Timeout** | Don't give up immediately; wait and retry |
| **Asynchronous** | Retry runs independently of main thread |
| **Delay-Tolerant** | Assume links will come back eventually |

## Repository Structure

```
week07-store-forward-basic/
├── README.md                    (← you are here)
├── node.py                      (Node with store-forward logic)
├── message_queue.py             (Queue implementation)
├── config.py                    (Shared configuration)
├── phase-1-random-port/         (Variant with dynamic port discovery)
│   ├── node.py
│   ├── message_queue.py
│   └── config.py
└── docs/
    └── run_instructions.md      (Detailed execution guide)
```

## Quick Start

### 1. Configure

Edit `config.py`:

```python
HOST = "127.0.0.1"
BASE_PORT = 8000
PEER_PORTS = [8001, 8002]    # Target peers
BUFFER_SIZE = 1024
RETRY_INTERVAL = 5           # Retry every 5 seconds
```

### 2. Run Multiple Nodes (Terminal 1, 2, 3, ...)

Terminal 1 (Node 8000):
```bash
python node.py
```

Expected output:
```
[NODE 8000] Listening for messages...
```

Terminal 2 (Node 8001):
```bash
python node.py
```

Terminal 3 (Node 8002):
```bash
python node.py
```

### 3. Stop a Node to Simulate Link Failure

Terminal 2: Press Ctrl+C to stop node 8001.

### 4. Send Message During Outage (Terminal 1)

```
[NODE 8000] Listening for messages...
[NODE 8000] Peer 8001 unavailable, storing message
[NODE 8000] Stored message for 8001 (will retry)
```

### 5. Restart Node 8001

Terminal 2:
```bash
python node.py
```

**Expected**: Node 8000 automatically forwards queued messages to 8001.

Terminal 1:
```
[NODE 8000] Sent stored message to 8001
```

Terminal 2:
```
[NODE 8001] Received: Hello from node 8000
```

## Implementation Deep Dive

### Message Queue (message_queue.py)

A simple FIFO queue to store messages awaiting delivery:

```python
import time
from collections import deque

class MessageQueue:
    """Store messages awaiting delivery."""
    
    def __init__(self):
        self.queue = deque()
    
    def add_message(self, message, peer_port):
        """Add a message to queue."""
        entry = {
            "message": message,
            "peer": peer_port,
            "timestamp": time.time(),
            "attempts": 0
        }
        self.queue.append(entry)
    
    def get_messages(self):
        """Return all queued messages."""
        return list(self.queue)
    
    def remove_message(self, msg):
        """Remove a message after successful delivery."""
        self.queue.remove(msg)
    
    def inc_attempts(self, msg):
        """Increment delivery attempt count."""
        msg["attempts"] += 1
    
    def size(self):
        """Return queue size."""
        return len(self.queue)
```

**Key Points**:
- **Deque**: Efficient for add/remove at both ends
- **Metadata**: Timestamp and attempt count for analytics
- **Simple**: No persistence (loses messages on crash; extension involves disk storage)

### Node Implementation (node.py)

The node runs three concurrent tasks:
1. **Server**: Accept messages from other nodes
2. **Sender**: Attempt to send queued messages
3. **Retry loop**: Periodically check queue and retry

```python
import socket
import threading
import time
from config import HOST, BASE_PORT, PEER_PORTS, BUFFER_SIZE, RETRY_INTERVAL
from message_queue import MessageQueue

queue = MessageQueue()

# ============================================================
# TASK 1: DELIVERY ATTEMPT
# ============================================================
def send_message(peer_port, message):
    """Try to send message to peer. Return success status."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)  # 2-second timeout
        s.connect((HOST, peer_port))
        s.sendall(message.encode())
        s.close()
        return True
    except (ConnectionRefusedError, socket.timeout, OSError):
        return False

# ============================================================
# TASK 2: RETRY LOOP (Background thread)
# ============================================================
def retry_loop():
    """Periodically retry delivering queued messages."""
    while True:
        time.sleep(RETRY_INTERVAL)  # Check every N seconds
        
        # Try to deliver all queued messages
        for msg_entry in queue.get_messages():
            peer = msg_entry["peer"]
            message = msg_entry["message"]
            
            print(f"[NODE {BASE_PORT}] Retrying to {peer}... (attempt {msg_entry['attempts'] + 1})")
            
            if send_message(peer, message):
                print(f"[NODE {BASE_PORT}] Sent stored message to {peer}")
                queue.remove_message(msg_entry)
            else:
                queue.inc_attempts(msg_entry)

# ============================================================
# TASK 3: SERVER (Listen for incoming)
# ============================================================
def start_server():
    """Accept messages from other nodes."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, BASE_PORT))
    server.listen(10)
    
    print(f"[NODE {BASE_PORT}] Listening for messages...")

    while True:
        conn, addr = server.accept()
        
        try:
            data = conn.recv(BUFFER_SIZE).decode()
            print(f"[NODE {BASE_PORT}] Received: {data} from {addr}")
        except Exception as e:
            print(f"[NODE {BASE_PORT}] Error: {e}")
        finally:
            conn.close()

# ============================================================
# MAIN: Send initial messages
# ============================================================
if __name__ == "__main__":
    # Start server thread (background)
    threading.Thread(target=start_server, daemon=True).start()
    
    # Start retry thread (background)
    threading.Thread(target=retry_loop, daemon=True).start()
    
    # Send initial messages to all peers
    for peer in PEER_PORTS:
        msg = f"Hello from node {BASE_PORT}"
        
        if send_message(peer, msg):
            print(f"[NODE {BASE_PORT}] Sent to {peer}: {msg}")
        else:
            print(f"[NODE {BASE_PORT}] Peer {peer} unavailable, storing message")
            queue.add_message(msg, peer)
    
    print(f"[NODE {BASE_PORT}] Queue size: {queue.size()}")
    
    # Keep process alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n[NODE {BASE_PORT}] Shutting down")
```

**Key Points**:
- **Send function**: Returns boolean (success/failure)
- **Retry loop**: Infinite loop checking queue every RETRY_INTERVAL seconds
- **Non-blocking**: Retry happens in background; main thread still responsive
- **Attempt tracking**: Count retries to detect persistent failures (extension: give up after N attempts)

## Store-and-Forward Flow

```
Message arrives
    ↓
Try to send
    ↓
 Success? ────YES──→ Deliver, done
    │
    NO
    ↓
Store in queue
    ↓
(Every RETRY_INTERVAL seconds)
    ↓
Try again
    ↓
Success? ────YES──→ Remove from queue
    │
    NO
    ↓
Keep in queue, retry later
```

## Contrast with Previous Weeks

| Week | Delivery Model | Guarantee | Link Failure |
|------|---|---|---|
| 1 (TCP) | Direct | Guaranteed | Blocks |
| 2 (UDP) | Direct | Best-effort | Loses |
| 3 (Broadcast) | Flooding | Best-effort | Loses |
| 4 (Multicast) | Flooding | Best-effort | Loses |
| 5 (P2P) | Direct | Graceful fail | Reported error |
| 6 (MANET) | Probabilistic | Best-effort | Loses |
| 7 (Store-Forward) | **Buffered** | **Eventual** | **Retries** |

## Common Mistakes & Interpretations

| Mistake | Why It Happens | Solution |
|---------|---|---|
| **Queue grows infinitely** | Never remove delivered messages | Check `queue.remove_message()` call |
| **Retries only once** | `retry_loop()` not running | Ensure thread is daemon=True |
| **Queue never empties** | Peer never comes back online | Add max attempts limit (extension) |
| **Race condition** | Main and retry thread modify queue | Use thread-safe container (extension) |
| **No retries visible** | RETRY_INTERVAL too long | Set to smaller value (e.g., 2 seconds) |

## Testing Scenarios

### Test 1: All Peers Online

Terminal 1:
```bash
python node.py  # BASE_PORT=8000
```

Terminal 2:
```bash
python node.py  # BASE_PORT=8001
```

Terminal 3:
```bash
python node.py  # BASE_PORT=8002
```

**Expected**: All messages delivered immediately. Queue stays empty.

### Test 2: Peer Offline During Send

Terminal 1:
```bash
python node.py  # BASE_PORT=8000
```

(Don't start terminals 2 & 3)

**Expected**:
```
[NODE 8000] Peer 8001 unavailable, storing message
[NODE 8000] Peer 8002 unavailable, storing message
[NODE 8000] Queue size: 2
[NODE 8000] Retrying to 8001... (attempt 1)
[NODE 8000] Retrying to 8002... (attempt 1)
... (repeats every RETRY_INTERVAL seconds)
```

### Test 3: Peer Comes Online

Terminal 1 (already running):
```
[Already shows retry attempts]
```

Terminal 2:
```bash
python node.py  # Start node 8001
```

**Expected in Terminal 1**:
```
[NODE 8000] Retrying to 8001... (attempt 7)
[NODE 8000] Sent stored message to 8001
```

**Expected in Terminal 2**:
```
[NODE 8001] Listened for messages...
[NODE 8001] Received: Hello from node 8000 from ('127.0.0.1', XXXXX)
```

### Test 4: Multiple Nodes Exchanging

All three running. Each node tries to send to the others
(modify code to use while loop with user input to send messages dynamically).

## Real-World Applications

| System | Uses Store-Forward | Scenario |
|---|---|---|
| **SMTP Email** | Yes | Mail servers queue messages; deliver when recipient online |
| **Delay-Tolerant Networks** | Yes | Space communication (Mars rovers) |
| **Mobile Messaging** | Partially | WhatsApp/Signal queue when offline |
| **IoT Gateways** | Yes | Sensor data buffered until uplink available |
| **Disaster Networks** | Yes | First responders communicate despite patchy connectivity |

## Extension Options

### Extension A: Persistent Storage

Save queue to disk so messages survive node restart:

```python
import json

def save_queue_to_disk():
    """Serialize queue to JSON file."""
    data = queue.get_messages()
    with open(f"queue_{BASE_PORT}.json", "w") as f:
        json.dump(data, f)

def load_queue_from_disk():
    """Restore queue from JSON file."""
    try:
        with open(f"queue_{BASE_PORT}.json", "r") as f:
            data = json.load(f)
            for entry in data:
                queue.add_message(entry["message"], entry["peer"])
    except FileNotFoundError:
        pass

# In main:
load_queue_from_disk()
# And periodically: save_queue_to_disk()
```

**Result**: Messages survive node crash.

### Extension B: Exponential Backoff

Don't retry forever; back off exponentially:

```python
INITIAL_RETRY = 2      # seconds
MAX_RETRY_INTERVAL = 300  # 5 minutes

def calc_retry_interval(attempts):
    """Exponential backoff: 2, 4, 8, 16, ..., capped at 300."""
    interval = INITIAL_RETRY * (2 ** attempts)
    return min(interval, MAX_RETRY_INTERVAL)

# In retry_loop():
time_since_attempt = time.time() - msg_entry["timestamp"]
next_retry_time = calc_retry_interval(msg_entry["attempts"])

if time_since_attempt >= next_retry_time:
    # Try again
```

**Result**: Don't flood network with retries; back off gracefully.

### Extension C: Prioritized Queues

Send high-priority messages first:

```python
class PriorityMessageQueue:
    def __init__(self):
        self.high = deque()
        self.normal = deque()
    
    def add_message(self, message, peer_port, priority="normal"):
        entry = {"message": message, "peer": peer_port, "timestamp": time.time()}
        if priority == "high":
            self.high.append(entry)
        else:
            self.normal.append(entry)
    
    def get_messages(self):
        """High-priority first, then normal."""
        return list(self.high) + list(self.normal)

# Usage:
queue.add_message("URGENT: Help needed", peer_port, priority="high")
queue.add_message("Regular data", peer_port, priority="normal")
```

**Result**: Critical messages forwarded first.

### Extension D: Max Attempts + TTL

Give up on persistent failures:

```python
MAX_ATTEMPTS = 10  # Give up after 10 failed tries
MESSAGE_TTL = 3600  # Keep message for 1 hour max

# In retry_loop():
for msg_entry in queue.get_messages():
    elapsed = time.time() - msg_entry["timestamp"]
    
    # Give up if too old or too many attempts
    if msg_entry["attempts"] >= MAX_ATTEMPTS or elapsed > MESSAGE_TTL:
        print(f"[NODE {BASE_PORT}] Giving up on message to {msg_entry['peer']}")
        queue.remove_message(msg_entry)
        continue
    
    # Try again
    if send_message(msg_entry["peer"], msg_entry["message"]):
        queue.remove_message(msg_entry)
    else:
        queue.inc_attempts(msg_entry)
```

**Result**: Queue doesn't grow unbounded; messages eventually expire.

## Debugging Checklist

- [ ] Both server and retry threads running?
- [ ] Queue message added when peer unavailable?
- [ ] Retry loop running (output every RETRY_INTERVAL)?
- [ ] Messages removed after successful delivery?
- [ ] RETRY_INTERVAL small enough to observe (use 2-5 sec for testing)?
- [ ] Attempting correct peer ports?
- [ ] No encoding/decoding errors?

## Key Difference from Previous Weeks

| Feature | MANET (Week 6) | Store-Forward (Week 7) |
|---------|---|---|
| **Failure Response** | Drop message | Buffer message |
| **Retry** | No | Yes, periodic |
| **State** | Probabilistic forwarding | Persistent queue |
| **Scope** | Network-wide flooding | Point-to-point delivery |
| **Memory** | Minimal | Queue size = history |

## Key Takeaway

> Store-and-forward trades latency for reliability. Accept that delivery may take time—but make sure it succeeds eventually.

Memory is the answer to uncertain networks.

---

**Status**: ✅ Implemented. Ready for learning.  
**Last Updated**: 2025  
**Previous**: Week 6 – Ad-Hoc Networking (MANET)  
**Next**: Week 8 – Opportunistic Routing
