# WEEK 4 – Multicast Communication

**Teaching Intent**: This week is about **selective listening**. Multicast is neither shouting nor whispering. It is joining a channel and agreeing to hear only those who speak on it. Students must internalize that multicast is about membership and scope, not guaranteed delivery.

## Overview

This lab introduces **UDP-based IP multicast**. One sender transmits to a multicast group address. Only receivers that explicitly join that group will receive the data.

Multicast trades universality for scalability.

## Learning Outcomes

By completing this week, you will:
- ✅ Differentiate multicast from broadcast and unicast
- ✅ Implement multicast sender and receiver in Python
- ✅ Explain group membership and TTL scope
- ✅ Train traits: Selective attention, scalability reasoning, protocol exactness

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Multicast Address** | `224.0.0.0` to `239.255.255.255` (reserved range) |
| **Group Membership** | Receivers *join* a group; senders just send |
| **`IP_ADD_MEMBERSHIP`** | Socket option to subscribe to group |
| **`IP_MULTICAST_TTL`** | Limit scope (1 = local LAN, 255 = internet) |
| **Selective Delivery** | Non-members don't receive (unlike broadcast) |

## Repository Structure

```
week04-udp-multicast-basic/
├── README.md                    (← you are here)
├── sender.py                    (Multicast sender)
├── receiver.py                  (Multicast receiver)
├── config.py                    (Shared configuration)
└── docs/
    └── run_instructions.md      (Detailed execution guide)
```

## Quick Start

### 1. Configure

Edit `config.py`:

```python
MULTICAST_GROUP = "224.1.1.1"  # Multicast address (class D)
PORT = 8000                     # UDP port
BUFFER_SIZE = 1024
TTL = 1                         # 1 = local LAN only
```

### 2. Run Receiver (Terminal 1, 2, 3, ...)

```bash
python receiver.py
```

Expected output:
```
[RECEIVER] Joined 224.1.1.1:8000
[RECEIVER] ('127.0.0.1', XXXXX) -> MULTICAST: Hello subscribers
```

Each receiver **joins the group**. They won't receive messages until they're subscribed.

### 3. Run Sender (Terminal N+1)

```bash
python sender.py
```

Expected output:
```
[SENDER] Multicast sent
```

The sender sends **one message to the group address**. Only members receive it.

## Implementation Deep Dive

### Shared Configuration (config.py)

```python
MULTICAST_GROUP = "224.1.1.1"  # Multicast address
PORT = 8000
BUFFER_SIZE = 1024
TTL = 1  # Time-to-Live: limit scope
```

**Important**: Multicast addresses start at `224.0.0.0` (Class D). Never use addresses below!

### Receiver Implementation (receiver.py)

The receiver **joins a multicast group** before receiving:

```python
import socket
import struct
from config import MULTICAST_GROUP, PORT, BUFFER_SIZE

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

# Bind to the multicast port (not the group address!)
sock.bind(("", PORT))

# Join multicast group (this is the "subscribe" operation)
# struct.pack() converts IP address into binary form for kernel
mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

print(f"[RECEIVER] Joined {MULTICAST_GROUP}:{PORT}")

# Wait for multicast datagrams
while True:
    data, addr = sock.recvfrom(BUFFER_SIZE)
    print(f"[RECEIVER] {addr} -> {data.decode()}")
```

**Key Points**:
- **`bind(("", PORT))`**: Listen on the port, not the group address
- **`IP_ADD_MEMBERSHIP`**: Kernel filter to only receive group traffic
- **`struct.pack()`**: Converts IP address to binary form for kernel
- **`socket.INADDR_ANY`**: Join on all available interfaces

### Sender Implementation (sender.py)

The sender just sends to the group address (no join needed):

```python
import socket
from config import MULTICAST_GROUP, PORT, TTL

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

# Set TTL to limit scope (1 = stay on LAN, 255 = internet)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, TTL)

# Send to multicast group address
message = "MULTICAST: Hello subscribers"
sock.sendto(message.encode(), (MULTICAST_GROUP, PORT))

print("[SENDER] Multicast sent")
sock.close()
```

