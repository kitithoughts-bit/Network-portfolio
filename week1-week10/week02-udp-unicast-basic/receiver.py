# Step 1: Create UDP Receiver
# receiver.py
import socket
from config import HOST, PORT, BUFFER_SIZE

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

print(f"[RECEIVER] Listening on {HOST}:{PORT}")

# Step 2: Receive Datagram
while True:
    data, addr = sock.recvfrom(BUFFER_SIZE)
    print(f"[RECEIVER] From {addr}: {data.decode()}")
