import unittest
from scraper import search

class TestScraper(unittest.TestCase):
    def test_search(self):
        self.assertEqual(search("kreg", "club")["id"], "VB-1849")
        self.assertEqual(search("VB-1849", "club")["president"], "Wim De Houwer")
        
if __name__ == "__main__":
    unittest.main()