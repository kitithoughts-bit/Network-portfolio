# config.py — Week 10: Quantum-Inspired Networking
# ============================================================
# Usage:
#   python node.py --port 11000 --peers 11001 11002
#   python node.py --port 11001 --peers 11000 11002
#   python node.py --port 11002 --peers 11000 11001
# ============================================================

HOST = "127.0.0.1"
BASE_PORT = 11000
PEER_PORTS = [11001, 11002]
BUFFER_SIZE = 4096

# ── Token lifecycle ────────────────────────────────────────────────────────────
TOKEN_EXPIRY = 30             # Seconds until an unread token self-destructs
MAX_HOPS = 3                  # Max nodes a token may travel through (no-cloning)

# ── Superposition / redundancy ─────────────────────────────────────────────────
# When a token is created in "superposition" mode it is split into N entangled
# copies.  The first copy that is READ causes all others to collapse (become
# invalid).  This is conceptual — real quantum entanglement works differently.
SUPERPOSITION_COPIES = 2      # How many entangled copies to create

# ── Probabilistic delivery ─────────────────────────────────────────────────────
# Simulates a noisy quantum channel: each send attempt succeeds with this prob.
CHANNEL_NOISE = 0.0           # 0.0 = perfect channel; 0.3 = 30% packet loss

# ── Timing ────────────────────────────────────────────────────────────────────
UPDATE_INTERVAL = 3           # Forward-loop interval (seconds)
PROBE_INTERVAL  = 6           # Peer-probe interval  (seconds)
