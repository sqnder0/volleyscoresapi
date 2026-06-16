from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db import Base

if TYPE_CHECKING:
    from team import Team
    from set import Set


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    match_nr: Mapped[str] = mapped_column(String, nullable=False)

    date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)

    home_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id"),
        nullable=False,
        index=True
    )

    visitor_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id"),
        nullable=False,
        index=True
    )

    home_team: Mapped["Team"] = relationship(
        "Team",
        foreign_keys=[home_id],
        back_populates="home_matches"
    )

    visitor_team: Mapped["Team"] = relationship(
        "Team",
        foreign_keys=[visitor_id],
        back_populates="visitor_matches"
    )

    hall: Mapped[str] = mapped_column(String, nullable=False)

    sets: Mapped[list["Set"]] = relationship(
        "Set",
        back_populates="match",
        cascade="all, delete-orphan"
    )