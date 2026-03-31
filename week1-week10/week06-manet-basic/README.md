# WEEK 6 – Ad-Hoc Networking (MANET Simulation)

**Teaching Intent**: Infrastructure disappears. Nodes improvise. Students simulate mobile nodes that discover neighbors and forward messages probabilistically. This is how real rescue networks work.

## Overview

This lab introduces **Mobile Ad-Hoc Network (MANET) simulation**. Nodes maintain a neighbor table dynamically, forward messages with TTL (Time-To-Live), and operate in the absence of fixed infrastructure.

There is no router. Each node is the router.

## Learning Outcomes

By completing this week, you will:
- ✅ Maintain a neighbor table dynamically
- ✅ Forward packets with TTL and probability
- ✅ Understand the basics of MANET routing
- ✅ Train traits: Adaptive thinking, probabilistic reasoning, debugging dynamic network states

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Ad-Hoc Network** | No infrastructure; nodes form network on-the-fly |
| **Neighbor Discovery** | Nodes learn about nearby peers dynamically |
| **Probabilistic Forwarding** | Forward messages with N% chance (not guaranteed) |
| **TTL** | Hop count to prevent infinite loops |
| **Soft State** | Table entries go stale (nodes may disappear) |
| **Mobility** | Nodes can move; topology changes constantly |

## Repository Structure

```
week06-manet-basic/
├── README.md                    (← you are here)
├── node.py                      (MANET node implementation)
├── config.py                    (Shared configuration)
├── phase-1-random-port/         (Variant with dynamic port discovery)
│   ├── node.py
│   └── config.py
└── docs/
    └── run_instructions.md      (Detailed execution guide)
```

## Quick Start

### 1. Configure

Edit `config.py`:

```python
HOST = "127.0.0.1"
BASE_PORT = 7000
BUFFER_SIZE = 1024
NEIGHBORS = [7001, 7002]      # Initial neighbor ports
FORWARD_PROBABILITY = 0.5     # 50% chance to forward
TTL = 3                       # Max 3 hops
```

### 2. Run Multiple Nodes (Terminal 1, 2, 3, ...)

Terminal 1:
```bash
# Modify config.py: BASE_PORT = 7000
python node.py
```

Expected output:
```
[NODE 7000] Listening for neighbors...
```

Terminal 2:
```bash
# Modify config.py: BASE_PORT = 7001
python node.py
```

Terminal 3:
```bash
# Modify config.py: BASE_PORT = 7002
python node.py
```

All nodes are now online, each knowing about the others (from NEIGHBORS config).

### 3. Observe Message Propagation

Node at 7000 sends a message: it propagates to 7001 and 7002, potentially bouncing around based on TTL and FORWARD_PROBABILITY.

## Implementation Deep Dive

### Shared Configuration (config.py)

```python
HOST = "127.0.0.1"
BASE_PORT = 7000          # Port for this node
NEIGHBORS = [7001, 7002]  # Known peers (in real systems, discovered dynamically)
FORWARD_PROBABILITY = 0.5 # 50% chance to forward each message
TTL = 3                   # Max hops before message dies
BUFFER_SIZE = 1024
```

In real MANETs, the neighbor list changes dynamically (nodes move in/out of range).

### Node Implementation (node.py)

The node listens for incoming messages and forwards them probabilistically:

