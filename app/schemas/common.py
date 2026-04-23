from datetime import date, datetime
from typing import Any, Generic, List, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class Message(BaseModel):
    message: str


class ErrorDetail(BaseModel):
    field: str | None = None
    message: str


class ErrorResponse(BaseModel):
    detail: str
    errors: List[ErrorDetail] = Field(default_factory=list)


class Paginated(BaseModel, Generic[T]):
    items: List[T]
    total: int
    skip: int
    limit: int


def dt_schema() -> str:
    return "ISO 8601 datetime string"


# Allow ORM
class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
