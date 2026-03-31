# Python Network Programming 2025 – Course Syllabus

**Course Code**: NETPROG-2025  
**Instructor**: Network Programming Team  
**Semester**: 2025 (10 weeks)  
**Location**: Lab-based (distributed)  
**Prerequisite**: Basic Python programming, understanding of IP/routing concepts

---

## Course Description

An intensive, lab-based course in **socket programming and network behavior**. Students build one fundamental network pattern each week, progressing from classical TCP client-server to futures like quantum-inspired communication.

This is not a networking theory course. This is a **programming course** where the subject is networks.

### Core Philosophy

> **Networks are not cables and boxes. They are agreements under uncertainty.**

Each week, students implement one agreement—simple first, fragile second, strange third. By the end, you will have built a complete spectrum of network behaviors: reliable, unreliable, direct, broadcast, peer, ad-hoc, store-and-forward, opportunistic, bio-inspired, and quantum-friendly.

---

## Learning Objectives

By the end of this course, students will be able to:

### Core Competencies
- ✅ Write socket programs in Python (TCP, UDP, multicast, broadcast)
- ✅ Debug network problems using packet inspection and log analysis
- ✅ Design systems that tolerate network failure
- ✅ Distinguish between reliability, latency, and throughput tradeoffs
- ✅ Recognize when each network pattern applies in real systems

### Trait Development
- 🧠 **Structured thinking**: Protocol discipline, sequential reasoning
- 🔍 **Systems thinking**: Emergent behavior in peer/ad-hoc networks
- 📊 **Probabilistic reasoning**: Handling uncertainty in routing
- 🛠️ **Defensive programming**: Assuming networks fail, then succeeding anyway
- 🧬 **Adaptive thinking**: Mobile nodes, dynamic topology, bio-inspired behavior

---

## Course Structure

### Format
- **10 weeks** of intensive lab work
- **One core concept per week** (TCP → UDP → Broadcast → Multicast → P2P → MANET → Store-Forward → Opportunistic → Bio-Inspired → Quantum)
- **Hands-on Python implementation**
- **Real-world application mappings**
- **Extensions and capstone projects**

### Time Commitment
- **Lab time**: 6-8 hours per week
- **Reading**: 1-2 hours per week (workshop guides + code review)
- **Capstone project**: 2-3 weeks (overlaps final weeks)

---

## Weekly Breakdown

### WEEK 1: TCP Client–Server Communication (Unicast)

**Core Concept**: Reliable, ordered, connection-based communication  
**Pattern**: Request–response  
**Key Socket Operations**: `bind()`, `listen()`, `accept()`, `connect()`

**Learning Outcomes**:
- Implement blocking socket communication
- Understand TCP's 3-way handshake (transparent)
- Relate TCP reliability to application behavior

**Lab Deliverables**:
- `server.py`: Single-threaded echo server
- `client.py`: Client connecting and exchanging messages
- **Extension**: Multi-threaded server (handle multiple clients)
- **Extra Lab**: Mini chat server with state management

**Real-World Mapping**: HTTP servers, database clients, file transfer (FTP), email backends

**Files**: [week01-tcp-client-server-basic/](../week01-tcp-client-server-basic/)

---

### WEEK 2: UDP Communication (Connectionless Unicast)

**Core Concept**: Fire-and-forget, stateless, best-effort delivery  
**Pattern**: Datagram  
**Key Socket Operations**: `sendto()`, `recvfrom()`

**Learning Outcomes**:
- Compare TCP vs UDP tradeoffs
- Observe packet loss behavior (intentionally)
- Implement loss-tolerant application logic

**Lab Deliverables**:
- `sender.py`: Send UDP datagrams
- `receiver.py`: Listen for datagrams, no state
- **Extension**: Manual sequence numbers to detect loss
- **Extension**: Build reliability (ACK/retry) on top of UDP
- **Extra Lab**: Sensor data streaming (IoT simulator)

**Real-World Mapping**: DNS, VoIP, online gaming state, video streaming, NTP

**Files**: [week02-udp-unicast-basic/](../week02-udp-unicast-basic/)

---

### WEEK 3: Broadcast Communication (LAN-Level One-to-All)

**Core Concept**: Shouting to all nodes on local network  
**Pattern**: Flooding / Discovery  
**Key Socket Operations**: `SO_BROADCAST`, `sendto(255.255.255.255)`

**Learning Outcomes**:
- Understand broadcast scope (LAN-local only)
- Implement discovery mechanisms
- Distinguish broadcast from unicast/multicast

**Lab Deliverables**:
- `broadcaster.py`: Flood discovery message
- `listener.py`: Receive broadcasts (multiple instances)
- **Extension**: Broadcast discovery + unicast reply collection
- **Extension**: Periodic broadcast discovery
- **Extension**: Subnet-scoped broadcast
- **Extra Lab**: LAN service discovery tool