**Key Points**:
- **No join**: Sender doesn't need to join the group
- **`IP_MULTICAST_TTL`**: Control how far the message travels
- **TTL=1**: Stays on local LAN (prevents internet flooding)
- **TTL=255**: Can traverse routers (use carefully!)

## Unicast vs Broadcast vs Multicast

### Unicast (One-to-One)
```
Sender → Specific IP:port
         (direct path)

Receivers: 1
Scope: Entire internet (if routable)
```

### Broadcast (One-to-All)
```
Sender → 255.255.255.255
         (floods entire LAN)

Receivers: All nodes on LAN
Scope: Local LAN only (doesn't route)
```

### Multicast (One-to-Group)
```
Sender → 224.x.x.x (group address)
         (only group members receive)

Receivers: Explicit members only
Scope: LAN (TTL=1) to internet (TTL=255)
```

## Multicast Address Space (Class D)

```
224.0.0.0     – 224.0.0.255    [Reserved by IANA]
224.0.1.0     – 238.255.255.255 [Globally scoped]
239.0.0.0     – 239.255.255.255 [Administratively scoped (local use)]
```

**Pick an address** from `239.0.0.0` to `239.255.255.255` for learning/testing.

## Common Mistakes & Interpretations

| Mistake | Why It Happens | Solution |
|---------|---|---|
| **Receiver never gets data** | Forgot `IP_ADD_MEMBERSHIP` | Add group join before recv() |
| **Multicast address < 224.0.0.0** | Confusion with subnet broadcast | Use `224.1.1.1` or `239.x.x.x` |
| **Using `struct.pack()` wrong** | Unfamiliar with binary format | Use exact pattern: `"4sl"` for IP+address |
| **TTL too high** | Want local-only but set to 255 | Set TTL=1 for LAN scoping |
| **Expecting replies** | Multicast is still one-way | Use separate unicast channel for ACKs |

## Testing Scenarios

### Test 1: Single Receiver, Single Sender

Terminal 1:
```bash
python receiver.py
```

Terminal 2:
```bash
python sender.py
```

**Result**: Receiver prints the multicast message.

### Test 2: Multiple Receivers, Single Sender

Terminal 1:
```bash
python receiver.py
```

Terminal 2:
```bash
python receiver.py
```

Terminal 3:
```bash
python receiver.py
```

Terminal 4:
```bash
python sender.py
```

**Result**: All three receivers print the message (all members of the group).

### Test 3: Non-Member Doesn't Receive (Selectivity Proof)

Modify `receiver.py` to **NOT** join the group:

```python
# receiver_no_join.py - Remove the IP_ADD_MEMBERSHIP line
import socket
from config import MULTICAST_GROUP, PORT, BUFFER_SIZE

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", PORT))
# Deliberately skip: sock.setsockopt(...IP_ADD_MEMBERSHIP...)

print(f"[RECEIVER (NO JOIN)] Listening on port {PORT}")

while True:
    data, addr = sock.recvfrom(BUFFER_SIZE)
    print(f"[RECEIVER (NO JOIN)] {addr} -> {data.decode()}")
```

Run sender:
```bash
python sender.py
```

**Result**: Non-member receives nothing (because kernel filters it).

## Real-World Applications

| Protocol | Uses Multicast | Why |
|----------|---|---|
| **Video Streaming** | Yes | One source to thousands of subscribers |
| **IPTV** | Yes | TV channels as multicast groups |
| **Live Events** | Yes | One feed to all attendees |
| **Financial Data** | Yes | Market data to traders (real-time, no retransmission) |
| **Gaming** | Sometimes | Game state to all players in match |

## Extension Options

### Extension A: Periodic Multicast Stream

Sender sends updates every N seconds:

