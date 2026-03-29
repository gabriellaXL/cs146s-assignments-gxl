from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def utcnow() -> datetime:
    return datetime.now(UTC)


class TimestampMixin:
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class Note(Base, TimestampMixin):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    action_items = relationship("ActionItem", back_populates="project")


class ActionItem(Base, TimestampMixin):
    __tablename__ = "action_items"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    completed = Column(Boolean, default=False, nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)
    project = relationship("Project", back_populates="action_items")
