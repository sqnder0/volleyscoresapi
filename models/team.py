import json
from sqlalchemy import Column, Integer, String, create_engine, Table
from sqlalchemy.orm import registry, relationship

# TODO: Finish match
class Match:
    def __init__(self, match_nr, date, home, visitors, hall:str):

# TODO; finish team init 
class Team:
    def __init__(self, team_id,):