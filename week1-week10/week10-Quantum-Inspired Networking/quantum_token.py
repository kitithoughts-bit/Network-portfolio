# token.py — Week 10: Quantum-Inspired Networking
# ============================================================
# Three quantum-inspired primitives, all implemented classically:
#
#  1. QuantumToken  — one-time-read, expiring, hop-limited
#     Analogy: a photon.  It can only be measured once.
#     Once read, the state collapses — no copy can ever carry the same value.
#
#  2. EntangledPair — two tokens sharing an entanglement_id.
#     The first READ collapses both simultaneously via a shared registry.
#     Analogy: Bell-state pair — measuring one instantly determines the other.
#
#  3. TokenRegistry — global registry that enforces collapse across all tokens.
#     In a real network this would require a trusted third party or a
#     distributed consensus mechanism (which is exactly why quantum networks
#     are hard to build classically).
# ============================================================

import time
import uuid
import threading
from dataclasses import dataclass, field
from typing import Optional

from config import TOKEN_EXPIRY, MAX_HOPS


# ── Shared collapse registry ───────────────────────────────────────────────────

class TokenRegistry:
    """
    Singleton-style registry that tracks which token IDs have already been read.
    All QuantumToken and EntangledPair objects share this registry.
    Enforces the no-cloning / state-collapse constraint globally (within a process).
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._collapsed: set[str] = set()
            cls._instance._entangled_groups: dict[str, set[str]] = {}
            cls._instance._rlock = threading.RLock()
        return cls._instance

    def register_entangled(self, group_id: str, token_id: str):
        with self._rlock:
            self._entangled_groups.setdefault(group_id, set()).add(token_id)

    def collapse(self, token_id: str) -> bool:
        """
        Mark token_id as collapsed (read).
        If it belongs to an entangled group, collapse all siblings too.
        Returns True if this was the first read (success), False if already collapsed.
        """
        with self._rlock:
            if token_id in self._collapsed:
                return False   # Already read — state collapse in effect
            self._collapsed.add(token_id)
            # Collapse all entangled siblings
            for group_id, members in self._entangled_groups.items():
                if token_id in members:
                    for sibling in members:
                        self._collapsed.add(sibling)
            return True

    def is_collapsed(self, token_id: str) -> bool:
        with self._rlock:
            return token_id in self._collapsed

    def active_count(self) -> int:
        with self._rlock:
            return sum(
                1 for gid, members in self._entangled_groups.items()
                for m in members
                if m not in self._collapsed
            )


_registry = TokenRegistry()


# ── QuantumToken ───────────────────────────────────────────────────────────────

@dataclass
class QuantumToken:
    """
    A one-time-read, expiring, hop-limited message token.

    Invariants:
      - Can only be READ once.  Second read → returns None (collapsed).
      - Expires after TOKEN_EXPIRY seconds from creation.
      - Carries a hop counter; dropped after MAX_HOPS.
      - Cannot be cloned: serialise() / deserialise() preserve the token_id,
        so the registry correctly rejects a duplicate read.

    Quantum analogy:
      A single photon carrying polarisation state.
      Measuring it collapses the wavefunction — the photon is gone.
    """
    content: str
    token_id: str       = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float   = field(default_factory=time.time)
    hops: int           = 0
    entanglement_id: Optional[str] = None   # set by EntangledPair

    # ── lifecycle checks ──────────────────────────────────────────────────────

    def is_expired(self) -> bool:
        return (time.time() - self.created_at) > TOKEN_EXPIRY

    def is_hop_exhausted(self) -> bool:
        return self.hops >= MAX_HOPS

    def is_collapsed(self) -> bool:
        return _registry.is_collapsed(self.token_id)

    def is_valid(self) -> bool:
        return not self.is_expired() and not self.is_hop_exhausted() and not self.is_collapsed()

    # ── the only way to get the message ──────────────────────────────────────

    def read(self) -> Optional[str]:
        """
        Attempt to read the token content.
        On success: state collapses, content returned.
        On failure: None returned (token was already read, expired, or hop-exhausted).

        This is the one-time measurement operation.
        """
        if self.is_expired():
            return None   # Token self-destructed
        if self.is_hop_exhausted():
            return None   # No-cloning violated — drop
        if not _registry.collapse(self.token_id):
            return None   # Already collapsed by another reader / entangled twin
        return self.content

    # ── routing ───────────────────────────────────────────────────────────────

    def forward(self) -> "QuantumToken":
        """
        Produce a forwarded copy for sending to the next hop.
        No-cloning: the token_id stays the same, hops increments.
        If this token is forwarded, it cannot also be read locally.
        """
        return QuantumToken(
            content=self.content,
            token_id=self.token_id,
            created_at=self.created_at,
            hops=self.hops + 1,
            entanglement_id=self.entanglement_id,
        )

    # ── wire format ───────────────────────────────────────────────────────────

    def serialise(self) -> str:
        """
        Simple pipe-delimited wire format:
        TOKEN|<id>|<entanglement_id>|<created_at>|<hops>|<content>
        """
        eid = self.entanglement_id or ""
        return f"TOKEN|{self.token_id}|{eid}|{self.created_at:.3f}|{self.hops}|{self.content}"

    @classmethod
    def deserialise(cls, raw: str) -> Optional["QuantumToken"]:
        try:
            parts = raw.split("|", 5)
            if parts[0] != "TOKEN" or len(parts) != 6:
                return None
            _, tid, eid, ts, hops, content = parts
            tok = cls(
                content=content,
                token_id=tid,
                created_at=float(ts),
                hops=int(hops),
                entanglement_id=eid or None,
            )
            if eid:
                _registry.register_entangled(eid, tid)
            return tok
        except (ValueError, IndexError):
            return None

    def __str__(self) -> str:
        age = int(time.time() - self.created_at)
        ttl = max(0, TOKEN_EXPIRY - age)
        state = "COLLAPSED" if self.is_collapsed() else ("EXPIRED" if self.is_expired() else "LIVE")
        return (
            f"[token:{self.token_id[:8]}] "
            f"state={state} hops={self.hops}/{MAX_HOPS} "
            f"ttl={ttl}s  '{self.content}'"
        )


# ── EntangledPair ──────────────────────────────────────────────────────────────

class EntangledPair:
    """
    Two QuantumTokens sharing the same entanglement_id.

    When EITHER token is read(), the TokenRegistry collapses BOTH.
    This models quantum entanglement: the act of measuring one particle
    instantly determines the state of its partner, no matter the distance.

    Use case: send one copy now, hold the other as a backup.
    If the first arrives and is read, the backup self-destructs.
    This prevents replay attacks without a shared secret.
    """

    def __init__(self, content: str):
        self.entanglement_id = str(uuid.uuid4())
        self.alpha = QuantumToken(
            content=content,
            entanglement_id=self.entanglement_id,
        )
        self.beta = QuantumToken(
            content=content,
            token_id=str(uuid.uuid4()),   # distinct ID, same entanglement group
            entanglement_id=self.entanglement_id,
        )
        _registry.register_entangled(self.entanglement_id, self.alpha.token_id)
        _registry.register_entangled(self.entanglement_id, self.beta.token_id)

    def __str__(self) -> str:
        return (
            f"[entangled:{self.entanglement_id[:8]}]  "
            f"α={self.alpha.token_id[:8]}  β={self.beta.token_id[:8]}"
        )