```python
import socket
import threading
import random
from config import HOST, BASE_PORT, BUFFER_SIZE, NEIGHBORS, FORWARD_PROBABILITY, TTL

neighbor_table = set(NEIGHBORS)

# ============================================================
# HANDLER: Process incoming message
# ============================================================
def handle_incoming(conn, addr):
    """Receive and process a message from a neighbor."""
    try:
        data = conn.recv(BUFFER_SIZE).decode()
        parts = data.split('|')
        
        if len(parts) == 2:
            msg, ttl_str = parts
            ttl = int(ttl_str)
        else:
            msg = data
            ttl = 0
        
        print(f"[NODE {BASE_PORT}] Received from {addr}: '{msg}' (TTL={ttl})")
        
        # Forward message if TTL > 0 and probability check passes
        if ttl > 0 and random.random() < FORWARD_PROBABILITY:
            forward_message(msg, ttl - 1, exclude_port=addr[1])
    
    except Exception as e:
        print(f"[NODE {BASE_PORT}] Error: {e}")
    finally:
        conn.close()

# ============================================================
# SERVER: Accept incoming connections
# ============================================================
def start_server():
    """Listen for messages from neighbors."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, BASE_PORT))
    server.listen(10)
    
    print(f"[NODE {BASE_PORT}] Listening for neighbors...")

    while True:
        conn, addr = server.accept()
        # Handle each connection in a thread (non-blocking)
        threading.Thread(target=handle_incoming, args=(conn, addr), daemon=True).start()

# ============================================================
# FORWARD: Send message to neighbors
# ============================================================
def forward_message(message, ttl, exclude_port=None):
    """Probabilistically forward message to neighbors."""
    for neighbor_port in neighbor_table:
        # Don't send back to sender
        if neighbor_port == exclude_port:
            continue
        
        try:
            # Open connection to neighbor
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((HOST, neighbor_port))
            
            # Send message with TTL
            payload = f"{message}|{ttl}"
            s.sendall(payload.encode())
            print(f"[NODE {BASE_PORT}] Forwarding to {neighbor_port}: '{message}' (TTL={ttl})")
            
            s.close()
        except ConnectionRefusedError:
            print(f"[NODE {BASE_PORT}] Neighbor {neighbor_port} unreachable")
        except Exception as e:
            print(f"[NODE {BASE_PORT}] Error forwarding to {neighbor_port}: {e}")

# ============================================================
# MAIN: Start server and send test message
# ============================================================
if __name__ == "__main__":
    # Start server in background
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Send initial test message
    test_message = f"Hello from node {BASE_PORT}"
    forward_message(test_message, TTL)
    
    # Keep process alive
    while True:
        threading.Event().wait(1)
```

**Key Points**:
- **Neighbor table**: Static (config.py) or dynamic (extended version)
- **Probabilistic forwarding**: `random.random() < 0.5` means 50% chance
- **TTL decrement**: Each hop reduces TTL by 1
- **Exclude sender**: Don't forward back to node that sent it
- **Threading**: Each connection handled in separate thread

## MANET Characteristics

### 1. Dynamic Topology
```
Time T=0:
Node A --- Node B --- Node C

Time T=10s (mobility):
Node A    Node B --- Node C
   |_________|
(A moved closer to B)

Time T=20s:
Node A - Node B    Node C
           |________|
(C moved into range)
```

### 2. Probabilistic Routing
```
If FORWARD_PROBABILITY = 0.5:

Incoming message → Random check → 50% forward, 50% drop
                    |
                    v
              Send to neighbors with TTL-1
```

### 3. TTL Prevents Loops
```
A sends "Hello" with TTL=3
    ↓
B receives, forwards with TTL=2
    ↓
C receives, forwards with TTL=1
    ↓
D receives, forwards with TTL=0
    ↓
(No one forwards TTL=0 message; loop stops)
```

## Common Mistakes & Interpretations

| Mistake | Why It Happens | Solution |
|---------|---|---|
| **Messages disappear** | Low FORWARD_PROBABILITY or TTL too low | Increase probability or TTL |
| **Messages loop forever** | Forgot to decrement TTL | Always do `ttl - 1` when forwarding |
| **Can't reach distant nodes** | TTL too low for network size | Set TTL ≥ max network diameter |
| **Same message sent twice** | No duplicate detection | Add message ID tracking (extension) |
| **Node never receives messages** | Not in neighbor's table | Update NEIGHBORS in config.py |

## Testing Scenarios

### Test 1: Simple Three-Node Chain

```
Node 7000 --- Node 7001 --- Node 7002
```

Config:
- Node 7000: `NEIGHBORS = [7001]`
- Node 7001: `NEIGHBORS = [7000, 7002]`
- Node 7002: `NEIGHBORS = [7001]`

Set `FORWARD_PROBABILITY = 1.0` (always forward).

Terminal 1: `node.py` (BASE_PORT=7000)
Terminal 2: `node.py` (BASE_PORT=7001)
Terminal 3: `node.py` (BASE_PORT=7002)

**Expected**: Message from 7000 → 7001 → 7002

