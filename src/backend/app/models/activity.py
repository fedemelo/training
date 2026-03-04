import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.fit_file import FitFile


class ActivityBase(SQLModel):
    timestamp: datetime = Field(sa_type=DateTime(timezone=True))
    total_timer_time: float
    num_sessions: int
    type: str = Field(max_length=50)
    event: str = Field(max_length=50)
    event_type: str = Field(max_length=50)
    local_timestamp: datetime = Field(sa_type=DateTime(timezone=True))


class ActivityCreate(ActivityBase):
    fit_file_id: uuid.UUID


class ActivityUpdate(SQLModel):
    timestamp: datetime | None = None
    total_timer_time: float | None = None
    num_sessions: int | None = None
    type: str | None = Field(default=None, max_length=50)
    event: str | None = Field(default=None, max_length=50)
    event_type: str | None = Field(default=None, max_length=50)
    local_timestamp: datetime | None = None


class Activity(ActivityBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    fit_file_id: uuid.UUID = Field(
        foreign_key="fitfile.id", nullable=False, ondelete="CASCADE"
    )
    fit_file: Optional["FitFile"] = Relationship(back_populates="activities")


class ActivityPublic(ActivityBase):
    id: uuid.UUID
    fit_file_id: uuid.UUID


class ActivitiesPublic(SQLModel):
    data: list[ActivityPublic]
    count: int
