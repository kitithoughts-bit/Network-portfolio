# Python Network Programming 2025

A weekly lab-based journey from classical sockets to future networks. Building one network agreement in Python every week—simple first, then fragile, then strange.

## Course Philosophy

Networks are not cables and boxes. **They are agreements under uncertainty.** You already know IP addressing and routing. Now we program behavior.

## Learning Path Overview

| Week | Topic | Type | Core Concepts |
|------|-------|------|---|
| 1 | Client–Server Communication (TCP Unicast) | BASIC | TCP sockets, bind, listen, accept, connect, request–response |
| 2 | UDP Communication (Connectionless Unicast) | BASIC | UDP sockets, datagrams, packet loss, no guarantees |
| 3 | Broadcast Communication | BASIC | LAN broadcast scope, discovery, service advertisement |
| 4 | Multicast Communication | BASIC | Group membership, multicast groups, selective delivery |
| 5 | Peer-to-Peer Networking | BASIC | Symmetric roles, dynamic ports, no central server |
| 6 | Ad-Hoc Networking (MANET Simulation) | BASIC | Neighbor discovery, routing, TTL, improvised networks |
| 7 | Store-and-Forward Communication | BASIC | Message queues, retry logic, persistent buffers |
| 8 | Opportunistic Routing | BASIC | Probability-based forwarding, encounter routing |
| 9 | Bio-Inspired Networking | ADVANCED | Pheromone routing, reinforcement learning, adaptive paths |
| 10 | Quantum-Inspired Networking | ADVANCED | No-cloning, one-time tokens, quantum-secure concepts |

## 📋 Kanban: Implementation Checklist

### ✅ Completed Implementations
- [x] Week 1: TCP Client–Server (server.py, server_threaded.py, client.py)
- [x] Week 2: UDP Unicast (sender.py, receiver.py)
- [x] Week 3: UDP Broadcast (broadcaster.py, listener.py)
- [x] Week 4: UDP Multicast (sender.py, receiver.py)
- [x] Week 5: Peer-to-Peer (peer.py)
- [x] Week 6: MANET Phase-1 (node.py with random port support)
- [x] Week 7: Store-and-Forward Phase-1 (node.py, message_queue.py)

### 🚧 In Progress / Planning
- [ ] Week 8: Opportunistic Routing implementation
- [ ] Week 9: Bio-Inspired Networking (pheromone routing)
- [ ] Week 10: Quantum-Inspired Networking (conceptual)

### 📦 Codebase Structure

```
networkprogramming2025/
├── week01-tcp-client-server-basic/
│   ├── server.py                 (TCP server)
│   ├── server_threaded.py        (Multi-threaded server)
│   ├── client.py                 (TCP client)
│   ├── config.py                 (Configuration)
│   ├── logger.py                 (Logging)
│   └── test_concurrent.py        (Unit tests)
├── week02-udp-unicast-basic/
│   ├── sender.py                 (UDP sender)
│   ├── receiver.py               (UDP receiver)
│   └── config.py
├── week03-udp-broadcast-basic/
│   ├── broadcaster.py            (Broadcast sender)
│   ├── listener.py               (Broadcast receiver)
│   └── config.py
├── week04-udp-multicast-basic/
│   ├── sender.py                 (Multicast sender)
│   ├── receiver.py               (Multicast receiver)
│   └── config.py
├── week05-peer-to-peer-basic/
│   ├── peer.py                   (P2P node)
│   └── config.py
├── week06-manet-basic/
│   ├── node.py                   (MANET node)
│   ├── config.py
│   └── phase-1-random-port/      (Random port variant)
│       ├── node.py
│       └── config.py
├── week07-store-forward-basic/
│   ├── node.py                   (Store-forward node)
│   ├── message_queue.py          (Queue implementation)
│   ├── config.py
│   └── phase-1-random-port/      (Random port variant)
│       ├── node.py
│       ├── message_queue.py
│       └── config.py
└── workshop/
    ├── Curriculum- Network Programming 2025.md
    └── [Lab guides and research notes]
```

## Key Learning Outcomes by Week

### WEEK 1 – TCP Unicast
- Understand TCP client–server architecture
- Implement blocking socket communication
- Relate TCP reliability to application behavior
- **Traits**: Structured thinking, protocol discipline

### WEEK 2 – UDP Unicast
- Compare TCP vs UDP trade-offs
- Implement connectionless communication
- Observe and handle packet loss behavior
- **Traits**: Risk awareness, performance analysis

### WEEK 3 – Broadcast
- Understand LAN broadcast scope
- Implement discovery mechanisms
- **Real-world usage**: DHCP, service discovery

### WEEK 4 – Multicast
- Join multicast groups
- Differentiate multicast vs broadcast
- Opt-in group communication
- **Real-world usage**: Video streaming, pub/sub

### WEEK 5 – Peer-to-Peer
- Build symmetric network roles
- Handle dynamic ports
- **Real-world usage**: File sharing, decentralized systems

### WEEK 6 – Ad-Hoc Networking (MANET)
- Simulate neighbor discovery
- Implement forwarding with TTL
- **Extension**: AODV/OLSR concepts

### WEEK 7 – Store-and-Forward
- Implement message queues
- Handle retry logic
- **Extension**: Persistent storage, delay-tolerant networks

### WEEK 8+ – Advanced Topics
- Opportunistic routing (probability-based)
- Bio-inspired networking (pheromone routing)
- Quantum-inspired concepts (one-time tokens, secure messaging)

## Getting Started

1. Navigate to any `week*` directory
2. Configure your environment in `config.py`
3. Run server/sender in one terminal
4. Run client/receiver in another terminal
5. Observe the network behavior

Example (Week 1):
```bash
python server.py
python client.py
```

## Philosophy Note

> If your program never fails, it's lying.

Networks are inherently uncertain. This curriculum teaches you to build programs that acknowledge failure, handle it, and communicate despite it.

---

**Current Status**: Weeks 1-7 implemented with all core functionality. Weeks 8-10 ready for implementation." 
