# Step 1: Multicast Receiver (Join Group)
# receiver.py
import socket
import struct
from config import MULTICAST_GROUP, PORT, BUFFER_SIZE

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.bind(("", PORT))

mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

print(f"[RECEIVER] Joined {MULTICAST_GROUP}:{PORT}")

while True:
    data, addr = sock.recvfrom(BUFFER_SIZE)
    print(f"[RECEIVER] {addr} -> {data.decode()}")
