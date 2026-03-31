# config.py — Week 8: Opportunistic Routing
# ============================================================
# Each node gets its own BASE_PORT. Peers are the other ports.
# To run 3 nodes:
#   Terminal 1: python node.py --port 9000 --peers 9001 9002
#   Terminal 2: python node.py --port 9001 --peers 9000 9002
#   Terminal 3: python node.py --port 9002 --peers 9000 9001
# ============================================================

HOST = "127.0.0.1"
BASE_PORT = 9000                  # Override with --port argument
PEER_PORTS = [9001, 9002]         # Override with --peers argument
BUFFER_SIZE = 4096

# Forwarding decision
FORWARD_THRESHOLD = 0.5           # Forward only if prob >= this value

# Probability decay (applied each UPDATE_INTERVAL if no encounter)
DECAY_FACTOR = 0.98               # Probability decays slowly when no contact

# How often the forward loop runs (seconds)
UPDATE_INTERVAL = 3

# How long a message lives before being dropped (seconds, 0 = forever)
MESSAGE_TTL = 60

# Max delivery attempts per message before giving up (0 = unlimited)
MAX_ATTEMPTS = 5

# Initial probability assigned to a new peer on first encounter
INITIAL_ENCOUNTER_PROB = 0.3

# How much probability increases on each successful encounter
ENCOUNTER_INCREMENT = 0.1
