from playwright.sync_api import sync_playwright, expect
from playwright.sync_api import Locator
from typing import Literal
import re
import json
import requests

# Toggle for debug purposes
HEADLESS=False

# TODO: Add a custom club, reeks and ploeg class that can be jsonified.
# TODO: Just return a list of possibilities if multiple possible results.
def get(q:str, search_type: Literal['club', 'ploeg']) -> dict:
    """
    Use the search box on volleyscores
    Args:
        q (str): Your query
        search_type (Literal['club', 'reeks', 'ploeg']): Type of search - 'club', 'reeks', or 'ploeg'
    Returns:
        dict: A list of all options if multiple, the first option if only one.
    """
    
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)  # Run headless browser
        page = browser.new_page()
        page.goto("https://www.volleyscores.be/", wait_until="networkidle")
        
        cookie = page.locator("#cookieChecker")
        if cookie.is_visible():
            cookie.get_by_role("button", name="Akkoord", exact=True).click()
        
        page.fill("#searcher", q)
        
        section_labels = {
            "club": "Clubs",
            "reeks": "Reeksen",
            "ploeg": "Ploegen",
        }

        suggestions = page.locator("div.autocomplete-suggestions > div")
        target = suggestions.filter(has_text=section_labels[search_type]).first
        target.wait_for()

        next_div = target.locator("xpath=following-sibling::div[1]")
        next_div.wait_for(state="visible")
        next_div.click()

        # Wait for page to load
        page.wait_for_function("""
        () => document.querySelector('.gts.t')?.value?.trim().length > 0
        """)
        
        result = {}
        
        if search_type == "club":
            result["name"] = page.locator(".teamtitle").inner_text()
            result["id"] = result["name"].split(" ")[1]
            
            info_rows = page.locator("#reqContent .col-md-4 .col-xs-12")
            for i in range(info_rows.count()):
                row = info_rows.nth(i)
                label = row.locator("label").inner_text().strip()
                value = row.locator(".col-xs-9").inner_text().strip()

                if label == "Voorzitter":
                    result["president"] = value
                elif label == "Secretaris":
                    result["secretary"] = value
                elif label == "Website":
                    result["website"] = row.locator("a").get_attribute("href")

            result["competition_teams"] = []
            result["cup_teams"] = []
            
            tables = page.locator("#reqContent table")
            
            if tables.count() > 0:
                competition_rows = tables.nth(0).locator("tbody tr")
                for i in range(competition_rows.count()):
                    row = competition_rows.nth(i)
                    result["competition_teams"].append({
                        "series": row.locator(".hidden-xs.serie").inner_text().strip(),
                        "team": row.locator(".hidden-xs.team").inner_text().strip(),
                        "next_match": row.locator(".hidden-xs").nth(4).inner_text().strip(),
                    })
            if tables.count() > 1:
                cup_rows = tables.nth(1).locator("tbody tr")
                for i in range(cup_rows.count()):
                    row = cup_rows.nth(i)
                    result["cup_teams"].append({
                        "series": row.locator(".hidden-xs.serie").inner_text().strip(),
                        "team": row.locator(".hidden-xs.team").inner_text().strip(),
                        "next_match": row.locator(".hidden-xs").nth(4).inner_text().strip(),
                    })
        if search_type == "ploeg":
            title = page.locator('.teamtitle').inner_text().strip()
            if title.lower().startswith('ploeg '):
                title = title[len('Ploeg '):].strip()

            series = ''
            m = re.search(r"\(([^)]+)\)", page.locator('.teamtitle').inner_text() or '')
            if m:
                series = m.group(1).strip()

            team_id = page.locator('input.gts[data-gt="ti"]').get_attribute('value')

            result['team_name'] = title
            result['series'] = series
            result['team_id'] = team_id

            result['matches'] = []

            def _parse_loadpage_args(onclick) -> list:
                if not onclick:
                    return []
                inside = onclick[onclick.find('(') + 1: onclick.rfind(')')]
                tokens = re.findall(r"'([^']*)'|(\d+)", inside)
                return [a if a else b for a, b in tokens]

            rows = page.locator('#reqContent table tbody tr')
            for i in range(rows.count()):
                row = rows.nth(i)

                match_cell = row.locator('td.hidden-xs.match[onclick]').first

                if match_cell.count() == 0:
                    continue

                code = match_cell.inner_text().strip()
                onclick = match_cell.get_attribute('onclick')

                if not onclick:
                    continue

                args = _parse_loadpage_args(onclick)


                hidden_cells = row.locator('td.hidden-xs')
                day = date = time = home = visitors = sporthal = result_text = sets = ''
                try:
                    if hidden_cells.count() > 1:
                        day = hidden_cells.nth(1).inner_text().strip()
                        date = hidden_cells.nth(2).inner_text().strip()
                        time = hidden_cells.nth(3).inner_text().strip()
                        home = hidden_cells.nth(4).inner_text().strip()
                        if hidden_cells.count() > 5:
                            visitors = hidden_cells.nth(5).inner_text().strip()
                        if hidden_cells.count() > 6:
                            sporthal = hidden_cells.nth(6).inner_text().strip()
                        if hidden_cells.count() > 7:
                            result_text = hidden_cells.nth(7).inner_text().strip()
                        if hidden_cells.count() > 8:
                            sets = hidden_cells.nth(8).inner_text().strip()
                except Exception:
                    pass

                match_id = None
                sporthall_id = None
                try:
                    if len(args) > 7 and args[7].isdigit():
                        match_id = args[7]
                    if len(args) > 8 and args[8].isdigit():
                        sporthall_id = args[8]
                except Exception:
                    pass

                sporthal_cell = row.locator('td.sporthal')
                if sporthal_cell.count() > 0:
                    sh_onclick = sporthal_cell.nth(0).get_attribute('onclick')
                    sh_args = _parse_loadpage_args(sh_onclick)
                    try:
                        for token in reversed(sh_args):
                            if token.isdigit():
                                sporthall_id = token
                                break
                    except Exception:
                        pass

                result['matches'].append({
                    'code': code,
                    'day': day,
                    'date': date,
                    'time': time,
                    'home': home,
                    'visitors': visitors,
                    'sporthal': sporthal,
                    'match_id': match_id,
                    'sporthall_id': sporthall_id,
                    'result': result_text,
                    'sets': sets,
                })
            
        browser.close()

    return result


def search(q: str, search_type: Literal["club", "ploeg"] | None = None):
    r = requests.get(
        "https://www.volleyscores.be/index.php",
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
                "club_id": item["value"].split(" ")[0],
                "name": " ".join(item["value"].split(" ")[1:]),
            }
            clubs.append(club)
        if item["data"]["category"] == "Ploegen":
            team = {
                "label": item["value"],
                "league_id": item["value"].split(" ")[0],
                "name": " ".join(item["value"].split(" ")[2:]),
            }
            teams.append(team)
            
    if search_type == "club":
        return clubs
    
    if search_type == "team":
        return teams
    
    return {
            "clubs": clubs,
            "teams": teams,
        }

