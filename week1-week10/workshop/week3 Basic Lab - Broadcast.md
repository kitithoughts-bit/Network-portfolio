WEEK 3 – BASIC: Broadcast Communication (LAN-Level)

Teaching Intent (Instructor Note)
Week 3 teaches controlled shouting. Broadcast is powerful, lazy, and dangerous. Students must learn when it works, why it fails, and why modern networks try to avoid it.

Overview
This lab introduces UDP broadcast communication within a local network. One sender transmits a message to all nodes on the broadcast domain. Receivers choose whether to listen.
No connections. No targeting. Just presence.

Learning Outcome / Trait Assessment
Understand broadcast scope and limitations
Implement UDP broadcast sender and receiver
Distinguish broadcast from unicast and multicast
Traits trained: - Network scope awareness - Resource discipline - Protocol restraint

Key Concepts
UDP broadcast
Broadcast address (255.255.255.255 or subnet broadcast)
SO_BROADCAST socket option
One-to-many delivery

BASIC LAB — GitHub Scaffold (Student Starter Repo)
Repository Name
week03-udp-broadcast-basic
Directory Structure
week03-udp-broadcast-basic/
├── README.md
├── broadcaster.py
├── listener.py
├── config.py
└── docs/
    └── run_instructions.md

BASIC LAB — Step-by-Step Implementation
Step 0: Shared Configuration
# config.py
BROADCAST_IP = "255.255.255.255"
PORT = 7000
BUFFER_SIZE = 1024

Step 1: Create Broadcast Sender
# broadcaster.py
import socket
from config import BROADCAST_IP, PORT

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

message = "DISCOVERY: Who is online?"
sock.sendto(message.encode(), (BROADCAST_IP, PORT))

print("[BROADCASTER] Message sent")
sock.close()

Step 2: Create Broadcast Listener
# listener.py
import socket
from config import PORT, BUFFER_SIZE

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", PORT))  # Listen on all interfaces

print(f"[LISTENER] Listening for broadcast on port {PORT}")

while True:
    data, addr = sock.recvfrom(BUFFER_SIZE)
    print(f"[LISTENER] From {addr}: {data.decode()}")

Execution & Verification
Start one or more listeners on the same LAN
Run broadcaster on any node
All listeners receive the message

Expected Output
Multiple listeners print the same broadcast message simultaneously.

Common Mistakes (and Why They Matter)
Forgetting SO_BROADCAST → packet silently dropped
Expecting replies automatically → broadcast is one-way
Running across subnets → broadcast does not route

BASIC EXTENSION OPTIONS (Same Repo, New Branches)
Extension A: Broadcast Discovery + Reply
Listener sends unicast reply to sender
Sender collects responses
Extension B: Periodic Broadcast
Send discovery every N seconds
Observe network noise
Extension C: Subnet Broadcast Address
Replace 255.255.255.255 with subnet-specific broadcast

EXTRA LAB — ADVANCED: LAN Service Discovery Tool
Purpose
Turn raw broadcast into controlled discovery, the way real systems do.

Advanced Repository
week03-lan-service-discovery-advanced
Directory Structure
week03-lan-service-discovery-advanced/
├── README.md
├── discovery/
│   ├── announcer.py
│   └── responder.py
├── registry/
│   └── registry.py
├── config.py
└── utils/
    └── message.py

Advanced Requirements
Services announce availability via broadcast
Clients discover services dynamically
Registry maintains active service list
Time-based expiration of stale entries

Advanced Concepts Introduced
Service discovery protocols
Soft state and timeouts
Broadcast containment

Real-World Mapping
DHCP discovery
mDNS / Zeroconf (conceptual)
LAN device discovery tools

Instructor Truth
Broadcast is a blunt instrument. This lab teaches students when not to swing it.

EXTRA LAB: Network Service Discovery Tool
Students build a tool that discovers active nodes on a LAN.


