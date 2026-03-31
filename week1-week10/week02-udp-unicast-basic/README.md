# WEEK 2 – UDP Communication (Connectionless Unicast)

**Teaching Intent**: Week 2 removes comfort. There is no handshake, no memory, no apology. Students must experience what it means when the network does not care.

## Overview

This lab introduces **UDP socket programming**, contrasting sharply with Week 1's TCP discipline. Messages may arrive late, out of order, or not at all—and that is **not a bug**. It is a feature.

## Learning Outcomes

By completing this week, you will:
- ✅ Understand connectionless communication model
- ✅ Implement UDP sender and receiver
- ✅ Compare reliability tradeoffs between TCP and UDP
- ✅ Train traits: Risk awareness, performance vs reliability reasoning, defensive programming

## Key Concepts

| Concept | TCP | UDP |
|---------|-----|-----|
| **Connection** | Required (handshake) | Not required |
| **Reliability** | Guaranteed delivery | Best-effort only |
| **Ordering** | In-order delivery | No guarantee |
| **Speed** | Slower (verification) | Faster (fire-and-forget) |
| **Overhead** | Higher (handshake + ACKs) | Lower (stateless) |
| **Use Case** | File transfer, email, web | VoIP, gaming, DNS, streaming |

## Repository Structure

```
week02-udp-unicast-basic/
├── README.md                    (← you are here)
├── sender.py                    (UDP sender)
├── receiver.py                  (UDP receiver)
├── config.py                    (Shared configuration)
└── docs/
    └── run_instructions.md      (Detailed execution guide)
```

## Quick Start

### 1. Configure

Edit `config.py`:

```python
HOST = "127.0.0.1"  # loopback
PORT = 6000         # UDP port
BUFFER_SIZE = 1024  # max datagram size
```

### 2. Run Receiver (Terminal 1)

```bash
python receiver.py
```

Expected output:
```
[RECEIVER] Listening on 127.0.0.1:6000
[RECEIVER] From ('127.0.0.1', XXXXX): Hello via UDP
```

The receiver **waits** for datagrams. It is stateless—it does not care who sends them.

### 3. Run Sender (Terminal 2)

```bash
python sender.py
```

Expected output:
```
[SENDER] Message sent
```

The sender **fires** a message and immediately exits. UDP is "fire and forget."

## Implementation Deep Dive

### Shared Configuration (config.py)

```python
HOST = "127.0.0.1"
PORT = 6000
BUFFER_SIZE = 1024
```

### Receiver Implementation (receiver.py)

The receiver is stateless—it listens for datagrams from anyone:

```python
import socket
from config import HOST, PORT, BUFFER_SIZE

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind to local address:port (no listen() needed!)
sock.bind((HOST, PORT))
print(f"[RECEIVER] Listening on {HOST}:{PORT}")

# Wait for datagrams indefinitely
while True:
    # recvfrom() BLOCKS until a datagram arrives
    # Returns BOTH data and sender address
    data, addr = sock.recvfrom(BUFFER_SIZE)
    message = data.decode()
    print(f"[RECEIVER] From {addr}: {message}")
```

**Key Points**:
- `socket.SOCK_DGRAM`: UDP (datagram) sockets
- **No `listen()`**: UDP is connectionless
- **`recvfrom()`**: Returns datagram + sender address
- **No handshake**: Server immediately ready to receive

### Sender Implementation (sender.py)

The sender is even simpler—create socket, send, done:

```python
import socket
from config import HOST, PORT, BUFFER_SIZE

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Send message to receiver
message = "Hello via UDP"
sock.sendto(message.encode(), (HOST, PORT))
print("[SENDER] Message sent")

# Sender does not wait for reply (unreliable delivery)
sock.close()
```

**Key Points**:
- **No `connect()`**: Just send to destination
- **`sendto()`**: Specify destination address inline
- **No ACK**: Sender does not know if message arrived
- **Stateless**: Socket closes immediately after send

## UDP vs TCP: The Trade-off

### TCP (Week 1)
```
Client              Server
  |                   |
  |--- SYN ------------->|
  |<-- SYN-ACK ---------|
  |--- ACK ------------->|  <- 3-way handshake (overhead!)
  |
  |--- DATA ----------->|
  |<-- ACK -------------|  <- Every message acknowledged (slow)
  |
  |--- FIN ------------->|
  |<-- FIN-ACK ---------|  <- Clean close (reliable)
```

### UDP (Week 2)
```
Sender              Receiver
  |                   |
  |--- DATAGRAM ------>|  <- One packet, no setup
  |                   |  <- May lose it (risk!)
  |                   |  <- No reply needed
```

**Lesson**: Speed vs certainty. Choose based on your needs.

## Common Mistakes & Interpretations

