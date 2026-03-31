Python Network Programming for Modern Networks
A weekly lab-based journey from classical sockets to future networks

Course Philosophy
Networks are not cables and boxes. They are agreements under uncertainty. Each week, you will build one agreement in Python—simple first, then fragile, then strange.
You already know IP addressing and routing. Now we program behavior.

WEEK 1 – BASIC: Client–Server Communication (TCP Unicast)
Overview
This lab introduces socket programming through the most fundamental network model: client–server communication. One side listens. One side asks. Nobody panics.
Learning Outcome / Trait Assessment
Understand TCP client–server architecture
Implement blocking socket communication
Relate TCP reliability to application behavior
Traits: Structured thinking, protocol discipline, debugging network state
Key Concepts
TCP sockets
Bind, listen, accept, connect
Request–response pattern
BASIC LAB (Step-by-Step)
Create a TCP server socket
Bind to a local port
Listen for incoming connections
Accept one client
Receive a message
Send a response
Close the connection
Students verify success using loopback (127.0.0.1).
Expected Output
Client sends text → Server responds with acknowledgment
Common Mistakes
Forgetting to listen()
Port already in use
Blocking forever on recv()
Future Extension
Add multiple clients (threading)
Add simple authentication
Transition to asyncio

EXTRA LAB: Mini Chat Server
Scenario: Build a helpdesk chat server where multiple clients can connect sequentially.
Real-world mapping: Call centers, ticketing systems

WEEK 2 – BASIC: UDP Communication (Connectionless Unicast)
Overview
This week removes the safety net. No connection. No guarantees. Just packets and hope.
Learning Outcome / Trait Assessment
Compare TCP vs UDP
Implement UDP sender/receiver
Observe packet loss behavior
Traits: Risk awareness, performance tradeoff analysis
BASIC LAB
Create UDP socket
Send datagram to receiver
Receive datagram
Print sender address
Discussion Point
Why DNS, VoIP, and games choose UDP.
Future Extension
Add sequence numbers
Implement reliability manually

EXTRA LAB: Sensor Data Stream
Scenario: Simulate IoT sensors streaming temperature data without retransmission.

WEEK 3 – BASIC: Broadcast Communication
Overview
Broadcast is shouting. Useful. Dangerous. Educational.
Learning Outcome
Understand LAN broadcast scope
Implement broadcast discovery
BASIC LAB
Enable broadcast socket option
Send discovery message
Receive broadcast on listener
Real-World Usage
DHCP
Service discovery
Future Extension
Add discovery timeout
Compare with multicast

EXTRA LAB: Network Service Discovery Tool
Students build a tool that discovers active nodes on a LAN.

WEEK 4 – BASIC: Multicast Communication
Overview
Multicast introduces group membership. You listen only if you care.
Learning Outcome
Join multicast groups
Differentiate multicast vs broadcast
BASIC LAB
Join multicast address
Send multicast message
Receive group data
Future Extension
Video streaming simulation
Pub/Sub model

EXTRA LAB: Classroom Announcement System
One sender, many listeners, opt-in only.

WEEK 5 – BASIC: Peer-to-Peer Networking
Overview
No server. Everyone pulls their own weight.
Learning Outcome
Build symmetric network roles
Handle dynamic ports
BASIC LAB
Node acts as server and client
Exchange peer messages
Future Extension
Peer discovery
NAT discussion

EXTRA LAB: File Sharing Prototype
Simulate BitTorrent-style peer exchange (no tracker yet).

WEEK 6 – BASIC: Ad-Hoc Networking (MANET Simulation)
Overview
Infrastructure disappears. Nodes improvise.
Learning Outcome
Simulate neighbor discovery
Forward packets probabilistically
BASIC LAB
Maintain neighbor table
Forward packets with TTL
Future Extension
AODV / OLSR concepts

EXTRA LAB: Disaster Response Mesh
Nodes form a temporary rescue network.

WEEK 7 – BASIC: Store-and-Forward Communication
Overview
When links fail, memory becomes the network.
Learning Outcome
Implement message queues
Retry logic
BASIC LAB
Detect link availability
Store messages
Forward later
Future Extension
Persistent storage

EXTRA LAB: Planetary Email System
Messages arrive minutes later. Students wait. Philosophically.

WEEK 8 – BASIC: Opportunistic Routing
Overview
Forward packets based on probability, not certainty.
Learning Outcome
Decision-based forwarding
Encounter-based routing
BASIC LAB
Maintain delivery probability
Forward when advantageous
Future Extension
Epidemic routing

EXTRA LAB: Wildlife Tracking Network
Mobile nodes exchange data when paths cross.

WEEK 9 – ADVANCED: Bio-Inspired Networking
Overview
Ants route better than we do. Deal with it.
Learning Outcome
Reinforcement routing
Adaptive path selection
BASIC LAB
Simulate pheromone-based routing tables.
EXTRA LAB
Self-healing network simulation.

WEEK 10 – ADVANCED: Quantum-Inspired Networking (Conceptual)
Overview
No quantum hardware. Still quantum thinking.
Learning Outcome
No-cloning constraint
State collapse modeling
BASIC LAB
One-time-read message tokens.
EXTRA LAB
Quantum-secure messenger simulation.

CAPSTONE OPTIONS
Disaster Mesh Network
Bio-routing Simulator
Delay-Tolerant Space Network

Final Note to Students
If your program never fails, it’s lying.

