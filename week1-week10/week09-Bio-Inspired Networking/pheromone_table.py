# pheromone_table.py — Week 9: Bio-Inspired Networking
# ============================================================
# Models the pheromone trail system used by ant colonies.
#
# Real ants:
#   - Lay pheromone on a path when they find food
#   - Follow paths with stronger pheromone
#   - Pheromone evaporates over time (decay)
#   - Shorter/faster routes get reinforced more → emerge as "best path"
#
# Here:
#   - Pheromone per peer-port represents "how good is this link"
#   - Successful delivery → reinforce (lay trail)
#   - Failed delivery    → penalise  (bad trail)
#   - Every cycle        → decay     (evaporation)
#
# Routing decision:
#   Pick the peer(s) whose pheromone >= FORWARD_THRESHOLD,
#   preferring the highest value (greedy best-first).
# ============================================================

import threading
import time

from config import (
    DECAY_FACTOR,
    REINFORCEMENT,
    FAILURE_PENALTY,
    INITIAL_PHEROMONE,
    INITIAL_ENCOUNTER_PHEROMONE,
)


class PheromoneTable:
    """
    Thread-safe pheromone table.

    Internal schema per peer:
        {
            "pher":      float   current pheromone level (≥ 0)
            "success":   int     total successful sends
            "failures":  int     total failed sends
            "last_seen": float   timestamp of last successful contact
        }
    """

    def __init__(self):
        self._table: dict[int, dict] = {}
        self._lock = threading.Lock()

    # ── write operations ──────────────────────────────────────────────────────

    def seed(self, peer: int, value: float = INITIAL_PHEROMONE):
        """Set initial pheromone for a known peer (won't overwrite existing)."""
        with self._lock:
            if peer not in self._table:
                self._table[peer] = {
                    "pher":      max(0.0, value),
                    "success":   0,
                    "failures":  0,
                    "last_seen": time.time(),
                }

    def reinforce(self, peer: int, amount: float = REINFORCEMENT):
        """
        Increase pheromone on a peer (called after successful send).
        Analogous to an ant laying a pheromone trail on the return path.
        """
        with self._lock:
            entry = self._table.setdefault(peer, _new_entry(INITIAL_ENCOUNTER_PHEROMONE))
            entry["pher"] += amount
            entry["success"] += 1
            entry["last_seen"] = time.time()

    def penalise(self, peer: int, amount: float = FAILURE_PENALTY):
        """
        Decrease pheromone on a peer (called after failed send).
        Models a blocked / broken trail.
        """
        with self._lock:
            entry = self._table.get(peer)
            if entry:
                entry["pher"] = max(0.0, entry["pher"] - amount)
                entry["failures"] += 1

    def set_pheromone(self, peer: int, value: float):
        """Manually set pheromone level (useful for seeding / testing)."""
        with self._lock:
            entry = self._table.setdefault(peer, _new_entry(value))
            entry["pher"] = max(0.0, value)

    def decay(self):
        """
        Evaporate all pheromone trails by DECAY_FACTOR.
        Called every UPDATE_INTERVAL.  Trails not reinforced will fade to 0.
        """
        with self._lock:
            for entry in self._table.values():
                entry["pher"] = max(0.0, entry["pher"] * DECAY_FACTOR)

    # ── read operations ───────────────────────────────────────────────────────

    def get_pheromone(self, peer: int) -> float:
        with self._lock:
            entry = self._table.get(peer)
            return entry["pher"] if entry else 0.0

    def get_best_candidates(self, threshold: float) -> list[int]:
        """
        Return peers whose pheromone >= threshold, sorted strongest-first.
        This is the routing decision: follow the most-reinforced trail.
        """
        with self._lock:
            candidates = [
                (peer, entry["pher"])
                for peer, entry in self._table.items()
                if entry["pher"] >= threshold
            ]
        candidates.sort(key=lambda x: x[1], reverse=True)
        return [peer for peer, _ in candidates]

    def all_peers(self) -> list[int]:
        with self._lock:
            return list(self._table.keys())

    def snapshot(self) -> dict:
        """Return a deep copy of the table for logging/display."""
        with self._lock:
            return {peer: dict(entry) for peer, entry in self._table.items()}


# ── helpers ───────────────────────────────────────────────────────────────────

def _new_entry(initial_pher: float) -> dict:
    return {
        "pher":      max(0.0, initial_pher),
        "success":   0,
        "failures":  0,
        "last_seen": time.time(),
    }