**Real-World Mapping**: DHCP discovery, ARP ("Who has this IP?"), device discovery, Bonjour

**Files**: [week03-udp-broadcast-basic/](../week03-udp-broadcast-basic/)

---

### WEEK 4: Multicast Communication (Group One-to-Many)

**Core Concept**: Selective listening via group membership  
**Pattern**: Pub/Sub / Opt-in group  
**Key Socket Operations**: `IP_ADD_MEMBERSHIP`, `IP_MULTICAST_TTL`

**Learning Outcomes**:
- Join/leave multicast groups dynamically
- Control scope with TTL
- Explain why multicast scales better than broadcast

**Lab Deliverables**:
- `sender.py`: Send to multicast group address
- `receiver.py`: Join group and receive
- **Extension**: Periodic multicast stream
- **Extension**: Multiple group membership
- **Extension**: Dynamic join/leave at runtime
- **Extra Lab**: Publish/Subscribe system with multiple topics

**Real-World Mapping**: IPTV, live event streaming, financial data feeds, game state distribution

**Files**: [week04-udp-multicast-basic/](../week04-udp-multicast-basic/)

---

### WEEK 5: Peer-to-Peer Networking (Decentralized)

**Core Concept**: No server; every node listens AND sends  
**Pattern**: Symmetric roles, bidirectional  
**Key Concepts**: Threading, concurrent listen/send

**Learning Outcomes**:
- Build nodes that are simultaneously clients and servers
- Handle multiple outbound connections
- Understand decentralized architecture

**Lab Deliverables**:
- `peer.py`: Single node with listener thread + sender
- Multiple instances interact bidirectionally
- **Extension**: Peer list management / broadcast to many
- **Extension**: Message relay (multi-hop)
- **Extension**: Graceful discovery and shutdown
- **Extra Lab**: Decentralized chat overlay

**Real-World Mapping**: BitTorrent, IPFS, Ethereum, Skype overlay, Discord voice peers

**Files**: [week05-peer-to-peer-basic/](../week05-peer-to-peer-basic/)

---

### WEEK 6: Ad-Hoc Networking (MANET Simulation)

**Core Concept**: Dynamic topology, probabilistic forwarding  
**Pattern**: Hop-limited flooding, TTL-based scoping  
**Key Concepts**: Neighbor tables, TTL decrement, probability checks

**Learning Outcomes**:
- Simulate mobile node discovery
- Implement probabilistic forwarding (not guaranteed delivery)
- Prevent infinite loops with TTL

**Lab Deliverables**:
- `node.py`: Node listens, forwards with TTL and probability
- Simulate 3-5 nodes in mesh
- **Extension**: Dynamic neighbor discovery (port scanning)
- **Extension**: Mobility simulation (neighbors change over time)
- **Extension**: Delivery metrics and routing analysis
- **Extra Lab**: Disaster response mesh network

**Real-World Mapping**: Search and rescue radios, military networks, UAV swarms, emergency services

**Files**: [week06-manet-basic/](../week06-manet-basic/)

---

### WEEK 7: Store-and-Forward Communication (Delay-Tolerant)

**Core Concept**: Buffer messages when links fail; deliver when online  
**Pattern**: Message queue + retry loop  
**Key Concepts**: Persistent state, link availability detection, backoff

