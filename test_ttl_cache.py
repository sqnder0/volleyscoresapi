import time
import unittest

from ttl_cache import TTLCache


class TestTTLCache(unittest.TestCase):
    def test_get_returns_none_for_missing_key(self):
        cache = TTLCache(ttl_seconds=60)
        self.assertIsNone(cache.get("missing"))

    def test_set_then_get_returns_the_value(self):
        cache = TTLCache(ttl_seconds=60)
        cache.set("a", {"foo": "bar"})
        self.assertEqual(cache.get("a"), {"foo": "bar"})

    def test_entry_expires_after_its_ttl(self):
        cache = TTLCache(ttl_seconds=0.05)
        cache.set("a", "value")
        self.assertEqual(cache.get("a"), "value")

        time.sleep(0.1)

        self.assertIsNone(cache.get("a"))

    def test_clear_removes_every_entry(self):
        cache = TTLCache(ttl_seconds=60)
        cache.set("a", "1")
        cache.set("b", "2")

        cache.clear()

        self.assertIsNone(cache.get("a"))
        self.assertIsNone(cache.get("b"))

    def test_keys_are_independent(self):
        cache = TTLCache(ttl_seconds=60)
        cache.set(("team", 1), "team-1")
        cache.set(("club", 1), "club-1")

        self.assertEqual(cache.get(("team", 1)), "team-1")
        self.assertEqual(cache.get(("club", 1)), "club-1")


if __name__ == "__main__":
    unittest.main()
