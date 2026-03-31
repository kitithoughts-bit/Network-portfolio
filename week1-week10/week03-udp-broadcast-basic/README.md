# WEEK 3 – Broadcast Communication (LAN-Level)

**Teaching Intent**: Week 3 teaches **controlled shouting**. Broadcast is powerful, lazy, and dangerous. Students must learn when it works, why it fails, and why modern networks try to avoid it.

## Overview

This lab introduces **UDP broadcast communication** within a local network. One sender transmits a message to **all nodes on the broadcast domain**. Receivers choose whether to listen.

No connections. No targeting. Just presence.

## Learning Outcomes

By completing this week, you will:
- ✅ Understand broadcast scope and limitations
- ✅ Implement UDP broadcast sender and receiver
- ✅ Distinguish broadcast from unicast and multicast
- ✅ Train traits: Network scope awareness, resource discipline, protocol restraint

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Broadcast Address** | `255.255.255.255` (entire LAN) or subnet-specific |
| **SO_BROADCAST** | Socket option to enable sending broadcasts |
| **One-to-Many** | One sender, all receivers on LAN |
| **LAN-Scoped** | Does NOT route beyond local network (unlike unicast) |
| **No ACK** | Sender doesn't know who received the message |

## Repository Structure

```
week03-udp-broadcast-basic/
├── README.md                    (← you are here)
├── broadcaster.py               (Broadcast sender)
├── listener.py                  (Broadcast receiver)
├── config.py                    (Shared configuration)
└── docs/
    └── run_instructions.md      (Detailed execution guide)
```

## Quick Start

### 1. Configure

Edit `config.py`:

```python
BROADCAST_IP = "255.255.255.255"  # LAN broadcast address
PORT = 7000                       # UDP port
BUFFER_SIZE = 1024
```

### 2. Run Listener(s) (Terminal 1, 2, 3, ...)

```bash
python listener.py
```

Expected output:
```
[LISTENER] Listening for broadcast on port 7000
[LISTENER] From ('127.0.0.1', XXXXX): DISCOVERY: Who is online?
```

Multiple listeners can run simultaneously; all will receive the same broadcast.

### 3. Run Broadcaster (Terminal N+1)

```bash
python broadcaster.py
```

Expected output:
```
[BROADCASTER] Message sent
```

The broadcaster sends **one message to all listeners**.

## Implementation Deep Dive

### Shared Configuration (config.py)

```python
BROADCAST_IP = "255.255.255.255"  # Broadcast address
PORT = 7000
BUFFER_SIZE = 1024
```

### Broadcaster Implementation (broadcaster.py)

The broadcaster enables the `SO_BROADCAST` option and sends:

```python
import socket
from config import BROADCAST_IP, PORT, BUFFER_SIZE

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# CRITICAL: Enable broadcast on this socket
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

# Send message to broadcast address
message = "DISCOVERY: Who is online?"
sock.sendto(message.encode(), (BROADCAST_IP, PORT))

print("[BROADCASTER] Message sent")
sock.close()
```

**Key Points**:
- **`SO_BROADCAST`**: Without this, broadcast sendto() fails silently
- **`255.255.255.255`**: Special address meaning "all nodes on this LAN"
- **`sendto()`**: Same as unicast, but destination is broadcast address
- **No reply**: Broadcaster doesn't wait for responses

### Listener Implementation (listener.py)

The listener binds to the port and waits for broadcasts:

```python
import socket
from config import PORT, BUFFER_SIZE

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind to port AND listen on ALL interfaces
sock.bind(("", PORT))  # "" means 0.0.0.0 (all interfaces)

print(f"[LISTENER] Listening for broadcast on port {PORT}")

while True:
    # recvfrom() receives ANY datagram on this port
    data, addr = sock.recvfrom(BUFFER_SIZE)
    message = data.decode()
    print(f"[LISTENER] From {addr}: {message}")
```

**Key Points**:
- **`bind(("", PORT))`**: Listen on all interfaces (not just loopback)
- **No multicast join**: Broadcast is automatic (no explicit "subscribe")
- **Simple receiver**: Just wait for datagrams

## Unicast vs Broadcast vs Multicast

### Unicast (One-to-One) – Week 1 & 2
```
Sender → Specific Receiver
         (address known ahead of time)

Example: TCP client-server, UDP unicast
```

### Broadcast (One-to-All) – Week 3
```
Sender → All receivers on LAN
         (255.255.255.255)

Example: DHCP, ARP, "anyone here?"
```

### Multicast (One-to-Group) – Week 4
```
Sender → Members of group 224.x.x.x
         (explicit subscriber list)

Example: Video streaming to subscribers only
```

## How Broadcast Works (OS Level)

```
Broadcaster sends to 255.255.255.255:7000
    ↓
OS broadcasts on physical LAN
    ↓
All NICs on LAN receive the frame
    ↓
All processes listening on :7000 get the datagram
    ↓
Listener prints: "From <sender>: <message>"
```

**Does NOT route through routers** (broadcast is LAN-local).

## Common Mistakes & Interpretations

