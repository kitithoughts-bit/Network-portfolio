#  Step 2: Node Detects Link Availability and Stores Messages
# node.py
import socket
import threading
import time
#from config import HOST, BASE_PORT, PEER_PORTS, BUFFER_SIZE, RETRY_INTERVAL
from message_queue import MessageQueue

import sys
import importlib

def load_node_config():
    # Usage: python main.py 0  (This makes the node port 7000)
    try:
        node_idx = int(sys.argv[1])
        cfg = importlib.import_module("config")
        
        # Logic: Pick self, then exclude self from PEER_PORTS
        BASE_PORT = cfg.ALL_PORTS[node_idx]
        PEER_PORTS = [p for p in cfg.ALL_PORTS if p != BASE_PORT]
        
        return BASE_PORT, PEER_PORTS, cfg
    except (IndexError, ValueError):
        print("Error: Provide a node index (0, 1, or 2)")
        sys.exit(1)

BASE_PORT, PEER_PORTS, cfg = load_node_config()
print(f"Running on {BASE_PORT}, PEER_PORTS: {PEER_PORTS}")

queue = MessageQueue()

def send_message(peer_port, message):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((cfg.HOST, peer_port))
        s.sendall(message.encode())
        s.close()
        return True
    except (ConnectionRefusedError, socket.timeout):
        return False

def forward_loop():
    while True:
        for msg in queue.get_messages():
            success = send_message(msg["peer"], msg["message"])
            if success:
                print(f"[NODE {BASE_PORT}] Sent stored message to {msg['peer']}")
                queue.remove_message(msg)
        time.sleep(cfg.RETRY_INTERVAL)
# ________________________________________
# Step 3: Node Receives Messages and Stores Undeliverable Messages
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((cfg.HOST, BASE_PORT))
    server.listen()
    print(f"[NODE {BASE_PORT}] Listening for messages...")
    while True:
        conn, addr = server.accept()
        data = conn.recv(cfg.BUFFER_SIZE).decode()
        print(f"[NODE {BASE_PORT}] Received: {data} from {addr}")
        conn.close()
#________________________________________
#Step 4: Send Initial Messages
if __name__ == "__main__":
    threading.Thread(target=start_server, daemon=True).start()
    threading.Thread(target=forward_loop, daemon=True).start()

    # Send initial messages
    for peer in PEER_PORTS:
        msg = f"Hello from node {BASE_PORT}"
        if not send_message(peer, msg):
            print(f"[NODE {BASE_PORT}] Peer {peer} unavailable, storing message")
            queue.add_message(msg, peer)

    while True:
        time.sleep(1)
