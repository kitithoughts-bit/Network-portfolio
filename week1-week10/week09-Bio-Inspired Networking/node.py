#!/usr/bin/env python3
# node.py — Week 9: Bio-Inspired Networking (Pheromone Routing)
# ============================================================
# Usage:
#   python node.py --port 10000 --peers 10001 10002
#   python node.py --port 10001 --peers 10000 10002
#   python node.py --port 10002 --peers 10000 10001
#
# Interactive commands:
#   send <port> <message>   — queue a directed message
#   flood <message>         — epidemic send to all peers
#   table                   — print pheromone table
#   queue                   — print message queue
#   stats                   — table + queue together
#   reinforce <port> <amt>  — manually reinforce a peer's trail
#   decay                   — manually trigger pheromone evaporation
#   quit                    — shutdown node
# ============================================================

import argparse
import socket
import threading
import time

import config as cfg
from pheromone_table import PheromoneTable
from message_queue import MessageQueue

# ── globals set at startup ────────────────────────────────────────────────────
MY_PORT: int = cfg.BASE_PORT
PEER_PORTS: list[int] = list(cfg.PEER_PORTS)

pheromone_table = PheromoneTable()
mq = MessageQueue()

_shutdown = threading.Event()

# ── logging ───────────────────────────────────────────────────────────────────

def log(text: str):
    print(f"[NODE:{MY_PORT}] {text}", flush=True)

# ── networking ────────────────────────────────────────────────────────────────

