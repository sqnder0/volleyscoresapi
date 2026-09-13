import unittest

import scraper


class TestSessionRetryConfig(unittest.TestCase):
    """A live flaky-server test isn't practical here, so this checks the
    retry policy is actually mounted on the shared session rather than
    silently dropped by a future refactor."""

    def test_retries_are_mounted_on_both_schemes(self):
        for scheme in ("https://", "http://"):
            adapter = scraper._session.get_adapter(f"{scheme}example.com")
            retry = adapter.max_retries
            self.assertEqual(retry.total, 3)
            self.assertIn(502, retry.status_forcelist)
            self.assertIn(503, retry.status_forcelist)
            self.assertIn(504, retry.status_forcelist)

    def test_raise_on_status_is_disabled(self):
        """Regression coverage: Retry's default raise_on_status=True raises
        RetryError once retries are exhausted, which main.py's `except
        HTTPError` blocks (in the /history endpoints) don't catch - an
        unhandled RetryError would surface as a raw 500 instead of the
        intended structured error response. Disabling it lets our own
        raise_for_status() calls raise the HTTPError those blocks expect."""
        for scheme in ("https://", "http://"):
            adapter = scraper._session.get_adapter(f"{scheme}example.com")
            self.assertFalse(adapter.max_retries.raise_on_status)


if __name__ == "__main__":
    unittest.main()
