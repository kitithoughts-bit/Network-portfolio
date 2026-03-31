# logger.py
from datetime import datetime

def log_event(level, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] [{level}] {message}")

def log_info(message):
    log_event("INFO", message)

def log_error(message):
    log_event("ERROR", message)
