import json
from sqlalchemy import column
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Club(Base):
    __table__ = "clubs"
    
    vb_id = Column("id", Integer, primary_key=True)
    name = Column(String)
    president = Column(String)
    secretary = Column(String)
    website = Column(String)
    
    def __init__(self, vb_id:str,
                 name=None, president=None,
                 secretary=None,
                 website=None,
                 competition_teams=None,
                 cup_teams=None):
        """
        Initialize a Club instance.

        Parameters
        ----------
        vb_id : str
            Unique club identifier (vb id).
        name : str or None, optional
            Club name.
        president : str or None, optional
            Name of the club president.
        secretary : str or None, optional
            Name of the club secretary.
        website : str or None, optional
            Club website URL.
        competition_teams : list or None, optional
            List of competition teams (default: None).
        cup_teams : list or None, optional
            List of cup teams (default: None).

        Notes
        -----
        Optional parameters after `vb_id` may be provided positionally
        or by keyword when calling the constructor or `from_dict`.
        """
        self.id = vb_id
        self.name = name
        self.president = president
        self.secretary = secretary
        self.website = website
        self.competition_teams = competition_teams
        self.cup_teams = cup_teams
        
    def __repr__(self):
        return self.name
    
    @classmethod
    def from_dict(cls, data:dict):
        return cls(
            data["id"],
            data.get("name"),
            data.get("president"),
            data.get("secretary"),
            data.get("website"),
            data.get("competition_teams", []),
            data.get("cup_teams", []),
        )
        
    @classmethod
    def from_json(cls, data:str):
        try:
            data_dict = json.loads(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid json string: {e}")
        
        return cls.from_dict(data_dict)
    

    
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
    
    def save():
    