# Week 10 – Quantum-Inspired Networking (Conceptual)

> **Core concept**: Messages exist until measured — and measuring destroys them.  
> Inspired by quantum mechanics: no-cloning, state collapse, entanglement.  
> Implemented entirely in classical Python — no quantum hardware required.

---

## Files

```
week10-quantum-network-basic/
├── config.py       ← Tunable parameters (expiry, hops, noise, …)
├── token.py        ← QuantumToken + EntangledPair + TokenRegistry
├── token_store.py  ← Thread-safe local vault
├── node.py         ← Full node: server + forward loop + CLI
└── README.md
```

---

## Quick Start (3 terminals)

```bash
# Terminal 1
python node.py --port 11000 --peers 11001 11002

# Terminal 2
python node.py --port 11001 --peers 11000 11002

# Terminal 3
python node.py --port 11002 --peers 11000 11001
```

---

## Interactive Commands

| Command | Description |
|---------|-------------|
| `send <port> <message>` | Send a one-time token to a specific peer |
| `entangle <port> <message>` | Create an entangled pair; send α, hold β |
| `flood <message>` | Send independent tokens to ALL peers |
| `read <token_id_prefix>` | Locally read (collapse) a held token |
| `tokens` | List all tokens currently held by this node |
| `stats` | Show token vault statistics |
| `quit` | Shutdown node |

---

## The Three Quantum Principles (Classically Simulated)

### 1. No-Cloning Theorem

> A quantum state cannot be copied without destroying the original.

**Classical simulation**: Each `QuantumToken` has a unique `token_id` tracked in a global `TokenRegistry`. When a token is forwarded, `hops` increments. The registry rejects any second `read()` attempt with the same `token_id` — even if a bug or a malicious peer sends a copy.

```
Token A (hops=0) → forward → Token A (hops=1) → forward → Token A (hops=2) READ here
                                                              ↳ token_id collapsed in registry
If anyone sends Token A again → registry rejects it
```

### 2. State Collapse (Wave-Function Collapse)

> Measuring a quantum state irreversibly collapses it.

**Classical simulation**: `token.read()` calls `registry.collapse(token_id)`. The first call returns the content and marks the ID as collapsed. Every subsequent call — by any node, any thread — returns `None`.

```python
token.read()   # → "hello world"    state = COLLAPSED
token.read()   # → None             already collapsed
```

### 3. Quantum Entanglement

> Two entangled particles share state. Measuring one instantly determines the other.

**Classical simulation**: `EntangledPair` creates two tokens (α and β) with the same `entanglement_id`. The `TokenRegistry` tracks them as a group. When α is read and collapses, the registry collapses β simultaneously — even if β is on a different node.

```
Node 11000 holds β
Node 11001 receives α, reads it → α collapses
                                → registry collapses β too
Node 11000: β.read() → None    (β is already collapsed)
```

This models the key property: **measuring one destroys the other**, preventing duplication.

---

## How the Node Works

### Token lifecycle

```
CREATE (send / entangle)
    ↓
TRANSIT (hop through nodes, hops counter increments)
    ↓
ARRIVE at destination node
    ↓
READ → content returned, token_id collapsed in registry
    ↓
Dead — all copies with same token_id are now invalid
```

### Forward loop (no-cloning enforcement)

The forward loop picks **one peer only** per token — never broadcasts the same token:

```python
peer = random.choice(active_peers)   # pick exactly one
forwarded = token.forward()          # hops+1, same token_id
try_send_token(peer, forwarded)      # send
store.mark_forwarded(token.token_id) # remove from local store
```

This is the classical equivalent of passing a physical object: the sender no longer has it.

### Channel noise (decoherence)

Set `CHANNEL_NOISE = 0.3` in `config.py` to simulate a 30% packet loss rate, analogous to photon loss in a noisy quantum channel. Tokens lost this way cannot be retransmitted — they are gone.

---

## Key Parameters (`config.py`)

| Parameter | Default | Effect |
|-----------|---------|--------|
| `TOKEN_EXPIRY` | `30` | Seconds until token self-destructs (0 = never) |
| `MAX_HOPS` | `3` | Max nodes a token travels before forced read |
| `SUPERPOSITION_COPIES` | `2` | Entangled pair size (concept reference) |
| `CHANNEL_NOISE` | `0.0` | Probability of silent packet drop (decoherence) |
| `UPDATE_INTERVAL` | `3` | Forward loop interval (seconds) |

---

## Experiments to Try

### Experiment 1: One-time-read
1. `send 11001 secret`
2. On node 11001 — token arrives and is auto-read at final hop
3. Try `send 11001 secret` again with a second copy
4. Notice: same token_id is rejected if forwarded again (no-cloning)