### Test 2: Variable Forwarding Probability

Change `FORWARD_PROBABILITY = 0.5` (50% chance).

Send multiple messages from node 7000.

**Expected**: Some messages reach node 7002, some don't (stochastic drops).

### Test 3: Out-of-Range Neighbor (Unreachable)

Config:
- Node 7000: `NEIGHBORS = [7999]` (doesn't exist)

**Expected**: Connection refused, message logged as unreachable.

## Real-World Applications

| System | Uses MANET | Scenario |
|---|---|---|
| **Disaster Response** | Yes | Search and rescue coordination |
| **Military** | Yes | Communication without infrastructure |
| **IoT Sensors** | Partially | Environmental monitoring mesh |
| **UAV Swarms** | Yes | Drone networks (no ground control) |
| **Emergency Services** | Yes | First responders in blind zones |

## Extension Options

### Extension A: Dynamic Neighbor Discovery

Instead of hardcoded NEIGHBORS, nodes discover each other:

```python
def discover_neighbors():
    """Ping port range to find online nodes."""
    neighbors = set()
    
    for port in range(BASE_PORT, BASE_PORT + 10):
        if port == BASE_PORT:  # Skip self
            continue
        
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            result = s.connect_ex((HOST, port))
            
            if result == 0:
                neighbors.add(port)
            
            s.close()
        except:
            pass
    
    return neighbors

# Periodically update neighbors
while True:
    neighbor_table = discover_neighbors()
    print(f"[NODE {BASE_PORT}] Neighbors: {neighbor_table}")
    time.sleep(5)
```

**Result**: Nodes automatically find each other (no config needed).

### Extension B: Mobility Simulation

Dynamically add/remove neighbors to simulate movement:

```python
def simulate_mobility():
    """Randomly change neighbors to simulate node movement."""
    all_potential = [7000, 7001, 7002, 7003, 7004]
    
    while True:
        # Every 10 seconds, randomly select 2-3 neighbors (simulating movement)
        neighbor_table = set(random.sample([p for p in all_potential if p != BASE_PORT], 2))
        
        print(f"[NODE {BASE_PORT}] Now neighbors with: {neighbor_table}")
        time.sleep(10)

# Run in background
threading.Thread(target=simulate_mobility, daemon=True).start()
```

**Result**: Topology dynamically changes; observe network resilience.

### Extension C: Delivery Metrics

Track message delivery success rate:

```python
class MessageMetrics:
    def __init__(self):
        self.sent = 0
        self.delivered = 0
    
    def record_send(self):
        self.sent += 1
    
    def record_delivery(self):
        self.delivered += 1
    
    def success_rate(self):
        return self.delivered / self.sent if self.sent > 0 else 0

metrics = MessageMetrics()

# Track in forward_message() and handle_incoming()
# At end: print(f"Delivery rate: {metrics.success_rate():.1%}")
```

**Result**: Measure network reliability with probabilistic routing.

## Debugging Checklist

- [ ] All nodes starting (listening output)?
- [ ] NEIGHBORS config matches running nodes?
- [ ] FORWARD_PROBABILITY between 0.0 and 1.0?
- [ ] TTL >= estimated hop count to destination?
- [ ] No "Connection refused" that shouldn't exist?
- [ ] Messages appear in receiving node's output?

## Key Difference from P2P (Week 5)

| Feature | P2P (Week 5) | MANET (Week 6) |
|---------|---|---|
| **Topology** | Known static | Dynamic, changing |
| **Forwarding** | Direct or relay | Probabilistic flooding |
| **TTL** | Not used | Prevents loops |
| **Discovery** | Manual (hardcoded) | Auto-discovery possible |
| **Reliability** | Intentional loss | Inherent loss |
| **Scale** | Few peers | Many nodes |

## Key Takeaway

> MANETs assume infrastructure doesn't exist. Design nodes that cooperate despite uncertainty.

Probabilistic forwarding teaches resilience: if one path fails, another may succeed.

---

**Status**: ✅ Implemented. Ready for learning.  
**Last Updated**: 2025  
**Previous**: Week 5 – Peer-to-Peer  
**Next**: Week 7 – Store-and-Forward