def try_send(peer_port: int, payload: str, timeout: float = 2.0) -> bool:
    """
    Attempt TCP send.  On success: reinforce pheromone trail.
    On failure: penalise trail (like a blocked ant path).
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((cfg.HOST, peer_port))
            s.sendall(payload.encode())
        pheromone_table.reinforce(peer_port)
        return True
    except (ConnectionRefusedError, socket.timeout, OSError):
        pheromone_table.penalise(peer_port)
        return False


def handle_connection(conn: socket.socket, addr):
    with conn:
        try:
            data = conn.recv(cfg.BUFFER_SIZE).decode()
        except OSError:
            return
    if not data:
        return

    # Protocol: "FROM:<port>|MSG:<content>"
    from_port = addr[1]
    content = data
    if data.startswith("FROM:"):
        try:
            parts = data.split("|", 1)
            from_port = int(parts[0].split(":")[1])
            content = parts[1].replace("MSG:", "", 1) if len(parts) > 1 else ""
        except (ValueError, IndexError):
            pass

    # Filter out internal probes from display
    if content != "__probe__":
        log(f"← received from :{from_port}  '{content}'")

    # A message arriving means this peer is alive → reinforce its trail
    pheromone_table.reinforce(from_port)

    # Auto-discover new peers
    if from_port != MY_PORT and from_port not in PEER_PORTS:
        PEER_PORTS.append(from_port)
        pheromone_table.seed(from_port, cfg.INITIAL_ENCOUNTER_PHEROMONE)
        log(f"  🐜 discovered new peer :{from_port}")

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
            threading.Thread(
                target=handle_connection, args=(conn, addr), daemon=True
            ).start()

# ── forward loop (core bio-routing logic) ─────────────────────────────────────

def forward_loop():
    """
    Every UPDATE_INTERVAL seconds:
      1. Evaporate pheromones (decay)
      2. Find peers above threshold
      3. Forward queued messages along the strongest trail
    """
    while not _shutdown.is_set():
        time.sleep(cfg.UPDATE_INTERVAL)

        # ── Step 1: Evaporation ───────────────────────────────────────────────
        pheromone_table.decay()

        # ── Step 2: Routing candidates ────────────────────────────────────────
        candidates = pheromone_table.get_best_candidates(cfg.FORWARD_THRESHOLD)

        # ── Step 3: Process queue ─────────────────────────────────────────────
        pending = mq.get_pending()
        if not pending:
            continue

        for msg in pending:
            payload = f"FROM:{MY_PORT}|MSG:{msg.content}"

            if msg.destination is not None:
                # ── Directed: follow the strongest trail toward destination ───
                if msg.destination in candidates:
                    pher = pheromone_table.get_pheromone(msg.destination)
                    log(f"→ 🐜 trail:{pher:.2f} → :{msg.destination}  msg:{msg.msg_id}")
                    if try_send(msg.destination, payload):
                        log(f"  ✓ delivered msg:{msg.msg_id}")
                        mq.mark_delivered(msg.msg_id)
                        mq.increment_hops(msg.msg_id)
                    else:
                        mq.increment_attempts(msg.msg_id)
                        log(f"  ✗ trail broken for :{msg.destination}, queued msg:{msg.msg_id}")
                else:
                    pher = pheromone_table.get_pheromone(msg.destination)
                    log(
                        f"  ⋯ weak trail:{pher:.2f} < {cfg.FORWARD_THRESHOLD} "
                        f"to :{msg.destination}  holding msg:{msg.msg_id}"
                    )
            else:
                # ── Epidemic: spray pheromone to all good candidates ──────────
                sent_any = False
                for peer in candidates:
                    pher = pheromone_table.get_pheromone(peer)
                    log(f"→ 🐜 epidemic trail:{pher:.2f} → :{peer}  msg:{msg.msg_id}")
                    try_send(peer, payload)
                    sent_any = True
                if sent_any:
                    mq.mark_delivered(msg.msg_id)
                else:
                    log(f"  ⋯ no candidates above threshold for epidemic msg:{msg.msg_id}")

# ── probe loop ────────────────────────────────────────────────────────────────

def probe_loop():
    """
    Periodically send heartbeat probes to all known peers.
    Success → reinforce trail.  Failure → penalise.
    This is analogous to scout ants checking paths without food.
    """
    while not _shutdown.is_set():
        time.sleep(cfg.PROBE_INTERVAL)
        for peer in list(PEER_PORTS):
            payload = f"FROM:{MY_PORT}|MSG:__probe__"
            ok = try_send(peer, payload, timeout=1.0)
            pher = pheromone_table.get_pheromone(peer)
            status = "✓" if ok else "✗"
            log(f"  probe :{peer} {status} trail={pher:.2f}")

# ── display helpers ───────────────────────────────────────────────────────────

def print_table():
    snap = pheromone_table.snapshot()
    if not snap:
        log("  pheromone table is empty")
        return
    log("  ── pheromone trail table ──────────────────────────────")
    max_pher = max((e["pher"] for e in snap.values()), default=1.0) or 1.0
    for peer, entry in sorted(snap.items()):
        pher = entry["pher"]
        bar_len = int((pher / max_pher) * 24)
        bar = "█" * bar_len + "░" * (24 - bar_len)
        age = int(time.time() - entry["last_seen"])
        above = "✓" if pher >= cfg.FORWARD_THRESHOLD else "✗"
        print(
            f"       :{peer}  [{bar}] {pher:.3f}  "
            f"ok={entry['success']} fail={entry['failures']}  "
            f"last={age}s  fwd={above}"
        )
    print(f"       threshold={cfg.FORWARD_THRESHOLD}  decay={cfg.DECAY_FACTOR}")


def print_queue():
    pending = mq.get_pending()
    stats = mq.stats()
    log(f"  queue: {stats['queued']} pending  {stats['delivered']} delivered")
    for msg in pending:
        print(f"       {msg}")

# ── interactive CLI ───────────────────────────────────────────────────────────

def cli_loop():
    print()
    print("  Commands: send <port> <msg> | flood <msg> | table | queue | stats")
    print("            reinforce <port> <amount> | decay | quit")
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
            if dest not in PEER_PORTS:
                PEER_PORTS.append(dest)
                pheromone_table.seed(dest, cfg.INITIAL_ENCOUNTER_PHEROMONE)
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

        elif cmd == "reinforce":
            if len(parts) < 3:
                print("  usage: reinforce <port> <amount>")
                continue
            try:
                peer = int(parts[1])
                amt  = float(parts[2])
            except ValueError:
                print("  port=int, amount=float")
                continue
            pheromone_table.reinforce(peer, amt)
            log(f"  manually reinforced :{peer} by {amt:.2f}")
            print_table()

        elif cmd == "decay":
            pheromone_table.decay()
            log("  manual decay applied")
            print_table()

        else:
            print(f"  unknown command: {cmd}")

# ── main ──────────────────────────────────────────────────────────────────────

def main():
    global MY_PORT, PEER_PORTS

    parser = argparse.ArgumentParser(description="Week 9 – Bio-Inspired Routing Node")
    parser.add_argument("--port",  type=int, default=cfg.BASE_PORT)
    parser.add_argument("--peers", type=int, nargs="*", default=cfg.PEER_PORTS)
    args = parser.parse_args()

    MY_PORT    = args.port
    PEER_PORTS = list(args.peers or [])

    # Seed pheromone trails for known peers
    for peer in PEER_PORTS:
        pheromone_table.seed(peer, cfg.INITIAL_PHEROMONE)

    log(
        f"starting | peers={PEER_PORTS} | "
        f"threshold={cfg.FORWARD_THRESHOLD} | "
        f"decay={cfg.DECAY_FACTOR} | "
        f"reinforcement={cfg.REINFORCEMENT}"
    )

    threading.Thread(target=server_thread, daemon=True).start()
    threading.Thread(target=forward_loop,  daemon=True).start()
    threading.Thread(target=probe_loop,    daemon=True).start()

    try:
        cli_loop()
    except KeyboardInterrupt:
        _shutdown.set()

    log("bye.")


if __name__ == "__main__":
    main()