**Learning Outcomes**:
- Implement message queues
- Detect link failures gracefully
- Retry with backoff (don't flood)

**Lab Deliverables**:
- `node.py`: Maintain queue, retry loop in background
- `message_queue.py`: FIFO queue with metadata
- **Extension**: Persistent storage (survive crash)
- **Extension**: Exponential backoff
- **Extension**: Prioritized queues
- **Extension**: Message TTL and max attempts
- **Extra Lab**: Planetary email system (high-latency network)

**Real-World Mapping**: SMTP email, Mars rover networks, mobile messaging (offline queue), IoT gateways

**Files**: [week07-store-forward-basic/](../week07-store-forward-basic/)

---

### WEEK 8: Opportunistic Routing (Probability-Based)

**Core Concept**: Forward based on delivery probability, not guaranteed paths  
**Pattern**: Epidemic / random walk  
**Key Concepts**: Encounter metrics, probability thresholds

**Learning Outcomes**:
- Implement decision-based forwarding
- Track delivery probabilities per neighbor
- Understand epidemic routing

**Lab Deliverables** (to be implemented):
- Probability-aware routing table
- Forward when confidence > threshold
- Mobile node encounter simulation
- **Extension**: Epidemic routing (broadcast to neighbors)
- **Extra Lab**: Wildlife tracking network

**Real-World Mapping**: Intermittent connectivity (planes), wildlife tracking, underwater comms

---

### WEEK 9: Bio-Inspired Networking (Reinforcement Routing)

**Core Concept**: Adaptive routing learned from network behavior (like ants following pheromones)  
**Pattern**: Stigmergy / pheromone-based routing  
**Key Concepts**: Pheromone tables, decay, reinforcement

**Learning Outcomes**:
- Simulate pheromone-based routing
- Implement adaptive path selection
- Understand reinforcement learning in networks

**Lab Deliverables** (to be implemented):
- Pheromone table per destination
- Forward along highest-pheromone paths
- Decay old pheromone traces
- **Extension**: Multi-hop pheromone propagation
- **Extra Lab**: Self-healing network simulation

**Real-World Mapping**: Ant colony algorithms, swarm robotics, biological network models

---

### WEEK 10: Quantum-Inspired Networking (Conceptual)

**Core Concept**: Network design principles inspired by quantum mechanics  
**Pattern**: No-cloning, superposition, entanglement (analog)  
**Key Concepts**: State collapse, one-time tokens, secure primitives

**Learning Outcomes**:
- Implement quantum-inspired primitives (conceptual, no real quantum)
- Design secure tokens using state collapse analogy
- Understand quantum-secure messaging patterns

**Lab Deliverables** (to be implemented):
- One-time-read message tokens
- Superposition-inspired redundancy
- **Extension**: Quantum-secure messenger
- **Extra Lab**: Quantum key distribution analog

**Real-World Mapping**: Future quantum internet, quantum-safe cryptography, post-quantum algorithms

---

## Capstone Projects

Students choose ONE of the following (or propose own with instructor approval):

### Capstone 1: Disaster Response Mesh Network
**Build**: A resilient ad-hoc mesh overlaying MANET + store-forward concepts  
**Scenario**: Communication in disaster zone (no infrastructure)  
**Components**:
- Dynamic neighbor discovery
- Probabilistic forwarding (Week 6)
- Store-and-forward for lost links (Week 7)
- Metrics: delivery rate, latency, hop count

**Deliverables**:
- `mesh_node.py`: Combined MANET + store-forward
- Analysis showing network resilience
- Paper: Design decisions and tradeoffs

### Capstone 2: Bio-Routing Simulator
**Build**: Pheromone-based routing with reinforcement learning  
**Scenario**: Network learns to route around failures  
**Components**:
- Pheromone table management
- Decay mechanism
- Comparison: Ants vs AODV vs random routing
- Visualization of pheromone trails

**Deliverables**:
- `bio_router.py`: Pheromone implementation
- Routing metrics and convergence analysis
- Visualization tool
- Paper: Comparing bio-inspired to classical routing

### Capstone 3: Delay-Tolerant Space Network
**Build**: Store-and-forward network simulating interplanetary communication  
**Scenario**: Mars rover communication with 5-20+ minute latency  
**Components**:
- Message queuing with priority
- Exponential backoff
- Persistent storage (disk)
- Simulated long propagation delays

**Deliverables**:
- `space_node.py`: Store-and-forward with long delays
- Traffic simulation (busy/quiet periods)
- Paper: Interplanetary communication challenges

---

## Assessment & Grading

### Weekly Labs (60%)
- **Completion**: Code runs without errors (30%)
- **Correctness**: Produces expected output, handles edge cases (20%)
- **Documentation**: README, code comments, testing evidence (10%)

### Extensions (20%)
- Completing 2-3 extensions per week (not required; replaces missing basic lab)
- More advanced than basic lab; added complexity or features

### Capstone Project (20%)
- **Implementation**: 12 pts (code works, meets requirements)
- **Analysis**: 5 pts (metrics, comparison, lessons learned)
- **Documentation**: 3 pts (design decisions, testing, paper/presentation)

### Overall Grading Scale
- 90-100: A (Excellent)
- 80-89: B (Good)
- 70-79: C (Satisfactory)
- 60-69: D (Passing)
- <60: F (Incomplete)

---

## Course Policies

### Attendance & Participation
- Labs are **hands-on**; attendance expected
- Office hours available for debugging help
- Async work acceptable if you document progress

### Late Work
- Labs due by **Sunday 11:59 PM** each week
- 10% deduction per day late (up to 3 days)
- After 3 days: 0 credit

### Academic Integrity
- Write your own code
- Cite external resources (StackOverflow, docs, tutorials)
- Group discussion OK; individual implementation required
- Cheating = F in course + referral

### Code of Conduct
- Respect peer debugging sessions
- Ask for help when stuck (don't suffer silently)
- Help others without giving answers

---

## Required Materials

### Software (All Free/Open-Source)
- **Python 3.8+**: https://www.python.org/downloads/
- **VS Code / PyCharm**: IDE of choice
- **Git**: Version control
- **Wireshark** (optional): Packet analysis

### Hardware
- **Machine with network stack**: Laptop/desktop
- **Multiple terminals**: For multi-node simulations

### Textbooks (Optional)
- *Unix Network Programming* by Stevens & Rago (definitive reference)
- *Computer Networking* by Kurose & Ross (theory supplement)
- Python socket module docs: https://docs.python.org/3/library/socket.html

---

## Course Schedule

| Week | Topic | Lab Focus | Capstone Prep |
|------|-------|-----------|---|
| 1 | TCP Unicast | Client-server | Understand threading |
| 2 | UDP Unicast | Unreliability | Loss tolerance |
| 3 | Broadcast | Discovery | Scope limitations |
| 4 | Multicast | Group membership | Scalability |
| 5 | Peer-to-Peer | Symmetric roles | Decentralization |
| 6 | MANET | Dynamic topology | Choose capstone |
| 7 | Store-Forward | Message queues | **Capstone begins** |
| 8 | Opportunistic | Probability routing | Capstone dev |
| 9 | Bio-Inspired | Pheromone routing | Capstone dev |
| 10 | Quantum | State collapse | **Capstone due** |

---

## Resources

### Official Documentation
- **Python `socket` module**: https://docs.python.org/3/library/socket.html
- **Python `threading`**: https://docs.python.org/3/library/threading.html
- **Python `struct` (binary packing)**: https://docs.python.org/3/library/struct.html

### Learning Resources
- **RealPython socket tutorial**: https://realpython.com/python-sockets/
- **Beej's Guide to Network Programming**: https://beej.us/guide/bgnet/
- **RFC 5952** (IPv6 text representation)
- **RFC 3986** (URI generic syntax)

### Tools
- **Wireshark**: Packet visualization
- **tcpdump**: Command-line packet capture
- **netstat**: View active connections
- **ping/traceroute**: Basic diagnostics

### Course Repository
All lab starters and solutions available at GitHub:
```
d:\buck\networkprogramming2025\
├── week01-tcp-client-server-basic/
├── week02-udp-unicast-basic/
├── week03-udp-broadcast-basic/
...
└── workshop/
    ├── README.md (← you are here)
    └── [Lab guides & research notes]
```

---

## Getting Help

### Debugging Resources
1. **Read the error message carefully** (90% of issues are in the output)
2. **Check preconditions**: Port in use? Peer running? Firewall?
3. **Add print statements** to trace execution
4. **Use Wireshark** to see actual packets
5. **Ask instructor/peers** after 15 minutes of independent effort

### Common Issues & Solutions

| Problem | Likely Cause | Fix |
|---------|---|---|
| "Address already in use" | Previous server didn't close | `SO_REUSEADDR` or wait 60s |
| "Connection refused" | Target peer not running | Start both/all endpoints |
| "recv() blocks forever" | Peer sent nothing or disconnected | Add timeout; check peer state |
| "Encoding error" | String ↔ bytes mismatch | `.encode()` / `.decode()` |
| "Socket timeout" | Network slow or unreachable | Increase timeout; check connectivity |

### Contact
- **Instructor**: [Office hours by appointment]
- **Course Discord**: [Link]
- **GitHub Issues**: [lab repos] (for confirmed bugs)

---

## Course Philosophy (Expanded)

> **If your program never fails, it's lying.**

Networks are inherently uncertain:
- **Links fail** (bits flip, packets drop, routers crash)
- **Hosts disappear** (mobility, power loss, deployment end)
- **Timing is weird** (variable latency, reordering, retransmission)

Classical education teaches reliability. This course teaches **resilience**:
- Acknowledge failure
- Communicate despite it
- Recover gracefully

By week 7, you've built:
1. ✅ Guaranteed delivery (TCP)
2. ✅ Loss tolerance (UDP)
3. ✅ One-to-many delivery (broadcast/multicast)
4. ✅ Decentralized communication (P2P)
5. ✅ Dynamic routing (MANET)
6. ✅ Delayed delivery (store-and-forward)

Weeks 8-10 teach the future:
7. 🔮 Smart routing (opportunistic)
8. 🧬 Biological intelligence (bio-inspired)
9. ⚛️ Quantum principles (quantum-inspired)

---

## Final Words

You are not learning *networking theory*. You are learning to **program networks**.

Each week, you build something that works. Each week, it gets stranger. By the end, you will have hands-on experience with concepts researchers are still inventing.

Don't rush past any week. If you skip the fundamentals, later weeks won't make sense. **Network programming is cumulative.**

And remember: The network is not against you. It's just indifferent. Program accordingly.

---

**Last Updated**: 2025  
**Course Status**: Active  
**Difficulty**: Intermediate (Python req'd; networking optional)  
**Time**: 10 weeks, 6-8 hrs/week

Good luck. May your packets arrive.
