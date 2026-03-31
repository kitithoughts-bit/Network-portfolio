# Step 1: Node Maintains a Neighbor Table
# node.py
import socket
import threading
import random
#from config import HOST, BASE_PORT, BUFFER_SIZE, NEIGHBORS, FORWARD_PROBABILITY, TTL

import sys
import importlib

def load_node_config():
    # Usage: python main.py 0  (This makes the node port 7000)
    try:
        node_idx = int(sys.argv[1])
        cfg = importlib.import_module("config")
        
        # Logic: Pick self, then exclude self from neighbors
        BASE_PORT = cfg.ALL_PORTS[node_idx]
        NEIGHBORS = [p for p in cfg.ALL_PORTS if p != BASE_PORT]
        
        return BASE_PORT, NEIGHBORS, cfg
    except (IndexError, ValueError):
        print("Error: Provide a node index (0, 1, or 2)")
        sys.exit(1)

BASE_PORT, NEIGHBORS, cfg = load_node_config()
print(f"Running on {BASE_PORT}, Neighbors: {NEIGHBORS}")



neighbor_table = set(NEIGHBORS)

def handle_incoming(conn, addr):
    data = conn.recv(cfg.BUFFER_SIZE).decode()
    msg, ttl = data.split('|')
    ttl = int(ttl)
    print(f"[NODE {BASE_PORT}] Received from {addr}: {msg} (TTL={ttl})")
    conn.close()
    
    # Forward probabilistically
    if ttl > 0 and random.random() < cfg.FORWARD_PROBABILITY:
        forward_message(msg, ttl - 1, exclude=addr[1])

def start_server(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((cfg.HOST, port))
    server.listen()
    print(f"[NODE {port}] Listening for neighbors...")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_incoming, args=(conn, addr)).start()
#________________________________________
# Step 2: Node Forwards Messages with TTL
def forward_message(message, ttl, exclude=None):
    for peer_port in neighbor_table:
        if peer_port == exclude:
            continue
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((cfg.HOST, peer_port))
            s.sendall(f"{message}|{ttl}".encode())
            s.close()
        except ConnectionRefusedError:
            print(f"[NODE {BASE_PORT}] Peer {peer_port} unreachable")
#________________________________________
#Step 3: Node Sends Initial Message
if __name__ == "__main__":
    threading.Thread(target=start_server, args=(BASE_PORT,), daemon=True).start()
    
    # Send a test message to neighbors
    test_message = f"Hello from node {BASE_PORT}"
    forward_message(test_message, cfg.TTL)
