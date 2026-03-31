# server_threaded.py
import socket
import threading
from config import HOST, PORT, BUFFER_SIZE
from logger import log_info, log_error

def handle_client(conn, addr):
    log_info(f"Connection from {addr}")
    try:
        # Simulate some processing time
        # import time; time.sleep(2)
        
        data = conn.recv(BUFFER_SIZE)
        if not data:
            log_info(f"Empty message from {addr}")
        else:
            message = data.decode().strip()
            log_info(f"Received from {addr}: {message}")
            
            # Validation
            if not message:
                reply = "ERROR: Empty message"
            else:
                reply = f"ACK: {message} (Threaded)"
            
            conn.sendall(reply.encode())
            log_info(f"Sent reply to {addr}")
            
    except Exception as e:
        log_error(f"Error handling {addr}: {e}")
    finally:
        conn.close()
        log_info(f"Closed connection with {addr}")

def start_threaded_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5) # Increase backlog for concurrent clients
        log_info(f"Threaded server listening on {HOST}:{PORT}")
        
        while True:
            # We don't use timeout here for simplicity, but in production we might
            try:
                conn, addr = server_socket.accept()
                client_thread = threading.Thread(target=handle_client, args=(conn, addr))
                client_thread.daemon = True # Allows server to exit even if threads are running
                client_thread.start()
                log_info(f"Started thread for {addr}. Active threads: {threading.active_count() - 1}")
            except Exception as e:
                log_error(f"Accept error: {e}")
                
    except KeyboardInterrupt:
        log_info("Server shutting down...")
    except Exception as e:
        log_error(f"Critical error: {e}")
    finally:
        server_socket.close()
        log_info("Socket closed. Goodbye.")

if __name__ == "__main__":
    start_threaded_server()
