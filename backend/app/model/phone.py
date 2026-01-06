from __future__ import annotations

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field


class PhoneBase(BaseModel):
    type: str = Field(..., min_length=2, max_length=40)
    number: str = Field(..., min_length=6, max_length=30)


class PhoneIn(PhoneBase):
    model_config = ConfigDict(populate_by_name=True)

    id: str | None = Field(default=None, alias="_id")


class PhoneOut(PhoneBase):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., alias="_id")


class PhoneInDB(PhoneBase):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    id: ObjectId = Field(..., alias="_id")
