from __future__ import annotations

from datetime import date, datetime

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from utils import now_utc


class AddressBase(BaseModel):
    line1: str = Field(..., min_length=2, max_length=200)
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


class PersonCreate(BaseModel):
    firstName: str = Field(..., min_length=2, max_length=120)
    lastName: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    documentNumber: str = Field(..., min_length=3, max_length=30)
    dateOfBirth: date | None = None
    addresses: list[AddressIn] = Field(default_factory=list)
    phoneNumbers: list[PhoneIn] = Field(default_factory=list)


class PersonUpdate(BaseModel):
    firstName: str | None = Field(None, min_length=2, max_length=120)
    lastName: str | None = Field(None, min_length=2, max_length=120)
    email: EmailStr | None = None
    documentNumber: str | None = Field(None, min_length=3, max_length=30)
    dateOfBirth: date | None = None
    addresses: list[AddressIn] | None = None
    phoneNumbers: list[PhoneIn] | None = None


class PersonOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    firstName: str
    lastName: str
    email: EmailStr
    documentNumber: str
    dateOfBirth: date | None = None
    addresses: list[AddressOut]
    phoneNumbers: list[PhoneOut]
    createdAt: datetime
    updatedAt: datetime
    version: int
    deletedAt: datetime | None = None


class PersonInDB(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    id: ObjectId = Field(..., alias="_id")
    firstName: str
    lastName: str
    email: EmailStr
    documentNumber: str
    dateOfBirth: date | None = None
    addresses: list[AddressInDB] = Field(default_factory=list)
    phoneNumbers: list[PhoneInDB] = Field(default_factory=list)
    createdAt: datetime = Field(default_factory=now_utc)
    updatedAt: datetime = Field(default_factory=now_utc)
    version: int = 1
    deletedAt: datetime | None = None
