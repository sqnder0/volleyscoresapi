"""Fast, network-free tests: real HTML/JSON responses saved under fixtures/,
replayed through scraper.py's actual request layer via a mocked session
get(). Unlike tests.py (which hits volleyscores.be live and is the better
signal for "did the site's markup change"), this suite runs in CI on every
push without depending on the network or the site being up.

Fixtures were captured from real responses - see fixtures/README.md for how
to refresh them if volleyscores.be's markup changes.
"""
import json
import unittest
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from unittest.mock import patch

import scraper
from scraper import search, get_club, get_team

FIXTURES = Path(__file__).parent / "fixtures"


class _FakeResponse:
    def __init__(self, text):
        self.text = text
        self.status_code = 200

    def raise_for_status(self):
        pass

    def json(self):
        return json.loads(self.text)


def _fake_get(url, params=None, timeout=None):
    # get_club() bakes its params into the URL query string instead of
    # passing them separately, so the action code has to be read from
    # whichever one actually carries it.
    if params:
        action = params.get("a")
    else:
        action = parse_qs(urlparse(url).query).get("a", [None])[0]

    if action == "ac":
        return _FakeResponse((FIXTURES / "search_response.json").read_text())
    if action == "t":
        return _FakeResponse((FIXTURES / "team_page.html").read_text())
    if action == "cc":
        return _FakeResponse((FIXTURES / "club_page.html").read_text())
    raise AssertionError(f"no fixture for action={action!r}")


@patch("scraper._session.get", side_effect=_fake_get)
class TestSearchFixture(unittest.TestCase):
    def test_search_returns_clubs_and_teams(self, mock_get):
        result = search("Mendo Booischot")
        self.assertIn("clubs", result)
        self.assertIn("teams", result)
        self.assertTrue(len(result["clubs"]) > 0)
        self.assertTrue(len(result["teams"]) > 0)


@patch("scraper._session.get", side_effect=_fake_get)
class TestGetClubFixture(unittest.TestCase):
    # get_club() is wrapped in a short-TTL cache keyed on (club_id, se) -
    # clear it before each test so one test's result can't leak into
    # another's and mask a call to the (mocked) session that should have
    # happened.
    def setUp(self):
        scraper._club_cache.clear()

    def test_get_club_returns_teams(self, mock_get):
        club = get_club("Mendo Booischot", 10911)
        self.assertIn("Mendo Booischot", club["name"])
        self.assertTrue(len(club["competition_teams"]) > 0)

    def test_second_call_within_ttl_is_served_from_cache(self, mock_get):
        get_club("Mendo Booischot", 10911)
        get_club("Mendo Booischot", 10911)
        self.assertEqual(mock_get.call_count, 1)

    def test_team_next_match_is_structured_not_a_text_blob(self, mock_get):
        club = get_club("Mendo Booischot", 10911)
        team = next(
            t for t in club["competition_teams"] if t["team"] == "Mendo Booischot A"
        )
        self.assertEqual(
            team["next_match"],
            {
                "date": "20/09/2026",
                "time": "17:00",
                "home_team": "Volley Noorderkempen A",
                "away_team": "Mendo Booischot A",
                "result": "",
            },
        )

    def test_previous_match_carries_a_result(self, mock_get):
        club = get_club("Mendo Booischot", 10911)
        team = next(
            t for t in club["competition_teams"] if t["team"] == "Mendo Booischot A"
        )
        self.assertEqual(team["previous_match"]["result"], "0 - 3")

    def test_missing_previous_match_is_none(self, mock_get):
        club = get_club("Mendo Booischot", 10911)
        team = next(
            t for t in club["competition_teams"] if t["team"] == "Mendo Booischot D"
        )
        self.assertIsNone(team["previous_match"])


@patch("scraper._session.get", side_effect=_fake_get)
class TestGetTeamFixture(unittest.TestCase):
    """Regression coverage for the two bugs fixed in this session, replayed
    against a saved copy of the exact page that exposed them."""

    def setUp(self):
        scraper._team_cache.clear()

    def test_returns_full_schedule_not_just_this_week(self, mock_get):
        team = get_team("Mendo Booischot A", 101645)
        self.assertGreater(len(team["matches"]), 10)

    def test_league_name_has_no_stray_closing_paren(self, mock_get):
        team = get_team("Mendo Booischot A", 101645)
        self.assertNotIn(")", team["league"])
        self.assertNotIn("(", team["league"])

    def test_second_call_within_ttl_is_served_from_cache(self, mock_get):
        get_team("Mendo Booischot A", 101645)
        get_team("Mendo Booischot A", 101645)
        self.assertEqual(mock_get.call_count, 1)

    def test_different_team_id_is_not_served_from_cache(self, mock_get):
        get_team("Mendo Booischot A", 101645)
        get_team("Mendo Booischot B", 105848)
        self.assertEqual(mock_get.call_count, 2)

    def test_ranking_is_a_flat_list_of_dicts(self, mock_get):
        team = get_team("Mendo Booischot A", 101645)
        ranking = team["ranking"]
        self.assertIsInstance(ranking, list)
        self.assertTrue(len(ranking) > 0)
        for row in ranking:
            self.assertIsInstance(row, dict)


if __name__ == "__main__":
    unittest.main()
