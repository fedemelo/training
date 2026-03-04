import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.fit_file import FitFile


class EventBase(SQLModel):
    timestamp: datetime = Field(sa_type=DateTime(timezone=True))
    event: str = Field(max_length=50)
    event_type: str = Field(max_length=50)
    event_group: int


class EventCreate(EventBase):
    fit_file_id: uuid.UUID


class EventUpdate(SQLModel):
    timestamp: datetime | None = None
    event: str | None = Field(default=None, max_length=50)
    event_type: str | None = Field(default=None, max_length=50)
    event_group: int | None = None


class Event(EventBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    fit_file_id: uuid.UUID = Field(
        foreign_key="fitfile.id", nullable=False, ondelete="CASCADE"
    )
    fit_file: Optional["FitFile"] = Relationship(back_populates="events")


class EventPublic(EventBase):
    id: uuid.UUID
    fit_file_id: uuid.UUID


class EventsPublic(SQLModel):
    data: list[EventPublic]
    count: int
