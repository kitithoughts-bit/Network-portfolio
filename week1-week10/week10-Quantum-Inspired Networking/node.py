#!/usr/bin/env python3
# node.py — Week 10: Quantum-Inspired Networking
# ============================================================
# Usage:
#   python node.py --port 11000 --peers 11001 11002
#   python node.py --port 11001 --peers 11000 11002
#   python node.py --port 11002 --peers 11000 11001
#
# Interactive commands:
#   send <port> <message>     — send a one-time token to a specific peer
#   entangle <port> <message> — create an entangled pair; send α, hold β
#   flood <message>           — send a token to ALL peers (epidemic)
#   read <token_id_prefix>    — locally read (collapse) a held token
#   tokens                    — list all tokens currently held by this node
#   stats                     — show token vault statistics
#   quit                      — shutdown node
# ============================================================

import argparse
import random
import socket
import threading
import time

import config as cfg
from quantum_token import QuantumToken, EntangledPair
from token_store import TokenStore

# ── globals ───────────────────────────────────────────────────────────────────
MY_PORT: int = cfg.BASE_PORT
PEER_PORTS: list[int] = list(cfg.PEER_PORTS)

store = TokenStore()
_shutdown = threading.Event()


# ── logging ───────────────────────────────────────────────────────────────────

def log(text: str):
    print(f"[NODE:{MY_PORT}] {text}", flush=True)


# ── networking ────────────────────────────────────────────────────────────────

def try_send_token(peer_port: int, token: QuantumToken, timeout: float = 2.0) -> bool:
    """
    Serialise and send a QuantumToken over TCP.
    Simulates CHANNEL_NOISE: with probability CHANNEL_NOISE the send is silently dropped.
    """
    # Probabilistic channel noise (quantum channel decoherence analogy)
    if cfg.CHANNEL_NOISE > 0 and random.random() < cfg.CHANNEL_NOISE:
        log(f"  ⚡ channel noise — token:{token.token_id[:8]} lost in transit to :{peer_port}")
        return False

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((cfg.HOST, peer_port))
            payload = f"FROM:{MY_PORT}|{token.serialise()}"
            s.sendall(payload.encode())
        return True
    except (ConnectionRefusedError, socket.timeout, OSError):
        return False


def handle_connection(conn: socket.socket, addr):
    with conn:
        try:
            raw = conn.recv(cfg.BUFFER_SIZE).decode()
        except OSError:
            return
    if not raw:
        return

    # Parse: "FROM:<port>|TOKEN|..."  or  "FROM:<port>|MSG:__probe__"
    from_port = addr[1]
    body = raw
    if raw.startswith("FROM:"):
        try:
            prefix, body = raw.split("|", 1)
            from_port = int(prefix.split(":")[1])
        except (ValueError, IndexError):
            pass

    if body == "MSG:__probe__":
        return   # Heartbeat — no action needed

    # Attempt to deserialise as a QuantumToken
    token = QuantumToken.deserialise(body)
    if token is None:
        log(f"  ✗ received malformed payload from :{from_port}")
        return

    log(f"← received {token}")

    if not token.is_valid():
        reason = (
            "already collapsed" if token.is_collapsed()
            else "expired" if token.is_expired()
            else "hop limit reached"
        )
        log(f"  ✗ token:{token.token_id[:8]} rejected — {reason}")
        return

    # ── Decision: read locally or forward? ───────────────────────────────────
    # Policy: if this is the final hop (hops == MAX_HOPS - 1), read it here.
    #         Otherwise store it for the forward loop to handle.
    if token.hops >= cfg.MAX_HOPS - 1:
        message = token.read()
        if message:
            log(f"  📖 READ (final hop): '{message}'")
            store.mark_read(token.token_id)
        else:
            log(f"  ✗ token:{token.token_id[:8]} collapsed before final read")
    else:
        added = store.add(token)
        if added:
            log(f"  📥 stored token:{token.token_id[:8]} (hops={token.hops})")
        else:
            log(f"  ✗ token:{token.token_id[:8]} rejected — duplicate (no-cloning)")


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


# ── forward loop ──────────────────────────────────────────────────────────────

def forward_loop():
    """
    Every UPDATE_INTERVAL seconds, forward held tokens to the next peer.

    No-cloning enforcement:
      - A token is forwarded to exactly ONE peer.
      - After forwarding, it is removed from the local store.
      - The peer receives a copy with hops+1; if hops reaches MAX_HOPS
        the receiving node MUST read (not forward) it.

    This models the quantum no-cloning theorem: you cannot duplicate
    an unknown quantum state.  A classical analogy is a one-time pad
    that is physically destroyed after use.
    """
    while not _shutdown.is_set():
        time.sleep(cfg.UPDATE_INTERVAL)

        pending = store.get_pending()
        if not pending:
            continue

        active_peers = [p for p in PEER_PORTS if p != MY_PORT]
        if not active_peers:
            continue

        for token in pending:
            # Choose ONE peer only (no broadcast — no-cloning)
            peer = random.choice(active_peers)
            forwarded = token.forward()

            log(
                f"→ forwarding token:{token.token_id[:8]} "
                f"hops={forwarded.hops} → :{peer}"
            )
            if try_send_token(peer, forwarded):
                log(f"  ✓ token:{token.token_id[:8]} delivered to :{peer}")
                store.mark_forwarded(token.token_id)
            else:
                log(f"  ✗ token:{token.token_id[:8]} send failed, retrying next cycle")


