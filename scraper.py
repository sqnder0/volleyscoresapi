from typing import Literal
from urllib.parse import urlencode
from datetime import date
import re
from bs4 import BeautifulSoup
import requests


def current_season_year(today: date | None = None) -> int:
    """The site's season year rolls over on June 1st, not January 1st."""
    today = today or date.today()
    if (today.month, today.day) >= (6, 1):
        return today.year
    return today.year - 1


def get_se(season: int | None = None) -> int:
    if season:
        return season - 2013
    return current_season_year() - 2013


def get_base(s: int | None = None):
    base = f"https://www.volleyscores.be/history/{s}/index.php" if s else "https://www.volleyscores.be/index.php"
    return base

# TODO: Add a custom club, reeks and ploeg class that can be jsonified.
def search(q: str, search_type: Literal["club", "ploeg"] | None = None, season: int | None = None):
    r = requests.get(
        get_base(season),
        params={
            "v": 2,
            "lng": "nl",
            "a": "ac",
            "se": get_se(season),
            "query": q,
        },
        timeout=10,
    )

    r.raise_for_status()
    data = r.json()
    
    clubs = []
    teams = []
    
    for item in data["suggestions"]:
        if item["data"]["category"] == "Clubs":
            club = {
                "label": item["value"],
                "club_code": item["value"].split(" ")[0],
                "club_id": item["data"]["fields"]["ci"],
                "name": " ".join(item["value"].split(" ")[1:]),
            }
            clubs.append(club)
        if item["data"]["category"] == "Ploegen":
            team = {
                "label": item["value"],
                "league_id": item["value"].split(" ")[0],
                "team_id": item["data"]["fields"]["ti"],
                "name": " ".join(item["value"].split(" ")[2:]),
            }
            teams.append(team)
            
    if search_type == "club":
        return clubs
    
    if search_type == "ploeg":
        return teams
    
    return {
            "clubs": clubs,
            "teams": teams,
        }


def get_club(label: str, club_id: int , season: int | None = None):
    base = get_base(season)

    params = {
        "v": "2",
        "isActiveSeason": "1",
        "t": f"Club {label}",
        "a": "cc",
        "se": str(get_se(season)),
        "ci": str(club_id),
        "lng": "nl",
    }

    r = requests.get(
        f"{base}?{urlencode(params)}",
        timeout=10,
    )

    r.raise_for_status()

    page = BeautifulSoup(r.text, "html.parser")

    result = {
        "name": None,
        "general": {},
        "competition_teams": [],
        "cup_teams": [],
    }

    title = page.find("div", class_="teamtitle")
    if title:
        result["name"] = title.get_text(strip=True)

    for section in page.find_all("div", class_="teamsubtitle"):
        section_name = section.get_text(strip=True)

        if section_name == "Algemeen":
            container = section.find_next("div", class_="col-md-4")

            if container:
                for row in container.find_all(
                    "div",
                    class_="col-xs-12",
                    recursive=False,
                ):
                    key = row.find("label")
                    value = row.find("div", class_="col-xs-9")

                    if key and value:
                        result["general"][
                            key.get_text(strip=True)
                        ] = value.get_text(" ", strip=True)

        elif section_name in {"Ploegen competitie", "Ploegen beker"}:
            table = section.find_next("table")

            if not table:
                continue

            target = (
                result["competition_teams"]
                if section_name == "Ploegen competitie"
                else result["cup_teams"]
            )

            for tr in table.select("tr"):
                serie = tr.find("td", class_="serie")
                team = tr.find("td", class_="team")

                if not serie or not team:
                    continue

                cells = tr.find_all("td", class_="hidden-xs")
                onclick = team.get("onclick")
                team_id = None

                if onclick:
                    inside = str(onclick).split("(", 1)[1].rsplit(")", 1)[0]

                    # split args more safely
                    raw_args = re.findall(r"'[^']*'|\d+", inside)

                    candidates = []

                    for a in raw_args:
                        a = a.strip("'")

                        if not a or a == "%":
                            continue

                        if a.isdigit():
                            num = int(a)

                            # heuristic filter: adjust if needed
                            if 1000 <= num <= 10_000_000:
                                candidates.append(num)

                    # pick the best candidate (usually only one)
                    if len(candidates) == 1:
                        team_id = candidates[0]

                target.append(
                    {
                        "series": serie.get_text(" ", strip=True),
                        "team": team.get_text(" ", strip=True),
                        "id": team_id,
                        "ranking": cells[2].get_text(" ", strip=True) if len(cells) > 2 else None,
                        "previous_match": cells[3].get_text(" ", strip=True) if len(cells) > 3 else None,
                        "next_match": cells[4].get_text(" ", strip=True) if len(cells) > 4 else None,
                    }
                )
    return result

def _extract_team(td):
    onclick = td.get("onclick", "")

    m = re.search(r",(\d+),'','','%'\);?$", onclick)

    return {
        "name": td.get_text(strip=True),
        "team_id": int(m.group(1)) if m else None,
    }


def _extract_onclick_id(onclick):
    """Pulls a numeric loadPage(...) argument out as its own comma-delimited
    token, quoted or not (markup is inconsistent between pages, and labels
    can contain literal parentheses so a [^)] bound doesn't work)."""
    if not onclick:
        return None
    ids = re.findall(r",\s*'?(\d{5,9})'?\s*,", str(onclick))
    return int(ids[-1]) if ids else None


