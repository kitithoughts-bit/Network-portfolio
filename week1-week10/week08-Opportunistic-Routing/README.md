# Week 8 – Opportunistic Routing

> **Core concept**: Forward packets based on *probability*, not certainty.  
> Nodes remember how reliably they've reached each peer and only forward when confidence is high enough.

---

## Files

```
week08-opportunistic-routing-basic/
├── config.py          ← All tunable parameters
├── delivery_table.py  ← Per-peer delivery probability tracker
├── message_queue.py   ← Thread-safe queue with TTL + attempt limit
├── node.py            ← Full node: server + forward loop + CLI
└── README.md
```

---

## Quick Start (3 terminals)

```bash
# Terminal 1
python node.py --port 9000 --peers 9001 9002

# Terminal 2
python node.py --port 9001 --peers 9000 9002

# Terminal 3
python node.py --port 9002 --peers 9000 9001
```

---

## Interactive Commands

Once a node is running, type commands and press Enter:

| Command | Description |
|---------|-------------|
| `send <port> <message>` | Queue a message for a specific peer |
| `flood <message>` | Epidemic: send to ALL reachable peers |
| `table` | Print delivery probability table |
| `queue` | Print pending message queue |
| `stats` | Print table + queue together |
| `decay` | Manually trigger probability decay |
| `quit` | Shutdown this node |

### Example session (Node 9000):
```
send 9001 hello from 9000
flood network-wide announcement
table
queue
```

---

## How It Works

### 1. Delivery Probability Table

Each node tracks a probability per peer:

```
:9001  [████████████░░░░░░░░] 0.60  encounters=3  last=2s ago
:9002  [████░░░░░░░░░░░░░░░░] 0.20  encounters=1  last=45s ago
```

- **Increases** on every successful message delivery → `record_encounter()`
- **Decreases** slightly on failed connection → `record_failure()`
- **Decays slowly** each `UPDATE_INTERVAL` even without failure → `apply_decay()`

### 2. Forwarding Decision

The `forward_loop` runs every `UPDATE_INTERVAL` seconds:

```
if delivery_prob(peer) >= FORWARD_THRESHOLD:
    → attempt delivery
else:
    ⋯ hold message, retry later
```

This is **opportunistic**: the message waits until a "good" moment (high probability peer is reachable).

### 3. Epidemic Mode (`flood`)

When `destination=None`, the message is forwarded to **all** candidates above threshold simultaneously. This is *epidemic routing* — maximises delivery chance at the cost of network traffic.

### 4. Probe Loop

Every `UPDATE_INTERVAL * 2` seconds, each node sends a tiny heartbeat (`__probe__`) to all known peers. This keeps the probability table fresh even when there are no user messages.

### 5. Message Lifecycle

Each message has:
- **TTL** (`MESSAGE_TTL` seconds) — drops if too old
- **Max attempts** (`MAX_ATTEMPTS`) — drops after N failures
- **Status**: queued → forwarded → delivered / dropped

---

## Key Parameters (`config.py`)

| Parameter | Default | Effect |
|-----------|---------|--------|
| `FORWARD_THRESHOLD` | `0.5` | Minimum probability to forward |
| `DECAY_FACTOR` | `0.98` | How fast probabilities decay |
| `UPDATE_INTERVAL` | `3` | Seconds between forward loop runs |
| `MESSAGE_TTL` | `60` | Message expiry in seconds (0 = never) |
| `MAX_ATTEMPTS` | `5` | Max retries before dropping (0 = unlimited) |
| `INITIAL_ENCOUNTER_PROB` | `0.3` | Starting probability for a new peer |
| `ENCOUNTER_INCREMENT` | `0.1` | Probability boost per successful delivery |

---

## Experiments to Try

### Experiment 1: Probability builds up
1. Start all 3 nodes
2. `send 9001 hello` from node 9000 several times
3. Watch `table` — probability for 9001 rises with each delivery

### Experiment 2: Below-threshold holding
1. In `config.py`, set `FORWARD_THRESHOLD = 0.9`
2. Restart nodes — messages will be held until many successful encounters build the probability up
3. Observe `⋯ holding msg:…` lines

### Experiment 3: Kill a peer
1. Start 3 nodes, exchange messages until probabilities are high
2. Kill node 9001 (`Ctrl+C`)
3. Send a message to 9001 from 9000 — watch it queue and retry
4. Restart node 9001 — message eventually delivers

### Experiment 4: Epidemic routing
1. `flood hello everyone` from any node
2. Message reaches all peers above threshold simultaneously

### Experiment 5: Decay
1. Build up high probability with some sends
2. Stop sending — probability slowly decays each cycle
3. `decay` command forces it immediately

---

## Extensions (Branches)

| Extension | Branch | Description |
|-----------|--------|-------------|
| A | `ext/dynamic-prob` | Probability updated from encounter *history* (EWMA) |
| B | `ext/message-ttl` | Already implemented — tweak `MESSAGE_TTL` in config |
| C | `ext/logging` | Write delivery stats to `log.csv` for analysis |

---

## Real-World Mapping

| System | How It Maps |
|--------|-------------|
| Intermittent connectivity (planes, trains) | Hold until better link available |
| Wildlife sensor networks | Sensors exchange data when animals meet |
| Disaster zone MANETs | Route around broken infrastructure opportunistically |
| Underwater acoustic networks | Very slow, probabilistic contact windows |

---

## Common Mistakes

| Mistake | Why It Matters |
|---------|----------------|
| Forwarding blindly (ignoring probability) | Wastes bandwidth, overwhelms weak links |
| Not queuing failed messages | Silently drops data — unacceptable in DTN |
| Not decaying probabilities | Stale high probs → forward to dead peers |
| Blocking I/O in forward loop | Node freezes; can't receive while forwarding |
| No message deduplication | Epidemic mode can deliver the same message twice |

---

## Connection to Course Arc

| Week | Concept | Relation to Week 8 |
|------|---------|-------------------|
| 6 – MANET | TTL-based flooding | Week 8 replaces random TTL with probability decision |
| 7 – Store-Forward | Message queue + retry | Week 8 inherits this; adds probability gate |
| **8 – Opportunistic** | **Probability-based forwarding** | **This week** |
| 9 – Bio-Inspired | Pheromone routing | Pheromones ≈ persistent probability with reinforcement |
