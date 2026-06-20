from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from volleyscoresapi.scraper import get_club #type: ignore

if __name__ == "__main__":
    print(get_club("VB-1849 Kreg Rotselaar", 11136))
    