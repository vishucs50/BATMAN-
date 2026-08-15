from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Mission(Base):
    __tablename__ = "missions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    mission_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    mission_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="PLANNING",
        nullable=False,
    )

    created_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    objectives = relationship(
        "Objective",
        back_populates="mission",
        cascade="all, delete-orphan",
    )

    creator = relationship(
        "User",
        back_populates="missions",
    )