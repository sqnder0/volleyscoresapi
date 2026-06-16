from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db import Base

if TYPE_CHECKING:
    from club import Club
    from match import Match


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    vb_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True,
        index=True
    )

    name: Mapped[str] = mapped_column(String, nullable=False)

    club_id: Mapped[int] = mapped_column(
        ForeignKey("clubs.id"),
        nullable=False
    )

    club: Mapped["Club"] = relationship(
        "Club",
        back_populates="teams"
    )

    home_matches: Mapped[list["Match"]] = relationship(
        "Match",
        foreign_keys="Match.home_id",
        back_populates="home_team"
    )

    visitor_matches: Mapped[list["Match"]] = relationship(
        "Match",
        foreign_keys="Match.visitor_id",
        back_populates="visitor_team"
    )