from fastapi import FastAPI
from scraper import search, get_club, get_team, get_ranking
from fastapi import HTTPException
from requests.exceptions import HTTPError

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

@app.get("/api/search/history/{season}", tags=["search"])
def search_all(season: int, q: str):
    try:
        return search(q, season=season)
    except HTTPError as e:
        raise HTTPException(
            status_code=e.response.status_code if e.response else 502,
            detail=e.response.text if e.response else str(e),
        )


@app.get("/api/search/club/history/{season}", tags=["search"])
def search_club(season: int, q: str):
    try:
        return search(q, "club", season=season)
    except HTTPError as e:
        raise HTTPException(
            status_code=e.response.status_code if e.response else 502,
            detail=e.response.text if e.response else str(e),
        )


@app.get("/api/search/team/history/{season}", tags=["search"])
def search_team(season: int, q: str):
    try:
        return search(q, "ploeg", season=season)
    except HTTPError as e:
        raise HTTPException(
            status_code=e.response.status_code if e.response else 502,
            detail=e.response.text if e.response else str(e),
        )


@app.get("/api/get/club/history/{season}", tags=["club"])
def get_club_endpoint(season: int, club_label: str, club_id: int):
    try:
        return get_club(club_label, club_id, season=season)
    except HTTPError as e:
        raise HTTPException(
            status_code=e.response.status_code if e.response else 502,
            detail=e.response.text if e.response else str(e),
        )


@app.get("/api/get/team/history/{season}", tags=["team"])
def get_team_endpoint(season: int, label: str, team_id: int):
    try:
        return get_team(label, team_id, season=season)
    except HTTPError as e:
        raise HTTPException(
            status_code=e.response.status_code if e.response else 502,
            detail=e.response.text if e.response else str(e),
        )

@app.get("/api/get/league")
def get_ranking_endpoint(label: str, season: int=2026):
    result = get_ranking(label, season)
    
    if result == None:
        raise HTTPException(
            status_code=404,
            detail="League not found"
        )
    else:
        return result