# token_store.py — Week 10: Quantum-Inspired Networking
# ============================================================
# A thread-safe vault for QuantumTokens held by this node.
# Expired and collapsed tokens are purged automatically.
# ============================================================

import threading
import time

from quantum_token import QuantumToken


class TokenStore:
    """
    Local vault of QuantumTokens waiting to be forwarded or read.

    Invariants enforced:
      - A token is stored at most once (by token_id).
      - Expired / collapsed tokens are never returned and are purged on access.
    """

    def __init__(self):
        self._store: dict[str, QuantumToken] = {}   # token_id → token
        self._lock = threading.Lock()
        self._forwarded: set[str] = set()           # IDs already forwarded
        self._read_count = 0
        self._dropped_count = 0

    def add(self, token: QuantumToken) -> bool:
        """
        Add a token to the vault.
        Returns False if a token with the same ID already exists (no-cloning).
        """
        with self._lock:
            if token.token_id in self._store or token.token_id in self._forwarded:
                return False   # Duplicate — no-cloning violated
            if not token.is_valid():
                self._dropped_count += 1
                return False   # Already dead on arrival
            self._store[token.token_id] = token
            return True

    def get_pending(self) -> list[QuantumToken]:
        """Return live tokens, purging dead ones."""
        with self._lock:
            live, dead = [], []
            for tok in self._store.values():
                (live if tok.is_valid() else dead).append(tok)
            for tok in dead:
                del self._store[tok.token_id]
                self._dropped_count += 1
            return live

    def mark_forwarded(self, token_id: str):
        with self._lock:
            self._store.pop(token_id, None)
            self._forwarded.add(token_id)

    def mark_read(self, token_id: str):
        with self._lock:
            self._store.pop(token_id, None)
            self._read_count += 1

    def stats(self) -> dict:
        with self._lock:
            return {
                "held":     len(self._store),
                "read":     self._read_count,
                "dropped":  self._dropped_count,
                "forwarded": len(self._forwarded),
            }

    def all_tokens(self) -> list[QuantumToken]:
        with self._lock:
            return list(self._store.values())
