import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.fit_file import FitFile


class RecordBase(SQLModel):
    timestamp: datetime = Field(sa_type=DateTime(timezone=True))
    position_lat: float | None = None
    position_long: float | None = None
    heart_rate: int | None = None
    distance: float = 0.0
    activity_type: str | None = Field(default=None, max_length=50)
    enhanced_speed: float | None = None
    enhanced_altitude: float | None = None


class RecordCreate(RecordBase):
    fit_file_id: uuid.UUID


class RecordUpdate(SQLModel):
    timestamp: datetime | None = None
    position_lat: float | None = None
    position_long: float | None = None
    heart_rate: int | None = None
    distance: float | None = None
    activity_type: str | None = Field(default=None, max_length=50)
    enhanced_speed: float | None = None
    enhanced_altitude: float | None = None


class Record(RecordBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    fit_file_id: uuid.UUID = Field(
        foreign_key="fitfile.id", nullable=False, ondelete="CASCADE"
    )
    fit_file: Optional["FitFile"] = Relationship(back_populates="records")


class RecordPublic(RecordBase):
    id: uuid.UUID
    fit_file_id: uuid.UUID


class RecordsPublic(SQLModel):
    data: list[RecordPublic]
    count: int
