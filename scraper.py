from playwright.sync_api import sync_playwright, expect
from playwright.sync_api import Locator
from typing import Literal
from urllib.parse import urlencode
import re
from bs4 import BeautifulSoup
import requests

# Toggle for debug purposes
HEADLESS=False
CURRENT_SE = 13

def get_se(season: int | None):
    if season:
        return season - 2013
    else:
        return CURRENT_SE


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
            "se": 13,
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
        "se": "13",
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


def get_team(team_label: str, team_id: int , season: int | None = None):
    result = {}
    
    base = get_base(season)

    params = {
        "v": "2",
        "ss": "0",
        "isActiveSeason": "1",
        "t": f"Ploeg {team_label}",
        "a": "t",
        "se": "13",
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
        name = name.get_text()
    else:
        name = team_label
    

    depth = 0
    start = None

    for i in range(len(name) - 1, -1, -1):
        if name[i] == ")":
            depth += 1
        elif name[i] == "(":
            depth -= 1
            if depth == 0:
                start = i
                break

    if start is not None:
        result["league"] = name[start + 1:-1].strip()
        name = name[:start].rstrip()

    name = name.removeprefix("Ploeg ").strip()
    result["name"] = name

    result["calendar"] = f"https://www.volleyscores.be/calendar/team/{team_id}"
    result["matches"] = []
    
    table = page.select_one("table.table")

    if not table:
        return result

    for tr in table.select("tr"):
        teams = tr.select("td.hidden-xs.team")

        if len(teams) != 2:
            continue

        cells = tr.find_all("td", recursive=False)

        if len(cells) < 8:
            continue

        result["matches"].append({
            "match_code": cells[1].get_text(strip=True),
            "day": cells[2].get_text(strip=True),
            "date": cells[3].get_text(strip=True),
            "time": cells[4].get_text(strip=True),
            "home_team": _extract_team(teams[0]),
            "away_team": _extract_team(teams[1]),
            "venue": cells[7].get_text(strip=True),
            "result": cells[8].get_text(strip=True),
        })

    result["ranking"] = _parse_ranking_table(page)
    
    return result


def get_league(q: str, season: int | None = None):
    se = get_se(season) if season else get_se(2026)

    r = requests.get(
        get_base(),
        params={"v": 2, "lng": "nl", "a": "ac", "se": se, "query": q},
        timeout=10,
    )
    r.raise_for_status()
    data = r.json()
    league = None

    for item in data["suggestions"]:
        if item["data"]["category"] == "Reeksen":
            league = {
                "label": item["value"],
                "league_id": item["data"]["fields"]["ssi"],
            }

    if league is None:
        return None

    # Fetch the ranking page — same endpoint/table markup get_ranking() uses —
    # and attach the parsed ranking to this league.
    base = get_base()
    params = {
        "v": "2", "ss": "0", "isActiveSeason": "1",
        "t": league["label"], "a": "sd", "se": se,
        "ssi": str(league["league_id"]), "st": "%", "w": "%", "lng": "nl",
    }

    r = requests.get(base, params=params, timeout=10)
    r.raise_for_status()
    page = BeautifulSoup(r.text, "html.parser")

    ranking, alert_text = _parse_ranking_table(page)
    league["ranking"] = ranking
    if alert_text:
        league["alert"] = alert_text

    return league

def get_ranking(series_label: str, league_id, season: int = 2026):
    se = get_se(season)

    if league_id is None:
        league = get_league(series_label, season=season)
        if league is None or league.get("label", "").lower() != series_label.lower():
            return None
        series_id = league["league_id"]
    else:
        series_id = league_id

    base = get_base()
    params = {
        "v": "2", "ss": "0", "isActiveSeason": "1",
        "t": series_label, "a": "sd", "se": se,
        "ssi": str(series_id), "st": "%", "w": "%", "lng": "nl",
    }

    r = requests.get(base, params=params, timeout=10)
    r.raise_for_status()
    page = BeautifulSoup(r.text, "html.parser")

    result = {"series": series_label, "series_id": series_id, "ranking": []}
    ranking, alert_text = _parse_ranking_table(page)
    result["ranking"] = ranking
    if alert_text:
        result["alert"] = alert_text

    return result

def _parse_ranking_table(page: BeautifulSoup):
    """Shared table-parsing logic for the ranking table (table.table with
    'Ploeg'/'Ptn' headers). Used by both get_ranking() and get_league()."""
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
            team_id = None
            if team_td and team_td.has_attr("onclick"):
                m = re.search(r"loadPage\([^)]*?'(\d+)'[^)]*\)", str(team_td["onclick"]))
                if m:
                    team_id = int(m.group(1))

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