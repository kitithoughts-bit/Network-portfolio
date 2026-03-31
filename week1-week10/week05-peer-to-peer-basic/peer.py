# Step 1: Create a Peer Node (Listener + Sender)
# peer.py
import socket
import threading
import sys
from config import HOST, BASE_PORT, BUFFER_SIZE

peer_id = int(sys.argv[1])
PORT = BASE_PORT + peer_id
# ________________________________________
# Step 2: Listener Thread
def listen():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen(5)
    print(f"[PEER {peer_id}] Listening on {PORT}")

    while True:
        conn, addr = sock.accept()
        data = conn.recv(BUFFER_SIZE)
        print(f"[PEER {peer_id}] From {addr}: {data.decode()}")
        conn.close()
# ________________________________________
# Step 3: Sender Function
def send_message(target_peer_id, message):
    target_port = BASE_PORT + target_peer_id
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, target_port))
    sock.sendall(message.encode())
    sock.close()
#________________________________________
# Step 4: Run Listener + Send Message
threading.Thread(target=listen, daemon=True).start()

while True:
    target = int(input("Send to peer ID: "))
    msg = input("Message: ")
    send_message(target, msg)
