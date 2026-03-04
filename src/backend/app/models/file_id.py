import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.fit_file import FitFile


class FileIdBase(SQLModel):
    type: str = Field(max_length=50)
    manufacturer: str = Field(max_length=100)
    product: int
    time_created: datetime = Field(sa_type=DateTime(timezone=True))
    product_name: str = Field(max_length=255)


class FileIdCreate(FileIdBase):
    fit_file_id: uuid.UUID


class FileIdUpdate(SQLModel):
    type: str | None = Field(default=None, max_length=50)
    manufacturer: str | None = Field(default=None, max_length=100)
    product: int | None = None
    time_created: datetime | None = None
    product_name: str | None = Field(default=None, max_length=255)


class FileId(FileIdBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    fit_file_id: uuid.UUID = Field(
        foreign_key="fitfile.id", nullable=False, ondelete="CASCADE"
    )
    fit_file: Optional["FitFile"] = Relationship(back_populates="file_id")


class FileIdPublic(FileIdBase):
    id: uuid.UUID
    fit_file_id: uuid.UUID
