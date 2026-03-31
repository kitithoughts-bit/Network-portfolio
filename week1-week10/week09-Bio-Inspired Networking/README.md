# Week 9 – Bio-Inspired Networking (Pheromone Routing)

> **Core concept**: Routes emerge from reinforcement, not configuration.  
> Successful paths get stronger trails. Failed paths fade. The network self-optimises — just like ants.

---

## Files

```
week09-bio-routing-basic/
├── config.py           ← All tunable parameters
├── pheromone_table.py  ← Per-peer pheromone trail tracker
├── message_queue.py    ← Thread-safe queue with TTL + attempt limit
├── node.py             ← Full node: server + forward loop + probe loop + CLI
└── README.md
```

---

## Quick Start (3 terminals)

```bash
# Terminal 1
python node.py --port 10000 --peers 10001 10002

# Terminal 2
python node.py --port 10001 --peers 10000 10002

# Terminal 3
python node.py --port 10002 --peers 10000 10001
```

---

## Interactive Commands

| Command | Description |
|---------|-------------|
| `send <port> <message>` | Queue a directed message |
| `flood <message>` | Epidemic: send to all reachable peers |
| `table` | Print pheromone trail table |
| `queue` | Print message queue |
| `stats` | Print table + queue |
| `reinforce <port> <amount>` | Manually strengthen a trail |
| `decay` | Manually trigger evaporation |
| `quit` | Shutdown node |

---

## The Ant Colony Analogy

| Ant behaviour | Network equivalent |
|---------------|-------------------|
| Scout ant finds food | Probe detects a reachable peer |
| Ant lays pheromone on return | `reinforce()` called after successful send |
| Pheromone evaporates over time | `decay()` applied every `UPDATE_INTERVAL` |
| Ant follows strongest trail | Forward to peer with highest pheromone |
| Trail to dead-end fades away | `penalise()` on failed sends → trail decays to 0 |
| New path emerges after blockage | Rediscovery and reinforcement of alternative peer |

---

## How It Works

### 1. Pheromone Table

Each node tracks a pheromone level per peer:

```
:10001  [████████████████████████] 1.450  ok=5 fail=0  last=3s  fwd=✓
:10002  [████████░░░░░░░░░░░░░░░░] 0.612  ok=2 fail=1  last=12s fwd=✓
        threshold=0.2  decay=0.92
```

### 2. Three forces on pheromone

```
Reinforce:  pher += REINFORCEMENT   (after successful send)
Penalise:   pher -= FAILURE_PENALTY (after failed send)
Decay:      pher *= DECAY_FACTOR    (every cycle, automatic evaporation)
```

At equilibrium: a peer you reach successfully every 4 seconds will stabilise at:

```
pher* ≈ REINFORCEMENT / (1 - DECAY_FACTOR)
      = 0.25 / (1 - 0.92)
      = 3.125
```

A peer you never reach decays toward 0.

### 3. Routing Decision

```
candidates = peers where pheromone >= FORWARD_THRESHOLD
→ pick the highest-pheromone candidate first
```

This is greedy best-first: follow the strongest trail.

### 4. Probe Loop

Every `PROBE_INTERVAL` seconds, scout heartbeats go to all known peers:
- Success → `reinforce()` (trail stays healthy)
- Failure → `penalise()` (trail weakens toward threshold)

When a probe-reinforced trail drops below threshold, that peer is effectively "off the routing table" until it recovers.

### 5. Message Lifecycle

```
enqueue → pending → [forward attempt] → delivered
                  ↘ attempts exhausted → dropped
                  ↘ TTL expired        → dropped
```

---

## Key Parameters (`config.py`)

| Parameter | Default | Effect |
|-----------|---------|--------|
| `INITIAL_PHEROMONE` | `1.0` | Starting trail strength for known peers |
| `DECAY_FACTOR` | `0.92` | Evaporation rate per cycle (lower = faster fade) |
| `REINFORCEMENT` | `0.25` | Trail strength gained per successful send |
| `FAILURE_PENALTY` | `0.15` | Trail strength lost per failed send |
| `FORWARD_THRESHOLD` | `0.2` | Minimum trail to route through a peer |
| `UPDATE_INTERVAL` | `4` | Seconds between forward loop cycles |
| `PROBE_INTERVAL` | `8` | Seconds between heartbeat probes |
| `MESSAGE_TTL` | `90` | Message expiry in seconds (0 = never) |
| `MAX_ATTEMPTS` | `6` | Max retries before dropping (0 = unlimited) |

