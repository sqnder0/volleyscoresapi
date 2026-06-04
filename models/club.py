import json

class Club():
    def __init__(self, vb_id:str):
        self.id = vb_id
        # self.name = name
        # self.president = president
        # self.secretary = secretary
        # self.website = website
        # self.competition_teams = competition_teams
        # self.cup_teams = cup_teams
        
    def __repr__(self):
        return self.name
    
    @classmethod
    def from_dict(self, data:dict):
        return self(
            data["id"],
            data.get("name"),
            data.get("president"),
            data.get("secretary"),
            data.get("website"),
            data.get("competition_teams", []),
            data.get("cup_teams", []),
        )
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "president": self.president,
            "secretary": self.secretary,
            "website": self.website,
            "competition_teams": self.competition_teams,
            "cup_teams": self.cup_teams
        }
    
    def export(self):
        result = json.dumps(self.as_dict())
        return result
    