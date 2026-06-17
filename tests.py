import unittest
from scraper import search

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db import Base
from models import Club, Team, Match, Set

class TestScraper(unittest.TestCase):
    def test_search(self):
        self.assertEqual(search("kreg", "club")["id"], "VB-1849")
        self.assertEqual(search("VB-1849", "club")["president"], "Wim De Houwer")

class TestDatabaseModels(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(cls.engine)

        cls.SessionLocal = sessionmaker(bind=cls.engine)

    def setUp(self):
        self.db = self.SessionLocal()

    def tearDown(self):
        self.db.rollback()
        self.db.close()

    def test_full_relationship_graph(self):
        club = Club(
            vb_id="VB-TEST-1",
            name="Test Club",
            president="John Doe",
            secretary=None,
            website=None
        )

        team = Team(
            vb_id="VB-TEAM-1",
            name="Test Team",
            club=club
        )

        match = Match(
            match_nr="MATCH-1",
            hall="Test Hall",
            home_team=team,
            visitor_team=team
        )

        set1 = Set(
            set_number=1,
            home_points=25,
            visitor_points=20,
            match=match
        )

        set2 = Set(
            set_number=2,
            home_points=18,
            visitor_points=25,
            match=match
        )

        self.db.add(club)
        self.db.commit()

        # Reload root object
        saved_club = self.db.query(Club).filter_by(vb_id="VB-TEST-1").first()

        # ---- ASSERTIONS ----

        self.assertEqual(saved_club.name, "Test Club")

        self.assertEqual(len(saved_club.teams), 1)
        self.assertEqual(saved_club.teams[0].vb_id, "VB-TEAM-1")

        saved_team = saved_club.teams[0]

        self.assertEqual(len(saved_team.home_matches), 1)

        saved_match = saved_team.home_matches[0]

        self.assertEqual(saved_match.hall, "Test Hall")

        self.assertEqual(len(saved_match.sets), 2)

        self.assertEqual(saved_match.sets[0].home_points, 25)
        self.assertEqual(saved_match.sets[1].visitor_points, 25)

    def test_cascade_delete(self):
        club = Club(
            vb_id="VB-DEL-1",
            name="Delete Club",
            president="Test",
        )

        team = Team(
            vb_id="VB-DEL-T1",
            name="Delete Team",
            club=club
        )

        self.db.add(club)
        self.db.commit()

        self.db.delete(club)
        self.db.commit()

        team_check = self.db.query(Team).filter_by(vb_id="VB-DEL-T1").first()

        self.assertIsNone(team_check)
        
if __name__ == "__main__":
    unittest.main()