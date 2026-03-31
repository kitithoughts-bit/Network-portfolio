# message_queue.py — Week 9: Bio-Inspired Networking
# ============================================================
# Identical lifecycle model as Week 8 (TTL + max-attempts),
# but messages now carry a "hops" counter so multi-hop
# propagation can be visualised.
# ============================================================

import threading
import time
import uuid
from dataclasses import dataclass, field

from config import MESSAGE_TTL, MAX_ATTEMPTS


@dataclass
class Message:
    content: str
    destination: int | None        # None = epidemic (all peers)
    msg_id: str   = field(default_factory=lambda: str(uuid.uuid4())[:8])
    created_at: float = field(default_factory=time.time)
    attempts: int = 0
    hops: int = 0                  # incremented each time the message is forwarded

    def is_expired(self) -> bool:
        return MESSAGE_TTL > 0 and (time.time() - self.created_at) > MESSAGE_TTL

    def is_exhausted(self) -> bool:
        return MAX_ATTEMPTS > 0 and self.attempts >= MAX_ATTEMPTS

    def should_drop(self) -> bool:
        return self.is_expired() or self.is_exhausted()

    def __str__(self):
        age = int(time.time() - self.created_at)
        dest = f":{self.destination}" if self.destination else "epidemic"
        return (
            f"[msg:{self.msg_id}] dest={dest} "
            f"attempts={self.attempts} hops={self.hops} age={age}s  "
            f"'{self.content}'"
        )


class MessageQueue:
    def __init__(self):
        self._queue: list[Message] = []
        self._lock = threading.Lock()
        self._delivered_ids: set[str] = set()

    def enqueue(self, content: str, destination: int | None = None) -> Message:
        msg = Message(content=content, destination=destination)
        with self._lock:
            self._queue.append(msg)
        return msg

    def mark_delivered(self, msg_id: str):
        with self._lock:
            self._delivered_ids.add(msg_id)
            self._queue = [m for m in self._queue if m.msg_id != msg_id]

    def get_pending(self) -> list[Message]:
        with self._lock:
            live, dead = [], []
            for msg in self._queue:
                if msg.msg_id in self._delivered_ids:
                    continue
                (dead if msg.should_drop() else live).append(msg)
            self._queue = [m for m in self._queue if m not in dead]
        return live

    def increment_attempts(self, msg_id: str):
        with self._lock:
            for msg in self._queue:
                if msg.msg_id == msg_id:
                    msg.attempts += 1
                    break

    def increment_hops(self, msg_id: str):
        with self._lock:
            for msg in self._queue:
                if msg.msg_id == msg_id:
                    msg.hops += 1
                    break

    def stats(self) -> dict:
        with self._lock:
            return {"queued": len(self._queue), "delivered": len(self._delivered_ids)}