### Experiment 2: Entanglement collapse
1. On node 11000: `entangle 11001 twin message`
2. Watch α dispatched to 11001, β held locally
3. On 11001: β arrives and is read — collapses
4. On 11000: `read <β_id_prefix>` → returns None (already collapsed)
5. This demonstrates: reading α destroyed β, across nodes

### Experiment 3: Token expiry
1. Set `TOKEN_EXPIRY = 5` in config.py
2. Start nodes, create a token: `send 11001 perishable`
3. Kill node 11001 so the token can't be delivered immediately
4. Wait 6 seconds — try again: token is expired, dropped

### Experiment 4: Channel noise
1. Set `CHANNEL_NOISE = 0.5` in config.py (50% loss)
2. Send several tokens to a peer
3. Notice roughly half are lost in transit with ⚡ channel noise log
4. Unlike Week 7 store-and-forward, these are NOT retried — the token is gone

### Experiment 5: Hop limit
1. Set `MAX_HOPS = 2` in config.py
2. Start 3 nodes in a chain: 11000 → 11001 → 11002
3. Send from 11000 to 11001; 11001 forwards to 11002
4. 11002 receives at hops=2 (= MAX_HOPS - 1) and must READ, not forward

### Experiment 6: Flood (independent tokens)
1. `flood everyone can see this`
2. Notice each peer gets a DIFFERENT token_id
3. This is NOT a clone — each is an independent new token
4. Compare to Week 8 `flood`: same content, different identities

---

## Week 8 / 9 / 10 Comparison

| Aspect | Week 8 (Opportunistic) | Week 9 (Bio-Inspired) | Week 10 (Quantum) |
|--------|----------------------|----------------------|------------------|
| Core metric | Delivery probability | Pheromone trail | Token state |
| Routing | Wait for good link | Follow strongest trail | Hop-limited, one destination |
| Duplicate handling | Deduplication by msg_id | N/A | No-cloning by token_id |
| Failure model | Retry with backoff | Penalise trail | Token lost = gone |
| Analogy | Reliability statistics | Ant colony | Quantum measurement |
| Self-healing | Yes | Yes (emergent) | No — by design |

---

## Quantum Concepts vs Classical Simulation

| Quantum concept | What we simulate | What we DON'T simulate |
|-----------------|-----------------|------------------------|
| No-cloning theorem | `token_id` uniqueness in registry | Actual quantum state copying is physically impossible |
| Wave-function collapse | `read()` marks ID as consumed | Real superposition of values |
| Entanglement | Shared `entanglement_id` in registry | Instantaneous non-local correlation |
| Decoherence | `CHANNEL_NOISE` packet drop | Physical interaction with environment |
| Superposition | Concept only (config reference) | Actual superposition of 0 and 1 |
| Quantum key distribution (QKD) | One-time tokens + expiry | Photon polarisation, Bell inequality |

This is **not** quantum computing. It is **quantum-inspired design**: taking the principles and applying them to classical network architecture.

---

## Extensions (Branches)

| Extension | Branch | Description |
|-----------|--------|-------------|
| A | `ext/expiry-management` | Per-token configurable TTL; expired token cleanup log |
| B | `ext/multi-hop-tracking` | Track full hop history in token; detect routing loops |
| C | `ext/logging` | Log all token state transitions to CSV; visualise collapse events |

---

## Real-World Mapping

| System | Quantum-Inspired Element |
|--------|--------------------------|
| Quantum Key Distribution (BB84) | One-time photon states; eavesdrop = collapse detected |
| Signal / Disappearing messages | Token expiry + one-time read |
| One-time pads | No-cloning: key used once then destroyed |
| Hardware security tokens (TOTP) | Time-bounded, single-use codes |
| Post-quantum cryptography | Designing classical systems against quantum adversaries |

---

## Common Mistakes

| Mistake | Why It Matters |
|---------|---------------|
| Reusing token_id | Violates no-cloning — registry should catch this |
| Broadcasting the same token | Creates clones — use `flood` (new token per peer) not forward |
| Not checking expiry before read | Stale tokens should self-destruct, not deliver |
| Retrying failed token sends | Quantum analogy: lost photon is gone — don't retry |
| Ignoring entangled β after α sent | β must be checked/stored or the entanglement is untracked |

---

## Course Arc — Final Week

| Week | Core Pattern | What It Teaches |
|------|-------------|-----------------|
| 1–4 | TCP, UDP, Broadcast, Multicast | Classical delivery guarantees |
| 5–6 | P2P, MANET | Decentralisation and dynamic topology |
| 7 | Store-and-Forward | Tolerating disconnection |
| 8 | Opportunistic | Probabilistic delivery decisions |
| 9 | Bio-Inspired | Emergent, adaptive routing |
| **10** | **Quantum-Inspired** | **Security, ephemerality, state-awareness** |

> Networks are agreements under uncertainty.  
> Quantum networks are agreements that cannot even be observed without changing.
