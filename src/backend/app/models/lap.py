import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.fit_file import FitFile


class LapBase(SQLModel):
    timestamp: datetime = Field(sa_type=DateTime(timezone=True))
    message_index: int
    start_time: datetime = Field(sa_type=DateTime(timezone=True))
    total_elapsed_time: float
    total_timer_time: float
    total_distance: float
    total_calories: int
    avg_heart_rate: int | None = None
    max_heart_rate: int | None = None
    avg_cadence: int | None = None
    avg_power: int | None = None
    max_power: int | None = None
    total_ascent: int | None = None
    total_descent: int | None = None
    sport: str = Field(max_length=50)
    normalized_power: int | None = None
    sub_sport: str = Field(max_length=50)
    total_work: int | None = None
    avg_temperature: float | None = None
    min_heart_rate: int | None = None
    enhanced_avg_speed: float | None = None
    enhanced_max_speed: float | None = None


class LapCreate(LapBase):
    fit_file_id: uuid.UUID


class LapUpdate(SQLModel):
    timestamp: datetime | None = None
    message_index: int | None = None
    start_time: datetime | None = None
    total_elapsed_time: float | None = None
    total_timer_time: float | None = None
    total_distance: float | None = None
    total_calories: int | None = None
    avg_heart_rate: int | None = None
    max_heart_rate: int | None = None
    avg_cadence: int | None = None
    avg_power: int | None = None
    max_power: int | None = None
    total_ascent: int | None = None
    total_descent: int | None = None
    sport: str | None = Field(default=None, max_length=50)
    normalized_power: int | None = None
    sub_sport: str | None = Field(default=None, max_length=50)
    total_work: int | None = None
    avg_temperature: float | None = None
    min_heart_rate: int | None = None
    enhanced_avg_speed: float | None = None
    enhanced_max_speed: float | None = None


class Lap(LapBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    fit_file_id: uuid.UUID = Field(
        foreign_key="fitfile.id", nullable=False, ondelete="CASCADE"
    )
    fit_file: Optional["FitFile"] = Relationship(back_populates="laps")


class LapPublic(LapBase):
    id: uuid.UUID
    fit_file_id: uuid.UUID


class LapsPublic(SQLModel):
    data: list[LapPublic]
    count: int
