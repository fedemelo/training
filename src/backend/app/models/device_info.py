import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.fit_file import FitFile


class DeviceInfoBase(SQLModel):
    timestamp: datetime = Field(sa_type=DateTime(timezone=True))
    manufacturer: str = Field(max_length=100)
    product_name: str = Field(max_length=255)


class DeviceInfoCreate(DeviceInfoBase):
    fit_file_id: uuid.UUID


class DeviceInfoUpdate(SQLModel):
    timestamp: datetime | None = None
    manufacturer: str | None = Field(default=None, max_length=100)
    product_name: str | None = Field(default=None, max_length=255)


class DeviceInfo(DeviceInfoBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    fit_file_id: uuid.UUID = Field(
        foreign_key="fitfile.id", nullable=False, ondelete="CASCADE"
    )
    fit_file: Optional["FitFile"] = Relationship(back_populates="device_infos")


class DeviceInfoPublic(DeviceInfoBase):
    id: uuid.UUID
    fit_file_id: uuid.UUID


class DeviceInfosPublic(SQLModel):
    data: list[DeviceInfoPublic]
    count: int
