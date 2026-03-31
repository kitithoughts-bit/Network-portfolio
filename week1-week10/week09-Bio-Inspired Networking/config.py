# config.py — Week 9: Bio-Inspired Networking (Pheromone Routing)
# ============================================================
# Usage:
#   python node.py --port 10000 --peers 10001 10002
#   python node.py --port 10001 --peers 10000 10002
#   python node.py --port 10002 --peers 10000 10001
# ============================================================

HOST = "127.0.0.1"
BASE_PORT = 10000
PEER_PORTS = [10001, 10002]
BUFFER_SIZE = 4096

# ── Pheromone mechanics ────────────────────────────────────────────────────────
INITIAL_PHEROMONE = 1.0       # Starting pheromone for known peers
DECAY_FACTOR = 0.92           # Multiply pheromone by this each cycle (< 1.0)
REINFORCEMENT = 0.25          # How much pheromone is added on a successful send
FAILURE_PENALTY = 0.15        # How much is subtracted on a failed send
FORWARD_THRESHOLD = 0.2       # Minimum pheromone level to consider forwarding

# ── Timing ────────────────────────────────────────────────────────────────────
UPDATE_INTERVAL = 4           # Seconds between forward-loop cycles
PROBE_INTERVAL = 8            # Seconds between heartbeat probes

# ── Message lifecycle ─────────────────────────────────────────────────────────
MESSAGE_TTL = 90              # Drop message after this many seconds (0 = never)
MAX_ATTEMPTS = 6              # Drop message after this many tries  (0 = unlimited)

# ── Discovery ─────────────────────────────────────────────────────────────────
INITIAL_ENCOUNTER_PHEROMONE = 0.5  # Assigned to newly discovered peers
