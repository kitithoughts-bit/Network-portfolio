# delivery_table.py — Week 8: Opportunistic Routing
# ============================================================
# Tracks per-peer delivery probabilities.
# Probabilities are updated on:
#   - Successful encounters  → increase
#   - Periodic decay         → decrease slowly
#   - Failed connections     → small penalty
# ============================================================

import threading
import time
from config import DECAY_FACTOR, INITIAL_ENCOUNTER_PROB, ENCOUNTER_INCREMENT


class DeliveryTable:
    """
    Thread-safe delivery probability table.

    Each entry:
        peer_port (int) → {
            "prob":      float   current delivery probability [0.0 – 1.0]
            "seen":      int     total successful encounters
            "last_seen": float   timestamp of last successful contact
        }
    """

    def __init__(self):
        self._table: dict[int, dict] = {}
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def record_encounter(self, peer: int) -> float:
        """
        Called when a message was successfully delivered to `peer`.
        Increases probability (capped at 1.0).
        Returns the new probability.
        """
        with self._lock:
            entry = self._table.get(peer)
            if entry is None:
                new_prob = INITIAL_ENCOUNTER_PROB + ENCOUNTER_INCREMENT
            else:
                new_prob = min(1.0, entry["prob"] + ENCOUNTER_INCREMENT)

            self._table[peer] = {
                "prob":      new_prob,
                "seen":      (entry["seen"] if entry else 0) + 1,
                "last_seen": time.time(),
            }
            return new_prob

    def record_failure(self, peer: int):
        """
        Called when a connection attempt to `peer` failed.
        Applies a small penalty.
        """
        FAILURE_PENALTY = 0.05
        with self._lock:
            entry = self._table.get(peer)
            if entry:
                entry["prob"] = max(0.0, entry["prob"] - FAILURE_PENALTY)

    def update_probability(self, peer: int, prob: float):
        """Manually set probability (e.g. from config or seed data)."""
        with self._lock:
            existing = self._table.get(peer, {})
            self._table[peer] = {
                "prob":      max(0.0, min(1.0, prob)),
                "seen":      existing.get("seen", 0),
                "last_seen": existing.get("last_seen", time.time()),
            }

    def get_probability(self, peer: int) -> float:
        with self._lock:
            entry = self._table.get(peer)
            return entry["prob"] if entry else 0.0

    def get_best_candidates(self, threshold: float) -> list[int]:
        """Return peers whose delivery probability >= threshold, sorted best-first."""
        with self._lock:
            candidates = [
                (peer, entry["prob"])
                for peer, entry in self._table.items()
                if entry["prob"] >= threshold
            ]
        candidates.sort(key=lambda x: x[1], reverse=True)
        return [peer for peer, _ in candidates]

    def apply_decay(self):
        """
        Decay all probabilities slightly (call periodically).
        Models the idea that unseen peers become less reliable over time.
        """
        with self._lock:
            for entry in self._table.values():
                entry["prob"] = max(0.0, entry["prob"] * DECAY_FACTOR)

    def snapshot(self) -> dict:
        """Return a copy of the full table for logging/display."""
        with self._lock:
            return {
                peer: dict(entry)
                for peer, entry in self._table.items()
            }

    def all_peers(self) -> list[int]:
        with self._lock:
            return list(self._table.keys())
