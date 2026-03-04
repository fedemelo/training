import uuid
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.fit_file import FitFile


class DeveloperDataIdBase(SQLModel):
    application_id: str = Field(max_length=36)
    manufacturer_id: str = Field(max_length=100)
    developer_data_index: int


class DeveloperDataIdCreate(DeveloperDataIdBase):
    fit_file_id: uuid.UUID


class DeveloperDataIdUpdate(SQLModel):
    application_id: str | None = Field(default=None, max_length=36)
    manufacturer_id: str | None = Field(default=None, max_length=100)
    developer_data_index: int | None = None


class DeveloperDataId(DeveloperDataIdBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    fit_file_id: uuid.UUID = Field(
        foreign_key="fitfile.id", nullable=False, ondelete="CASCADE"
    )
    fit_file: Optional["FitFile"] = Relationship(back_populates="developer_data_ids")


class DeveloperDataIdPublic(DeveloperDataIdBase):
    id: uuid.UUID
    fit_file_id: uuid.UUID


class DeveloperDataIdsPublic(SQLModel):
    data: list[DeveloperDataIdPublic]
    count: int
