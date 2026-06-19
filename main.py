from fastapi import FastAPI, Request, status, HTTPException
from scraper import get, search, get_club, get_team

app = FastAPI()

@app.get("/api/get/club")
def parse_club(club_label: str, club_id):
    response = get_club(club_label, club_id)
    
    return response

@app.get("/api/search")
def search_for_query(q: str):
    return search(q)

@app.get("/api/search/club")
def search_for_club(q: str):
    return search(q, "club")

@app.get("/api/search/team")
def search_for_team(q: str):
    return search(q, "ploeg")

@app.get("/api/get/team")
def parse_team(label: str, team_id: int):
    return get_team(label, team_id)