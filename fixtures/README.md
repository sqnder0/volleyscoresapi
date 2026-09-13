# Fixtures

Real responses from volleyscores.be, saved for `tests_fixtures.py` (the
fast, network-free test suite). Regenerate them if volleyscores.be's markup
changes and the live suite (`tests.py`) starts failing:

```bash
source venv/bin/activate
python3 -c "
import requests

r = requests.get('https://www.volleyscores.be/index.php', params={
    'v': 2, 'lng': 'nl', 'a': 'ac', 'se': 13, 'query': 'Mendo Booischot',
}, timeout=10)
open('fixtures/search_response.json', 'w').write(r.text)

r = requests.get('https://www.volleyscores.be/index.php', params={
    'v': '2', 'ss': '0', 'isActiveSeason': '1', 't': 'Ploeg Mendo Booischot A',
    'a': 't', 'se': '13', 'ti': '101645', 'lng': 'nl',
}, timeout=10)
open('fixtures/team_page.html', 'w').write(r.text)

r = requests.get('https://www.volleyscores.be/index.php', params={
    'v': '2', 'isActiveSeason': '1', 't': 'Club Mendo Booischot', 'a': 'cc',
    'se': '13', 'ci': '10911', 'lng': 'nl',
}, timeout=10)
open('fixtures/club_page.html', 'w').write(r.text)
"
```

`team_page.html` is specifically "Mendo Booischot A" (team_id 101645) because
its page carries three `table.table` elements with identical headers (a
"matches this week" widget plus the real full-season schedule) - the exact
shape that caused the "only one match ever loads" bug, so it's worth keeping
this team as the fixture rather than a simpler page.
