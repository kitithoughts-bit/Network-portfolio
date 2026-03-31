# message_queue.py — Week 8: Opportunistic Routing
# ============================================================
# A thread-safe message queue with TTL and attempt tracking.
# Messages that exceed MAX_ATTEMPTS or have expired TTL are dropped.
# ============================================================

import threading
import time
import uuid
from dataclasses import dataclass, field
from config import MESSAGE_TTL, MAX_ATTEMPTS


@dataclass
class Message:
    content: str
    destination: int | None      # None = deliver to any candidate (epidemic)
    msg_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    created_at: float = field(default_factory=time.time)
    attempts: int = 0

    def is_expired(self) -> bool:
        if MESSAGE_TTL <= 0:
            return False
        return (time.time() - self.created_at) > MESSAGE_TTL

    def is_exhausted(self) -> bool:
        if MAX_ATTEMPTS <= 0:
            return False
        return self.attempts >= MAX_ATTEMPTS

    def should_drop(self) -> bool:
        return self.is_expired() or self.is_exhausted()

    def __str__(self):
        age = int(time.time() - self.created_at)
        return (
            f"[msg:{self.msg_id}] "
            f"dest={self.destination} "
            f"attempts={self.attempts} "
            f"age={age}s  "
            f"'{self.content}'"
        )


class MessageQueue:
    """
    FIFO queue of Message objects.
    Automatically purges expired / exhausted messages on iteration.
    """

    def __init__(self):
        self._queue: list[Message] = []
        self._lock = threading.Lock()
        self._delivered: list[str] = []   # IDs of successfully delivered msgs

    def enqueue(self, content: str, destination: int | None = None) -> Message:
        msg = Message(content=content, destination=destination)
        with self._lock:
            self._queue.append(msg)
        return msg

    def mark_delivered(self, msg_id: str):
        with self._lock:
            self._delivered.append(msg_id)
            self._queue = [m for m in self._queue if m.msg_id != msg_id]

    def get_pending(self) -> list[Message]:
        """Return messages that are still live (not expired/exhausted)."""
        with self._lock:
            live, dead = [], []
            for msg in self._queue:
                if msg.msg_id in self._delivered:
                    continue
                if msg.should_drop():
                    dead.append(msg)
                else:
                    live.append(msg)
            # Purge dead messages
            self._queue = [m for m in self._queue if m not in dead]
        return live

    def increment_attempts(self, msg_id: str):
        with self._lock:
            for msg in self._queue:
                if msg.msg_id == msg_id:
                    msg.attempts += 1
                    break

    def size(self) -> int:
        with self._lock:
            return len(self._queue)

    def stats(self) -> dict:
        with self._lock:
            return {
                "queued":    len(self._queue),
                "delivered": len(self._delivered),
            }
