WEEK 4 – BASIC: Multicast Communication
Teaching Intent (Instructor Note)
This week is about selective listening. Multicast is neither shouting nor whispering. It is joining a channel and agreeing to hear only those who speak on it.
Students must internalize that multicast is about membership and scope, not guaranteed delivery.

Overview
This lab introduces UDP-based IP multicast. One sender transmits to a multicast group address. Only receivers that explicitly join that group will receive the data.
Multicast trades universality for scalability.

Learning Outcomes / Trait Assessment
Differentiate multicast from broadcast and unicast
Implement multicast sender and receiver in Python
Explain group membership and TTL scope
Traits trained: - Selective attention - Scalability reasoning - Protocol exactness

Key Concepts
Multicast address range (224.0.0.0 – 239.255.255.255)
Group membership (join / leave)
UDP multicast sockets
TTL-based scoping

BASIC LAB — Student Starter GitHub Repo
Repository Name
week04-udp-multicast-basic
Repository Structure
week04-udp-multicast-basic/
├── README.md
├── sender.py
├── receiver.py
├── config.py
└── docs/
    └── run_instructions.md

BASIC LAB — Step-by-Step
Step 0: Shared Configuration
# config.py
MULTICAST_GROUP = "224.1.1.1"
PORT = 8000
BUFFER_SIZE = 1024
TTL = 1  # restrict to local network

Step 1: Multicast Receiver (Join Group)
# receiver.py
import socket
import struct
from config import MULTICAST_GROUP, PORT, BUFFER_SIZE

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.bind(("", PORT))

mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

print(f"[RECEIVER] Joined {MULTICAST_GROUP}:{PORT}")

while True:
    data, addr = sock.recvfrom(BUFFER_SIZE)
    print(f"[RECEIVER] {addr} -> {data.decode()}")

Step 2: Multicast Sender
# sender.py
import socket
from config import MULTICAST_GROUP, PORT, TTL

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, TTL)

message = "MULTICAST: Hello subscribers"
sock.sendto(message.encode(), (MULTICAST_GROUP, PORT))

print("[SENDER] Multicast sent")
sock.close()

Execution & Verification
Start two or more receivers
Run sender once
Only receivers that joined the group print the message

Expected Behavior
Messages are delivered only to subscribed receivers. Non-members hear nothing.

Common Errors (and What They Teach)
Forgetting group membership → silence is correct
Using wrong multicast range → packets dropped
Misconfigured TTL → unintended scope expansion

BASIC EXTENSIONS (Same Repo, Branch-Based)
Extension 1: Periodic Multicast Stream
Send updates every N seconds
Observe stable group delivery
Extension 2: Multiple Groups / Channels
Subscribe to different multicast addresses
Demonstrate topic separation
Extension 3: Dynamic Join / Leave
Join and leave groups at runtime
Observe immediate delivery changes

EXTRA LAB — ADVANCED: Multicast Publish/Subscribe System
Advanced GitHub Repo
week04-multicast-pubsub-advanced
Repository Structure
week04-multicast-pubsub-advanced/
├── README.md
├── publisher.py
├── subscriber.py
├── topics.py
├── config.py
└── utils/
    └── protocol.py

Advanced Lab Goals
Topic-based multicast channels
Multiple publishers and subscribers
Application-layer topic mapping

Advanced Concepts Introduced
Publish/Subscribe communication
Group-based scaling
Event distribution semantics

Later Application Context (Conceptual)
IPTV and live streaming
Financial market data feeds
Multiplayer game state distribution
Distributed event and notification systems

Instructor Truth
Multicast works because not everyone is invited—and that is the point.