# ── probe loop ────────────────────────────────────────────────────────────────

def probe_loop():
    while not _shutdown.is_set():
        time.sleep(cfg.PROBE_INTERVAL)
        for peer in list(PEER_PORTS):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1.0)
                    s.connect((cfg.HOST, peer))
                    s.sendall(f"FROM:{MY_PORT}|MSG:__probe__".encode())
            except OSError:
                pass


# ── display helpers ───────────────────────────────────────────────────────────

def print_tokens():
    tokens = store.all_tokens()
    if not tokens:
        log("  no tokens held")
        return
    log(f"  ── held tokens ({len(tokens)}) ─────────────────────────────")
    for tok in tokens:
        print(f"       {tok}")


def print_stats():
    s = store.stats()
    log(
        f"  stats  held={s['held']}  read={s['read']}  "
        f"forwarded={s['forwarded']}  dropped={s['dropped']}"
    )


# ── interactive CLI ───────────────────────────────────────────────────────────

def cli_loop():
    print()
    print("  Commands: send <port> <msg> | entangle <port> <msg> | flood <msg>")
    print("            read <token_id_prefix> | tokens | stats | quit")
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

        # ── send ─────────────────────────────────────────────────────────────
        if cmd == "send":
            if len(parts) < 3:
                print("  usage: send <port> <message>")
                continue
            try:
                dest = int(parts[1])
            except ValueError:
                print("  port must be an integer")
                continue
            token = QuantumToken(content=parts[2])
            log(f"  created {token}")
            if try_send_token(dest, token):
                log(f"  ✓ token:{token.token_id[:8]} dispatched → :{dest}")
            else:
                log(f"  ✗ could not reach :{dest}, storing locally")
                store.add(token)

        # ── entangle ─────────────────────────────────────────────────────────
        elif cmd == "entangle":
            if len(parts) < 3:
                print("  usage: entangle <port> <message>")
                continue
            try:
                dest = int(parts[1])
            except ValueError:
                print("  port must be an integer")
                continue
            pair = EntangledPair(content=parts[2])
            log(f"  created {pair}")
            log(f"  → sending α to :{dest}")
            if try_send_token(dest, pair.alpha):
                log(f"  ✓ α dispatched  |  β held locally")
            else:
                log(f"  ✗ α send failed, storing both locally")
                store.add(pair.alpha)
            # β always held locally
            store.add(pair.beta)
            log(f"  β stored: {pair.beta}")
            log(f"  When α is READ at :{dest}, β here will auto-collapse")

        # ── flood ─────────────────────────────────────────────────────────────
        elif cmd == "flood":
            if len(parts) < 2:
                print("  usage: flood <message>")
                continue
            content = " ".join(parts[1:])
            # Flood creates a SEPARATE token per peer (each unique — no cloning)
            active = [p for p in PEER_PORTS if p != MY_PORT]
            if not active:
                print("  no peers to flood")
                continue
            for peer in active:
                tok = QuantumToken(content=content)  # New token, new ID
                log(f"  → token:{tok.token_id[:8]} → :{peer}")
                if not try_send_token(peer, tok):
                    log(f"  ✗ peer :{peer} unreachable")

        # ── read ──────────────────────────────────────────────────────────────
        elif cmd == "read":
            if len(parts) < 2:
                print("  usage: read <token_id_prefix>")
                continue
            prefix = parts[1]
            found = None
            for tok in store.all_tokens():
                if tok.token_id.startswith(prefix):
                    found = tok
                    break
            if not found:
                print(f"  no token matching prefix '{prefix}'")
                continue
            message = found.read()
            if message:
                log(f"  📖 READ: '{message}'")
                store.mark_read(found.token_id)
                log(f"  ☠️  token:{found.token_id[:8]} collapsed — entangled twins also collapsed")
            else:
                log(f"  ✗ token:{found.token_id[:8]} already collapsed / expired")

        # ── tokens ────────────────────────────────────────────────────────────
        elif cmd == "tokens":
            print_tokens()

        # ── stats ─────────────────────────────────────────────────────────────
        elif cmd == "stats":
            print_stats()
            print_tokens()

        # ── quit ──────────────────────────────────────────────────────────────
        elif cmd == "quit":
            log("shutting down…")
            _shutdown.set()

        else:
            print(f"  unknown command: {cmd}")


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    global MY_PORT, PEER_PORTS

    parser = argparse.ArgumentParser(description="Week 10 – Quantum-Inspired Networking Node")
    parser.add_argument("--port",  type=int, default=cfg.BASE_PORT)
    parser.add_argument("--peers", type=int, nargs="*", default=cfg.PEER_PORTS)
    args = parser.parse_args()

    MY_PORT    = args.port
    PEER_PORTS = list(args.peers or [])

    log(
        f"starting | peers={PEER_PORTS} | "
        f"token_expiry={cfg.TOKEN_EXPIRY}s | "
        f"max_hops={cfg.MAX_HOPS} | "
        f"channel_noise={cfg.CHANNEL_NOISE:.0%}"
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
