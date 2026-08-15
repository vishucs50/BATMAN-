from datetime import datetime

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Objective(Base):
    __tablename__ = "objectives"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    mission_id: Mapped[int] = mapped_column(
        ForeignKey("missions.id", ondelete="CASCADE"),
        nullable=False,
    )

    obj_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    priority: Mapped[int] = mapped_column(
        nullable=False,
    )

    target_location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    deadline: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="PENDING",
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    mission = relationship(
        "Mission",
        back_populates="objectives",
    )