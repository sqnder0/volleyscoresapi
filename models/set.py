from typing import TYPE_CHECKING

from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db import Base

if TYPE_CHECKING:
    from match import Match


class Set(Base):
    __tablename__ = "sets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    match_id: Mapped[int] = mapped_column(
        ForeignKey("matches.id"),
        nullable=False,
        index=True
    )

    set_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    home_points: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    visitor_points: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    match: Mapped["Match"] = relationship(
        "Match",
        back_populates="sets"
    )