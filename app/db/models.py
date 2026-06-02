from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import ForeignKey, Integer, String, Text, JSON, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Announcement(Base):
    __tablename__ = "announcements"
    id: Mapped[int] = mapped_column(primary_key=True)
    source_type: Mapped[str] = mapped_column(String(16), default="submit")
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    raw_text: Mapped[str] = mapped_column(Text)
    org_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    region: Mapped[str | None] = mapped_column(String(128), nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    positions: Mapped[list[Position]] = relationship(back_populates="announcement")


class Position(Base):
    __tablename__ = "positions"
    id: Mapped[int] = mapped_column(primary_key=True)
    announcement_id: Mapped[int] = mapped_column(ForeignKey("announcements.id"))
    org_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    position_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    major_req: Mapped[str | None] = mapped_column(Text, nullable=True)
    age_req: Mapped[str | None] = mapped_column(String(256), nullable=True)
    education_req: Mapped[str | None] = mapped_column(String(256), nullable=True)
    experience_req: Mapped[str | None] = mapped_column(Text, nullable=True)
    cert_req: Mapped[str | None] = mapped_column(Text, nullable=True)
    headcount: Mapped[int | None] = mapped_column(Integer, nullable=True)

    announcement: Mapped[Announcement] = relationship(back_populates="positions")
    analyses: Mapped[list[Analysis]] = relationship(back_populates="position")


class Analysis(Base):
    __tablename__ = "analyses"
    id: Mapped[int] = mapped_column(primary_key=True)
    position_id: Mapped[int] = mapped_column(ForeignKey("positions.id"))
    suspicion_score: Mapped[int] = mapped_column(Integer)
    level: Mapped[str] = mapped_column(String(8))
    hit_features: Mapped[list] = mapped_column(JSON, default=list)
    reasoning: Mapped[str] = mapped_column(Text, default="")
    highlights: Mapped[list] = mapped_column(JSON, default=list)
    model_version: Mapped[str] = mapped_column(String(64))
    analyzed_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    position: Mapped[Position] = relationship(back_populates="analyses")