---

## Experiments to Try

### Experiment 1: Trail reinforcement
1. Start 3 nodes
2. Send several messages to peer 10001: `send 10001 hello`
3. Run `table` — watch 10001's trail get stronger with each success

### Experiment 2: Trail decay
1. Build up a strong trail to 10001
2. Kill node 10001 (`Ctrl+C`)
3. Watch `table` over time — the trail fades as probes fail + decay applies
4. Once trail drops below threshold, directed messages are held

### Experiment 3: Self-healing
1. Let trails build to all peers
2. Kill node 10001
3. Wait for its trail to decay below threshold
4. Restart node 10001
5. Probes immediately reinforce the trail — routing resumes automatically

### Experiment 4: Compare to Week 8
- Week 8: probabilities are **normalised** [0, 1], decay is mild
- Week 9: pheromones are **unbounded** (accumulate with reinforcement), decay is stronger
- Run identical message patterns on both — notice how fast pheromone routing "locks in" a preferred path

### Experiment 5: Manual reinforcement
1. `reinforce 10002 5.0` — artificially boost 10002's trail
2. Watch the forward loop now strongly prefer 10002
3. Let natural decay bring it back to balance

### Experiment 6: Tune decay vs reinforcement
In `config.py`, try:
- `DECAY_FACTOR = 0.5` → trails evaporate very fast (aggressive forgetting)
- `DECAY_FACTOR = 0.99` → trails persist a long time (slow adaptation)
- `REINFORCEMENT = 1.0` → dominant paths emerge very quickly

---

## Week 8 vs Week 9 Comparison

| Aspect | Week 8 (Opportunistic) | Week 9 (Bio-Inspired) |
|--------|----------------------|--------------------|
| Metric | Delivery probability [0–1] | Pheromone strength [0–∞] |
| Reinforcement | `+ENCOUNTER_INCREMENT` | `+REINFORCEMENT` |
| Decay | `× DECAY_FACTOR` per cycle | `× DECAY_FACTOR` per cycle |
| Penalty | Small fixed penalty | `−FAILURE_PENALTY` |
| Routing | Forward if prob ≥ threshold | Follow strongest trail ≥ threshold |
| Analogy | Reliability statistics | Ant colony pheromone |
| Self-healing | Yes (via decay + encounter) | Yes (stronger — emergent) |

---

## Extensions (Branches)

| Extension | Branch | Description |
|-----------|--------|-------------|
| A | `ext/dynamic-learning` | Update pheromone using round-trip time (faster RTT = more pheromone) |
| B | `ext/multi-hop` | Store pheromone per destination (not just per direct neighbor) |
| C | `ext/visualization` | Log pheromone evolution to CSV; plot with matplotlib |

---

## Real-World Mapping

| System | Pheromone Analogy |
|--------|-----------------|
| Ant Colony Optimization (ACO) | Direct inspiration — used in combinatorial optimisation |
| OSPF / BGP routing | Prefer lower-cost paths (pheromone ≈ inverse of cost) |
| AntNet (1998) | Real network routing protocol based on ant behaviour |
| Swarm robotics | Robots reinforce explored paths back to base |
| Sensor networks | Nodes reinforce paths to sink nodes that respond |

---

## Common Mistakes

| Mistake | Why It Matters |
|---------|---------------|
| No decay | Old paths dominate forever; network can't adapt |
| No penalty on failure | Broken links keep attracting traffic |
| Blocking I/O in forward loop | Node freezes; misses reinforcement signals |
| Pheromone grows unbounded | Lower `DECAY_FACTOR` or cap the maximum |
| Threshold too high | No paths qualify; all messages queue forever |
| Threshold too low | Every peer forwards — epidemic on every message |

---

## Connection to Course Arc

| Week | Concept | Relation to Week 9 |
|------|---------|-------------------|
| 6 – MANET | TTL flooding, random forwarding | Week 9 replaces randomness with reinforcement |
| 7 – Store-Forward | Queue + retry | Week 9 inherits this pattern |
| 8 – Opportunistic | Probability-based forwarding | Week 9 is the biologically-motivated extension: probabilities → pheromone trails |
| **9 – Bio-Inspired** | **Pheromone routing** | **This week** |
| 10 – Quantum | State collapse, one-time tokens | Conceptual leap beyond classical adaptive routing |
