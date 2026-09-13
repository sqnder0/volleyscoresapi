import unittest

from scraper import search, get_club, get_team, get_match_detail


class TestSearch(unittest.TestCase):
    def test_search_club(self):
        clubs = search("Mendo Booischot", "club")
        self.assertIsInstance(clubs, list)
        self.assertTrue(any(c["name"] == "Mendo Booischot" for c in clubs))

    def test_search_team(self):
        teams = search("Mendo Booischot A", "ploeg")
        self.assertIsInstance(teams, list)
        self.assertTrue(len(teams) > 0)
        self.assertIn("team_id", teams[0])


class TestGetClub(unittest.TestCase):
    def test_get_club_returns_teams(self):
        club = get_club("Mendo Booischot", 10911)
        self.assertIn("Mendo Booischot", club["name"])
        self.assertTrue(len(club["competition_teams"]) > 0)
        first = club["competition_teams"][0]
        self.assertIn("series", first)
        self.assertIn("team", first)


class TestGetTeam(unittest.TestCase):
    """Regression coverage for the ranking bug: get_team() used to assign
    the raw (rows, alert) tuple from _parse_ranking_table() straight into
    result["ranking"], instead of unpacking it. That made the API return
    `"ranking": [[...], null]` whenever there was no alert (the common
    case), which the Flutter client couldn't parse correctly."""

    def test_ranking_is_a_flat_list_of_dicts(self):
        team = get_team("Mendo Booischot A", 101645)
        ranking = team["ranking"]

        self.assertIsInstance(ranking, list)
        self.assertTrue(len(ranking) > 0)
        for row in ranking:
            self.assertIsInstance(row, dict)
            self.assertIn("team", row)
            self.assertIn("points", row)

    def test_ranking_rows_carry_team_id_where_clickable(self):
        team = get_team("Mendo Booischot A", 101645)
        ranking = team["ranking"]

        # At least one *other* team in the ranking table should resolve to
        # a real numeric team_id (the site doesn't link the row for the
        # team whose page you're already on, so that one row is None).
        ids = [row["team_id"] for row in ranking if row["team"] != "Mendo Booischot A"]
        self.assertTrue(any(ids), "expected at least one non-null team_id in the ranking table")

    def test_matches_have_home_and_away_team_ids(self):
        team = get_team("Mendo Booischot A", 101645)
        self.assertTrue(len(team["matches"]) > 0)
        match = team["matches"][0]
        self.assertIsNotNone(match["home_team"]["team_id"])
        self.assertIsNotNone(match["away_team"]["team_id"])

    def test_matches_have_match_id(self):
        team = get_team("Mendo Booischot A", 101645)
        match = team["matches"][0]
        self.assertIsNotNone(match["match_id"])

    def test_league_name_has_no_stray_closing_paren(self):
        """Regression coverage: the site pads the team title with a
        trailing space after the closing ")" (e.g. "... (Nationale 1
        Heren) "). get_team() sliced off what it assumed was that trailing
        ")" with name[start + 1:-1], but with the extra space that slice
        cut the space instead and left the ")" stuck onto the league name
        (rendered everywhere as a league badge in the Flutter app)."""
        team = get_team("Mendo Booischot A", 101645)
        self.assertNotIn(")", team["league"])
        self.assertNotIn("(", team["league"])

    def test_returns_full_schedule_not_just_this_week(self):
        """Regression coverage: the team page can carry several table.table
        elements with identical headers - a small "matches this week" widget
        (a handful of rows) alongside the real full-season schedule (dozens
        of rows). get_team() used to blindly take the first table.table on
        the page, which was the "this week" widget, so it silently returned
        only 1-3 matches instead of the full schedule."""
        team = get_team("Caruur Volley Gent B", 100074)
        self.assertGreater(len(team["matches"]), 10)


class TestGetMatchDetail(unittest.TestCase):
    def test_played_match_has_sets(self):
        team = get_team("Caruur Volley Gent B", 100074)
        played = [m for m in team["matches"] if m["result"]]
        self.assertTrue(len(played) > 0, "expected at least one played match")

        match = played[0]
        detail = get_match_detail(match["match_code"], match["match_id"])

        self.assertIsNotNone(detail)
        self.assertEqual(detail["result"], match["result"])
        self.assertTrue(len(detail["sets"]) > 0)
        for s in detail["sets"]:
            self.assertIn("home", s)
            self.assertIn("away", s)

    def test_unknown_match_returns_none(self):
        self.assertIsNone(get_match_detail("NAT1H-0008", 1))


if __name__ == "__main__":
    unittest.main()
