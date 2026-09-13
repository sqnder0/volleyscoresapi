import time


class TTLCache:
    """A simple in-process cache with a fixed time-to-live per entry.

    Absorbs repeated requests for the same entity within a short window -
    e.g. ClubDetailPage's pull-to-refresh fires one request per team (up to
    ~50 for a big club), and a user re-refreshing shortly after would
    otherwise re-scrape every one of those pages again.
    """

    def __init__(self, ttl_seconds: float):
        self.ttl_seconds = ttl_seconds
        self._store: dict = {}

    def get(self, key):
        entry = self._store.get(key)
        if entry is None:
            return None

        expires_at, value = entry
        if time.monotonic() >= expires_at:
            del self._store[key]
            return None

        return value

    def set(self, key, value):
        self._store[key] = (time.monotonic() + self.ttl_seconds, value)

    def clear(self):
        self._store.clear()
