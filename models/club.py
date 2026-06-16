from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from team import Team

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db import Base

class Club(Base):
    __tablename__ = "clubs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    vb_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True,
        index=True
    )
    name: Mapped[str] = mapped_column(String(), nullable=False)
    president: Mapped[str] = mapped_column(String(), nullable=False)
    secretary: Mapped[str | None ] = mapped_column(String(), nullable=True)
    website: Mapped[str | None] = mapped_column(String(), nullable=True)
    teams: Mapped[list["Team"]] = relationship("Team", back_populates="club", cascade="all, delete-orphan")