| Mistake | Why It Happens | Solution |
|---------|---|---|
| **SO_BROADCAST not set** | Broadcast is disabled by default | Add `setsockopt(...SO_BROADCAST, 1)` |
| **Broadcaster gets "Permission denied"** | Socket doesn't have broadcast privilege | Use `SO_BROADCAST` |
| **Listener in different subnet** | Broadcast doesn't cross routers | Use subnet broadcast (e.g., `192.168.1.255`) |
| **Using unicast address** | `127.0.0.1` is loopback, not broadcast | Use `255.255.255.255` |
| **Listener binds to specific IP** | Doesn't receive broadcasts destined for `255.255.255.255` | Bind to `""` (all interfaces) |

## Testing Scenarios

### Test 1: Single Listener, Single Broadcaster

Terminal 1:
```bash
python listener.py
```

Terminal 2:
```bash
python broadcaster.py
```

**Result**: Listener prints the broadcast message.

### Test 2: Multiple Listeners, One Broadcaster

Terminal 1:
```bash
python listener.py
```

Terminal 2:
```bash
python listener.py
```

Terminal 3:
```bash
python listener.py
```

Terminal 4:
```bash
python broadcaster.py
```

**Result**: All three listeners print the same message (simultaneously).

### Test 3: Broadcaster Before Any Listener (Loss Proof)

Terminal 1:
```bash
python broadcaster.py
```

Terminal 2 (delay 2 seconds):
```bash
python listener.py
```

**Result**: Listener gets nothing (datagram already sent; UDP is not buffered).

## Real-World Applications

| Protocol | Uses Broadcast | Why |
|----------|---|---|
| **DHCP** | Yes | Client discovering DHCP servers without knowing IP |
| **ARP** | Yes | "Who has IP 192.168.1.1?" |
| **IGMP** | Yes | Host telling router "I want multicast group X" |
| **mDNS** | Yes | "Anyone know hostname 'printer.local'?" |
| **Bonjour** | Yes | Service discovery on LAN |

## Extension Options

### Extension A: Broadcast Discovery + Reply

Listeners send unicast reply back to broadcaster:

```python
# listener.py with reply
import socket
from config import PORT, BUFFER_SIZE

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", PORT))

while True:
    data, addr = sock.recvfrom(BUFFER_SIZE)
    print(f"[LISTENER] From {addr}: {data.decode()}")
    
    # Send unicast reply back to sender
    reply = "I am online"
    sock.sendto(reply.encode(), addr)
```

```python
# broadcaster.py with collection
import socket
import time
from config import BROADCAST_IP, PORT, BUFFER_SIZE

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("", PORT))  # Also listen for replies

# Send broadcast
sock.sendto(b"DISCOVERY: Who is online?", (BROADCAST_IP, PORT))
print("[BROADCASTER] Discovery sent")

# Wait for replies
sock.settimeout(2)
responses = []
while True:
    try:
        data, addr = sock.recvfrom(BUFFER_SIZE)
        responses.append(addr)
        print(f"[BROADCASTER] Reply from {addr}: {data.decode()}")
    except socket.timeout:
        break

print(f"[BROADCASTER] Total responses: {len(responses)}")
```

**Result**: Broadcaster discovers active nodes.

### Extension B: Periodic Broadcast

Send discovery every N seconds:

```python
# broadcaster.py with periodic sending
import socket
import time
from config import BROADCAST_IP, PORT

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

while True:
    message = f"DISCOVERY: {time.strftime('%H:%M:%S')}"
    sock.sendto(message.encode(), (BROADCAST_IP, PORT))
    print(f"[BROADCASTER] Sent: {message}")
    time.sleep(5)  # Every 5 seconds
```

**Result**: Network fills with discovery traffic (beware!).

### Extension C: Subnet Broadcast Address

Use subnet-specific broadcast instead of `255.255.255.255`:

```python
# E.g., for 192.168.1.0/24:
BROADCAST_IP = "192.168.1.255"
```

**Result**: Broadcast limited to specific subnet.

## Broadcast Limitations (Why It's Unpopular)

1. **Network Flooding**: Every node receives every broadcast
2. **Scalability**: N broadcast senders = N×(network devices) traffic
3. **Doesn't Cross Routers**: Limited to local LAN
4. **Wasted Resources**: Nodes receive even unwanted broadcasts
5. **No Selectivity**: Can't choose which nodes get message

**Solution**: Multicast (Week 4) solves some of these problems.

## Debugging Checklist

- [ ] `SO_BROADCAST` enabled on broadcaster?
- [ ] Listener binding to `""` (all interfaces)?
- [ ] Using `255.255.255.255` or subnet broadcast?
- [ ] Both on same LAN/subnet?
- [ ] Ports match exactly?
- [ ] No firewall blocking broadcast?
- [ ] Trying from same machine (loopback)?

## Key Takeaway

> Broadcast is shouting into a void. Everyone on the LAN hears it, and you have no idea who's listening.

Use it for discovery, but respect its crude nature.

---

**Status**: ✅ Implemented. Ready for learning.  
**Last Updated**: 2025  
**Previous**: Week 2 – UDP Unicast  
**Next**: Week 4 – UDP Multicast
