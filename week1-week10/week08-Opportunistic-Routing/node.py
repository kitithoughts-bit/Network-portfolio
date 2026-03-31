#!/usr/bin/env python3
# node.py — Week 8: Opportunistic Routing
# ============================================================
# Usage:
#   python node.py --port 9000 --peers 9001 9002
#   python node.py --port 9001 --peers 9000 9002
#   python node.py --port 9002 --peers 9000 9001
#
# Interactive commands (type and press Enter):
#   send <port> <message>   — queue a message for a specific peer
#   flood <message>         — epidemic: queue to all known peers
#   table                   — print current delivery probability table
#   queue                   — print current message queue
#   stats                   — print delivery statistics
#   decay                   — manually trigger probability decay
#   quit                    — shut down this node
# ============================================================

import argparse
import socket
import threading
import time
import sys

import config as cfg
from delivery_table import DeliveryTable
from message_queue import MessageQueue


# ── globals set at startup ────────────────────────────────────────────────────
MY_PORT: int = cfg.BASE_PORT
PEER_PORTS: list[int] = list(cfg.PEER_PORTS)

delivery_table = DeliveryTable()
mq = MessageQueue()

_shutdown = threading.Event()


# ── helpers ───────────────────────────────────────────────────────────────────

def tag(text: str = "") -> str:
    return f"[NODE:{MY_PORT}] {text}"


def log(text: str):
    print(tag(text), flush=True)


# ── networking ────────────────────────────────────────────────────────────────

