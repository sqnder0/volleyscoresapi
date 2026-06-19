from fastapi import FastAPI
from scraper import search, get_club, get_team

app = FastAPI(
    title="Volleyscoresapi",
    description="REST API wrapper for Belgian volleyball data from volleyscores.be",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

@app.get("/api/search", tags=["search"])
def search_all(q: str):
    return search(q)


@app.get("/api/search/club", tags=["search"])
def search_club(q: str):
    return search(q, "club")


@app.get("/api/search/team", tags=["search"])
def search_team(q: str):
    return search(q, "ploeg")


@app.get("/api/get/club", tags=["club"])
def get_club_endpoint(club_label: str, club_id: int):
    return get_club(club_label, club_id)


@app.get("/api/get/team", tags=["team"])
def get_team_endpoint(label: str, team_id: int):
    return get_team(label, team_id)