#Step 0: Shared Configuration
# config.py
HOST = "127.0.0.1"
BASE_PORT = 7000
BUFFER_SIZE = 1024
NEIGHBORS = [7001, 7002]  # Example peer ports
FORWARD_PROBABILITY = 0.5  # 50% chance to forward
TTL = 3  # Max hops for message
