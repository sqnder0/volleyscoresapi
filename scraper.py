from playwright.sync_api import sync_playwright
from typing import Literal
import json

def search(q:str, search_type: Literal['club', 'reeks', 'ploeg']):
    
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Run headless browser
        page = browser.new_page()
        page.goto("https://www.volleyscores.be/", wait_until="networkidle")
        
        cookie = page.locator("#cookieChecker")
        if cookie.is_visible():
            cookie.get_by_role("button", name="Akkoord", exact=True).click()
        
        page.fill("#searcher", q)
        
        suggestions = page.locator("div.autocomplete-suggestions > div")
        target = suggestions.filter(has_text=search_type).first
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
            
        browser.close()

    return json.dumps(result)