| Mistake | Why It Happens | Solution |
|---------|---|---|
| **Message lost** | UDP is unreliable | This is OK! Design apps that tolerate loss |
| **"Why doesn't receiver know sender exists?"** | No connection state | UDP is stateless. Each datagram is independent |
| **Sender blocked forever** | Waiting for reply that never comes | UDP doesn't wait. Add timeout if you need it |
| **Datagrams arrive out of order** | Network routing varies | Application must handle reordering if needed |
| **Payload truncated at BUFFER_SIZE** | Datagrams can't be reassembled | Use fixed message size or length prefix |

## Testing Scenario

### Test 1: Single Send/Receive

Terminal 1:
```bash
python receiver.py
```

Terminal 2:
```bash
python sender.py
```

**Result**: Receiver prints the message.

### Test 2: Multiple Sends, Single Receiver

Terminal 1:
```bash
python receiver.py
```

Terminal 2:
```bash
python sender.py
python sender.py
python sender.py
```

**Result**: Receiver prints all three messages (or loses some!).

### Test 3: Sender Without Receiver (Unreliability Proof)

Terminal 1:
Do NOT start receiver.

Terminal 2:
```bash
python sender.py
```

**Result**: 
- Sender completes successfully (no error!)
- Receiver would see nothing (loss is silent)
- **This proves UDP is unreliable.**

## Extension Options

### Extension A: Sequence Numbers

Add message ID to detect loss:

```python
# receiver.py - track sequence numbers
received_ids = set()

while True:
    data, addr = sock.recvfrom(BUFFER_SIZE)
    msg_id, text = data.decode().split('|', 1)
    msg_id = int(msg_id)
    
    if msg_id in received_ids:
        print(f"[RECEIVER] Duplicate: {msg_id}")
    else:
        received_ids.add(msg_id)
        print(f"[RECEIVER] New: {msg_id} -> {text}")
```

```python
# sender.py - send sequence number
import socket
from config import HOST, PORT

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

for i in range(5):
    message = f"{i}|Message {i}"
    sock.sendto(message.encode(), (HOST, PORT))
    print(f"[SENDER] Sent: {i}")
```

**Result**: Detect missing sequences.

### Extension B: Manual ACK (Reliability Layer)

Receiver sends ACK; sender retries on timeout:

```python
# sender.py with retry
import socket
import time
from config import HOST, PORT

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(2)  # 2-second timeout

message = "Message requiring ACK"
max_retries = 3

for attempt in range(max_retries):
    sock.sendto(message.encode(), (HOST, PORT))
    print(f"[SENDER] Sent (attempt {attempt + 1})")
    
    try:
        ack, addr = sock.recvfrom(BUFFER_SIZE)
        if ack.decode() == "ACK":
            print("[SENDER] ACK received!")
            break
    except socket.timeout:
        print("[SENDER] No ACK, retrying...")
```

```python
# receiver.py with ACK
sock.bind((HOST, PORT))

while True:
    data, addr = sock.recvfrom(BUFFER_SIZE)
    print(f"[RECEIVER] Received: {data.decode()}")
    sock.sendto(b"ACK", addr)  # Send ACK back to sender
```

**Result**: You just built TCP-like reliability on top of UDP!

### Extension C: Rate Control

Send multiple messages and observe receiver saturation:

```python
# sender.py with rate control
import socket
import time
from config import HOST, PORT

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

for i in range(100):
    message = f"Fast message {i}"
    sock.sendto(message.encode(), (HOST, PORT))
    # No delay - send as fast as possible
    if (i + 1) % 10 == 0:
        print(f"[SENDER] Sent {i + 1} messages")
```

**Result**: Some messages are dropped at OS level.

## Real-World Applications

| Protocol | Uses UDP | Why |
|----------|----------|-----|
| **DNS** | Yes | One query, one reply. Loss OK. |
| **VoIP** | Yes | Speed > perfect delivery. Users tolerate gaps. |
| **Online Gaming** | Yes | 60 FPS updates > occasional stale state. |
| **Video Streaming** | Yes | Drop frames, not speed. |
| **DHCP** | Yes | Boot-time config. Broadcast to LAN. |

## Debugging Checklist

- [ ] Receiver running first?
- [ ] Host:port matches between sender and receiver?
- [ ] Using `SOCK_DGRAM` not `SOCK_STREAM`?
- [ ] Sender not waiting for reply (fire-and-forget)?
- [ ] No handshake errors in terminal?
- [ ] BUFFER_SIZE large enough for messages?

## Key Takeaway

> UDP is honest: it makes no promises. Write code that respects its nature.

TCP is a safety net. UDP is the open sky. Choose accordingly.

---

**Status**: ✅ Implemented. Ready for learning.  
**Last Updated**: 2025  
**Previous**: Week 1 – TCP Unicast  
**Next**: Week 3 – UDP Broadcast