def get_team(team_label: str, team_id: int , season: int | None = None):
    result = {}
    
    base = get_base(season)

    params = {
        "v": "2",
        "ss": "0",
        "isActiveSeason": "1",
        "t": f"Ploeg {team_label}",
        "a": "t",
        "se": str(get_se(season)),
        "ti": str(team_id),
        "lng": "nl",
    }

    r = requests.get(
        base,
        params=params,
        timeout=10,
    )

    r.raise_for_status()

    page = BeautifulSoup(r.text, "html.parser")
    
    name = page.find("div", class_="teamtitle")

    if name:
        name = name.get_text(strip=True)
    else:
        name = team_label

    # The site pads the title with trailing whitespace after the closing
    # ")" - anchor the scan on the last actual ")" (via rfind) rather than
    # len(name) - 1, so trailing junk after it doesn't get swallowed into
    # the league name (or the paren itself left dangling in it).
    end = name.rfind(")")
    start = None

    if end != -1:
        depth = 0
        for i in range(end, -1, -1):
            if name[i] == ")":
                depth += 1
            elif name[i] == "(":
                depth -= 1
                if depth == 0:
                    start = i
                    break

    if start is not None:
        result["league"] = name[start + 1:end].strip()
        name = name[:start].rstrip()

    name = name.removeprefix("Ploeg ").strip()
    result["name"] = name

    result["calendar"] = f"https://www.volleyscores.be/calendar/team/{team_id}"
    result["matches"] = []

    # The page can contain several table.table elements sharing identical
    # headers (e.g. a "matches this week" widget alongside the full-season
    # schedule), so header-matching alone can't tell them apart. Parse every
    # candidate and keep whichever yields the most match rows - the full
    # schedule always has more rows than a short "this week" widget.
    best_matches = []

    for table in page.select("table.table"):
        candidate_matches = []

        for tr in table.select("tr"):
            teams = tr.select("td.hidden-xs.team")

            if len(teams) != 2:
                continue

            cells = tr.find_all("td", recursive=False)

            if len(cells) < 8:
                continue

            candidate_matches.append({
                "match_code": cells[1].get_text(strip=True),
                "match_id": _extract_onclick_id(cells[1].get("onclick")),
                "day": cells[2].get_text(strip=True),
                "date": cells[3].get_text(strip=True),
                "time": cells[4].get_text(strip=True),
                "home_team": _extract_team(teams[0]),
                "away_team": _extract_team(teams[1]),
                "venue": cells[7].get_text(strip=True),
                "result": cells[8].get_text(strip=True),
            })

        if len(candidate_matches) > len(best_matches):
            best_matches = candidate_matches

    result["matches"] = best_matches

    ranking, alert_text = _parse_ranking_table(page)
    result["ranking"] = ranking
    if alert_text:
        result["alert"] = alert_text

    return result


def get_match_detail(match_code: str, match_id: int, season: int | None = None):
    """Per-set scores for a single match, via the site's undocumented
    match-detail ('md') action. match_id is the internal numeric id
    (get_team()'s matches carry it as "match_id"), not the match_code."""
    base = get_base(season)
    params = {
        "v": "2",
        "isActiveSeason": "1",
        "t": match_code,
        "a": "md",
        "se": str(get_se(season)),
        "mm": str(match_id),
        "lng": "nl",
        "w": "%",
    }

    r = requests.get(base, params=params, timeout=10)
    r.raise_for_status()

    if "error, match not found" in r.text.lower():
        return None

    page = BeautifulSoup(r.text, "html.parser")
    result = {"match_code": match_code, "result": None, "sets": []}

    score_el = page.select_one(".alert-score .h4 strong")
    if score_el:
        result["result"] = score_el.get_text(strip=True)

    for row in page.select(".alert-score .row"):
        label = row.find(class_="col-xs-3")
        value = row.find(class_="col-xs-9")
        if not label or not value:
            continue
        if label.get_text(strip=True).lower() != "sets":
            continue

        for part in value.get_text(strip=True).split(","):
            part = part.strip()
            if "/" not in part:
                continue
            home_str, away_str = part.split("/", 1)
            try:
                result["sets"].append(
                    {"home": int(home_str), "away": int(away_str)}
                )
            except ValueError:
                continue
        break

    return result


def _parse_ranking_table(page: BeautifulSoup):
    """Shared table-parsing logic for the ranking table (table.table with
    'Ploeg'/'Ptn' headers). Used by get_team()."""
    ranking = []

    alert = page.find("div", class_="alert")
    if alert:
        if "niet beschikbaar" in alert.text.lower():
            return ranking, alert.get_text(" ", strip=True)
        else:
            alert = alert.get_text(strip=True)

    for table in page.select("table.table"):
        headers = [
            th.get_text(" ", strip=True) for th in table.select("thead tr.hidden-xs th")
        ]

        if "Ploeg" not in headers or "Ptn" not in headers:
            continue

        for row in table.select("tbody tr"):
            tds = row.select("td.hidden-xs")
            if not tds:
                continue

            cell_texts = [td.get_text(" ", strip=True) for td in tds]

            team_td = row.select_one("td.hidden-xs.team")
            team_id = _extract_onclick_id(team_td.get("onclick") if team_td else None)

            try:
                entry = {
                    "position": cell_texts[0].rstrip("."),
                    "team": cell_texts[1],
                    "team_id": team_id,
                    "points": int(cell_texts[2]),
                    "played": int(cell_texts[3]),
                    "won_3_0_3_1": int(cell_texts[4]),
                    "won_3_2": int(cell_texts[5]),
                    "lost_3_0_3_1": int(cell_texts[6]),
                    "lost_3_2": int(cell_texts[7]),
                    "sets_won": int(cell_texts[8]),
                    "sets_lost": int(cell_texts[9]),
                    "forfeits": int(cell_texts[10]) if len(cell_texts) > 10 else 0,
                }
            except (ValueError, IndexError):
                entry = cell_texts

            ranking.append(entry)

        if ranking:
            break

    return ranking, alert
