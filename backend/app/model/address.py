from __future__ import annotations

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field


class AddressBase(BaseModel):
    line1: str = Field(..., min_length=2, max_length=200)
    line2: str | None = Field(None, max_length=200)
    city: str | None = Field(None, max_length=120)
    state: str | None = Field(None, max_length=120)
    postalCode: str | None = Field(None, max_length=20)
    country: str | None = Field(None, max_length=120)


class AddressUpdate(BaseModel):
    line1: str | None = Field(None, min_length=2, max_length=200)
    line2: str | None = Field(None, max_length=200)
    city: str | None = Field(None, max_length=120)
    state: str | None = Field(None, max_length=120)
    postalCode: str | None = Field(None, max_length=20)
    country: str | None = Field(None, max_length=120)

class AddressIn(AddressBase):
    model_config = ConfigDict(populate_by_name=True)

    id: str | None = Field(default=None, alias="_id")


class AddressOut(AddressBase):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., alias="_id")


class AddressInDB(AddressBase):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    id: ObjectId = Field(..., alias="_id")