```python
# sender.py with periodic updates
import socket
import time
from config import MULTICAST_GROUP, PORT, TTL

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, TTL)

count = 0
while True:
    message = f"Update #{count} @ {time.strftime('%H:%M:%S')}"
    sock.sendto(message.encode(), (MULTICAST_GROUP, PORT))
    print(f"[SENDER] {message}")
    count += 1
    time.sleep(2)  # One message every 2 seconds
```

**Result**: Receivers see continuous stream.

### Extension B: Multiple Groups

Receiver joins multiple groups (channels):

```python
# receiver_multi_group.py
import socket
import struct
from config import PORT, BUFFER_SIZE

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", PORT))

# Join multiple groups
groups = ["224.1.1.1", "224.1.1.2", "224.1.1.3"]
for group in groups:
    mreq = struct.pack("4sl", socket.inet_aton(group), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    print(f"[RECEIVER] Joined {group}")

print("[RECEIVER] Subscribed to multiple channels")

while True:
    data, addr = sock.recvfrom(BUFFER_SIZE)
    print(f"[RECEIVER] From {addr}: {data.decode()}")
```

```python
# sender_group2.py - Send to group 2
import socket
from config import PORT, TTL

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, TTL)

message = "Message on 224.1.1.2"
sock.sendto(message.encode(), ("224.1.1.2", PORT))
print("[SENDER] Sent to 224.1.1.2")
```

**Result**: Receiver sees messages from both groups.

### Extension C: Dynamic Join/Leave

Subscribe and unsubscribe at runtime:

```python
# receiver_dynamic.py
import socket
import struct
import time
from config import PORT, BUFFER_SIZE

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", PORT))

group = "224.1.1.1"

# Join
mreq = struct.pack("4sl", socket.inet_aton(group), socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
print(f"[RECEIVER] Joined {group}")

# Receive for 10 seconds
for i in range(10):
    sock.settimeout(1)
    try:
        data, addr = sock.recvfrom(BUFFER_SIZE)
        print(f"[RECEIVER] {i}: {data.decode()}")
    except socket.timeout:
        pass

# Leave
sock.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)
print(f"[RECEIVER] Left {group}")

# Wait (won't receive anything now)
print("[RECEIVER] Waiting (not subscribed)...")
time.sleep(5)
```

**Result**: Messages only arrive while subscribed.

## Key Differences from Broadcast

| Feature | Broadcast | Multicast |
|---------|-----------|-----------|
| **Address Type** | `255.255.255.255` | `224.x.x.x` |
| **Requires Join** | No (automatic) | Yes (explicit) |
| **Scope Control** | LAN only | TTL controls scope |
| **Receiver Count** | All on LAN | Only members |
| **Scalability** | Floods network | Efficient routing |
| **Standard** | Ancient (before multicast) | Modern (post-1990s) |

## TTL (Time-to-Live) Scope

| TTL | Scope | Example |
|-----|-------|---------|
| 1 | Local network segment | VLAN, LAN |
| 2-31 | Local network | Campus, building |
| 32-63 | Organization | Company WAN |
| 64-127 | Region | Geographic region |
| 128-255 | Global | Internet-wide |

**Best practice for testing**: Use `TTL=1` to avoid accidental internet flooding.

## Debugging Checklist

- [ ] Multicast address in range `224.0.0.0`–`239.255.255.255`?
- [ ] Receiver joining before sender sends?
- [ ] Using `IP_ADD_MEMBERSHIP` correctly?
- [ ] `struct.pack()` pattern correct (`"4sl"`)?
- [ ] TTL set appropriately (usually 1)?
- [ ] Port matches between sender and receiver?
- [ ] No firewall blocking multicast?

## Key Takeaway

> Multicast is broadcast's smarter sibling. You shout, but only to people who raised their hand first.

It's efficient, scalable, and essential for modern streaming.

---

**Status**: ✅ Implemented. Ready for learning.  
**Last Updated**: 2025  
**Previous**: Week 3 – UDP Broadcast  
**Next**: Week 5 – Peer-to-Peer
