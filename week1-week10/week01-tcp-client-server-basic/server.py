# server.py
import socket
import sys
from config import HOST, PORT, BUFFER_SIZE

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Allow port reuse immediately after close
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        print(f"[SERVER] Persistent server listening on {HOST}:{PORT}")
        print("[SERVER] Press Ctrl+C to stop the server.")

        while True:
            try:
                # Set a timeout so we can check for keyboard interrupts
                server_socket.settimeout(1.0)
                try:
                    conn, addr = server_socket.accept()
                except socket.timeout:
                    continue
                
                print(f"[SERVER] Connection from {addr}")
                
                # Receive message
                data = conn.recv(BUFFER_SIZE)
                if not data:
                    print("[SERVER] Received empty message")
                else:
                    message = data.decode().strip()
                    print(f"[SERVER] Received: {message}")
                    
                    # Basic Validation
                    if len(message) == 0:
                        reply = "ERROR: Empty message"
                    else:
                        reply = f"ACK: {message}"
                    
                    conn.sendall(reply.encode())
                
                conn.close()
                print(f"[SERVER] Closed connection with {addr}")

            except Exception as e:
                print(f"[SERVER] Error handling client: {e}")
                
    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down...")
    except Exception as e:
        print(f"[SERVER] Critical error: {e}")
    finally:
        server_socket.close()
        print("[SERVER] Socket closed. Goodbye.")

if __name__ == "__main__":
    start_server()
