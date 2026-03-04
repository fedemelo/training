import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.activity import Activity
    from app.models.developer_data_id import DeveloperDataId
    from app.models.device_info import DeviceInfo
    from app.models.event import Event
    from app.models.file_id import FileId
    from app.models.lap import Lap
    from app.models.record import Record
    from app.models.session import Session


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)


class FitFileBase(SQLModel):
    filename: str = Field(max_length=255)


class FitFileCreate(FitFileBase):
    pass


class FitFileUpdate(SQLModel):
    filename: str | None = Field(default=None, max_length=255)


class FitFile(FitFileBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    uploaded_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),
    )
    file_id: Optional["FileId"] = Relationship(
        back_populates="fit_file", cascade_delete=True
    )
    developer_data_ids: list["DeveloperDataId"] = Relationship(
        back_populates="fit_file", cascade_delete=True
    )
    device_infos: list["DeviceInfo"] = Relationship(
        back_populates="fit_file", cascade_delete=True
    )
    activities: list["Activity"] = Relationship(
        back_populates="fit_file", cascade_delete=True
    )
    events: list["Event"] = Relationship(back_populates="fit_file", cascade_delete=True)
    records: list["Record"] = Relationship(
        back_populates="fit_file", cascade_delete=True
    )
    laps: list["Lap"] = Relationship(back_populates="fit_file", cascade_delete=True)
    sessions: list["Session"] = Relationship(
        back_populates="fit_file", cascade_delete=True
    )


class FitFilePublic(FitFileBase):
    id: uuid.UUID
    uploaded_at: datetime | None = None


class FitFilesPublic(SQLModel):
    data: list[FitFilePublic]
    count: int