def try_send(peer_port: int, payload: str, timeout: float = 2.0) -> bool:
    """
    Attempt a single TCP send to peer_port.
    Returns True on success, False on any error.
    Updates delivery_table accordingly.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((cfg.HOST, peer_port))
            s.sendall(payload.encode())
        delivery_table.record_encounter(peer_port)
        return True
    except (ConnectionRefusedError, socket.timeout, OSError):
        delivery_table.record_failure(peer_port)
        return False


def handle_connection(conn: socket.socket, addr):
    """Called in a thread for each incoming connection."""
    with conn:
        try:
            data = conn.recv(cfg.BUFFER_SIZE).decode()
        except OSError:
            return

    if not data:
        return

    # Parse protocol: "FROM:<port>|MSG:<content>"
    from_port = addr[1]   # fallback
    content = data

    if data.startswith("FROM:"):
        try:
            parts = data.split("|", 1)
            from_port = int(parts[0].split(":")[1])
            content = parts[1].replace("MSG:", "", 1) if len(parts) > 1 else ""
        except (ValueError, IndexError):
            pass

    log(f"← received from :{from_port}  '{content}'")

    # Seed delivery table: we just had a live encounter with this peer
    delivery_table.record_encounter(from_port)

    # If this peer is not in our known list yet, add it
    if from_port not in PEER_PORTS:
        PEER_PORTS.append(from_port)
        log(f"  discovered new peer :{from_port}")


# ── server thread ─────────────────────────────────────────────────────────────

def server_thread():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((cfg.HOST, MY_PORT))
        srv.listen(10)
        srv.settimeout(1.0)
        log(f"listening on :{MY_PORT}")

        while not _shutdown.is_set():
            try:
                conn, addr = srv.accept()
            except socket.timeout:
                continue
            t = threading.Thread(
                target=handle_connection, args=(conn, addr), daemon=True
            )
            t.start()


# ── forward loop ──────────────────────────────────────────────────────────────

def forward_loop():
    """
    Periodically check the message queue.
    For each pending message, attempt delivery to the best candidate(s).
    Only forwards if delivery probability >= FORWARD_THRESHOLD.
    """
    while not _shutdown.is_set():
        time.sleep(cfg.UPDATE_INTERVAL)

        # Decay probabilities a little each cycle
        delivery_table.apply_decay()

        pending = mq.get_pending()
        if not pending:
            continue

        candidates = delivery_table.get_best_candidates(cfg.FORWARD_THRESHOLD)

        for msg in pending:
            if msg.destination is not None:
                # Directed: only forward to specific peer if it's a good candidate
                if msg.destination in candidates:
                    payload = f"FROM:{MY_PORT}|MSG:{msg.content}"
                    log(f"→ forwarding msg:{msg.msg_id} → :{msg.destination} "
                        f"(prob={delivery_table.get_probability(msg.destination):.2f})")
                    if try_send(msg.destination, payload):
                        log(f"  ✓ delivered msg:{msg.msg_id}")
                        mq.mark_delivered(msg.msg_id)
                    else:
                        mq.increment_attempts(msg.msg_id)
                        log(f"  ✗ failed msg:{msg.msg_id}, queued for retry")
                else:
                    prob = delivery_table.get_probability(msg.destination)
                    log(f"  ⋯ holding msg:{msg.msg_id} "
                        f"(prob={prob:.2f} < threshold={cfg.FORWARD_THRESHOLD})")
            else:
                # Epidemic: forward to ALL good candidates
                for peer in candidates:
                    payload = f"FROM:{MY_PORT}|MSG:{msg.content}"
                    log(f"→ epidemic msg:{msg.msg_id} → :{peer}")
                    try_send(peer, payload)
                mq.mark_delivered(msg.msg_id)


# ── probe loop (keep table alive) ────────────────────────────────────────────

def probe_loop():
    """
    Periodically probe each known peer with a tiny heartbeat.
    Updates delivery probabilities based on reachability.
    """
    PROBE_INTERVAL = cfg.UPDATE_INTERVAL * 2

    while not _shutdown.is_set():
        time.sleep(PROBE_INTERVAL)
        for peer in list(PEER_PORTS):
            payload = f"FROM:{MY_PORT}|MSG:__probe__"
            reachable = try_send(peer, payload, timeout=1.0)
            prob = delivery_table.get_probability(peer)
            status = "✓" if reachable else "✗"
            log(f"  probe :{peer} {status} prob={prob:.2f}")


# ── interactive CLI ───────────────────────────────────────────────────────────

def print_table():
    snap = delivery_table.snapshot()
    if not snap:
        log("  delivery table is empty")
        return
    log("  ── delivery probability table ──────────────────")
    for peer, entry in sorted(snap.items()):
        bar_len = int(entry["prob"] * 20)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        age = int(time.time() - entry["last_seen"])
        print(f"       :{peer}  [{bar}] {entry['prob']:.2f}  "
              f"encounters={entry['seen']}  last={age}s ago")


def print_queue():
    pending = mq.get_pending()
    stats = mq.stats()
    log(f"  queue: {stats['queued']} pending  {stats['delivered']} delivered")
    for msg in pending:
        print(f"       {msg}")


def cli_loop():
    print()
    print("  Commands: send <port> <msg> | flood <msg> | table | queue | stats | decay | quit")
    print()

    while not _shutdown.is_set():
        try:
            line = input().strip()
        except (EOFError, KeyboardInterrupt):
            _shutdown.set()
            break

        if not line:
            continue

        parts = line.split(maxsplit=2)
        cmd = parts[0].lower()

        if cmd == "quit":
            log("shutting down…")
            _shutdown.set()

        elif cmd == "send":
            if len(parts) < 3:
                print("  usage: send <port> <message>")
                continue
            try:
                dest = int(parts[1])
            except ValueError:
                print("  port must be an integer")
                continue
            content = parts[2]
            # Seed the peer if not known
            if dest not in PEER_PORTS:
                PEER_PORTS.append(dest)
                delivery_table.update_probability(dest, cfg.INITIAL_ENCOUNTER_PROB)
            msg = mq.enqueue(content, destination=dest)
            log(f"  queued {msg}")

        elif cmd == "flood":
            if len(parts) < 2:
                print("  usage: flood <message>")
                continue
            content = " ".join(parts[1:])
            msg = mq.enqueue(content, destination=None)
            log(f"  queued epidemic {msg}")

        elif cmd == "table":
            print_table()

        elif cmd == "queue":
            print_queue()

        elif cmd == "stats":
            print_table()
            print_queue()

        elif cmd == "decay":
            delivery_table.apply_decay()
            log("  manual decay applied")
            print_table()

        else:
            print(f"  unknown command: {cmd}")


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    global MY_PORT, PEER_PORTS

    parser = argparse.ArgumentParser(description="Week 8 – Opportunistic Routing Node")
    parser.add_argument("--port",  type=int, default=cfg.BASE_PORT,
                        help="This node's listen port (default: %(default)s)")
    parser.add_argument("--peers", type=int, nargs="*", default=cfg.PEER_PORTS,
                        help="Known peer ports to seed (default: %(default)s)")
    args = parser.parse_args()

    MY_PORT = args.port
    PEER_PORTS = list(args.peers or [])

    # Seed delivery table with initial (neutral) probabilities for known peers
    for peer in PEER_PORTS:
        delivery_table.update_probability(peer, cfg.INITIAL_ENCOUNTER_PROB)

    log(f"starting | peers={PEER_PORTS} | threshold={cfg.FORWARD_THRESHOLD}")

    # Spin up background threads
    threading.Thread(target=server_thread, daemon=True).start()
    threading.Thread(target=forward_loop,  daemon=True).start()
    threading.Thread(target=probe_loop,    daemon=True).start()

    # CLI runs on main thread
    try:
        cli_loop()
    except KeyboardInterrupt:
        _shutdown.set()

    log("bye.")


if __name__ == "__main__":
    main()
