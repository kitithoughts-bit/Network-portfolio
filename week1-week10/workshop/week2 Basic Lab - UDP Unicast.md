WEEK 2 – BASIC: UDP Communication (Connectionless Unicast)

Teaching Intent (Instructor Note)
Week 2 removes comfort. There is no handshake, no memory, no apology. Students must experience what it means when the network does not care.

Overview
This lab introduces UDP socket programming, contrasting sharply with Week 1’s TCP discipline. Messages may arrive late, out of order, or not at all—and that is not a bug.

Learning Outcome / Trait Assessment
Understand connectionless communication
Implement UDP sender and receiver
Compare reliability tradeoffs between TCP and UDP
Traits trained: - Risk awareness - Performance vs reliability reasoning - Defensive programming

Key Concepts
UDP sockets
sendto() / recvfrom()
No connection state
Application-layer responsibility

BASIC LAB — GitHub Scaffold (Student Starter Repo)
Repository Name
week02-udp-unicast-basic
Directory Structure
week02-udp-unicast-basic/
├── README.md
├── sender.py
├── receiver.py
├── config.py
└── docs/
    └── run_instructions.md

BASIC LAB — Step-by-Step Implementation
Step 0: Shared Configuration
# config.py
HOST = "127.0.0.1"
PORT = 6000
BUFFER_SIZE = 1024

Step 1: Create UDP Receiver
# receiver.py
import socket
from config import HOST, PORT, BUFFER_SIZE

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

print(f"[RECEIVER] Listening on {HOST}:{PORT}")

Step 2: Receive Datagram
while True:
    data, addr = sock.recvfrom(BUFFER_SIZE)
    print(f"[RECEIVER] From {addr}: {data.decode()}")

Step 3: Create UDP Sender
# sender.py
import socket
from config import HOST, PORT

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
message = "Hello via UDP"

sock.sendto(message.encode(), (HOST, PORT))
print("[SENDER] Message sent")

Execution & Verification
Terminal 1: python receiver.py
Terminal 2: python sender.py
Stop receiver with Ctrl+C
Run sender again (observe no error, no receiver)

Expected Output
Receiver prints incoming datagram if available. Sender never waits.

Common Mistakes (and Why They Matter)
Expecting recvfrom() to know the sender beforehand
Assuming delivery is guaranteed
Forgetting that UDP has no session

BASIC EXTENSION OPTIONS (Same Repo, New Branches)
Extension A: Sequence Numbers
Add incrementing IDs
Observe missing packets
Extension B: Manual ACK
Receiver sends ACK packet
Sender retries on timeout
Extension C: Rate Control
Send packets in a loop
Observe receiver saturation

EXTRA LAB — ADVANCED: UDP Sensor Streaming System
Purpose
Expose students to high-frequency, unreliable data flows where speed matters more than perfection.

Advanced Repository
week02-udp-sensor-stream-advanced
Directory Structure
week02-udp-sensor-stream-advanced/
├── README.md
├── sensor/
│   └── sensor_node.py
├── collector/
│   └── collector.py
├── utils/
│   └── packet.py
└── config.py

Advanced Requirements
Multiple sensor nodes
Periodic UDP transmissions
Collector logs received data
No retransmission

Advanced Concepts Introduced
Real-time data tradeoffs
Packet loss tolerance
Application-layer framing

Real-World Mapping
IoT telemetry
Online gaming state updates
VoIP media streams

Forward Application Hooks
This lab feeds into: - Week 3: Broadcast discovery - Week 4: Multicast groups - Week 6: Ad-hoc gossip routing

Instructor Truth
UDP teaches humility. If students complain, the lesson is working.

EXTRA LAB: Sensor Data Stream
Scenario: Simulate IoT sensors streaming temperature data without retransmission.


