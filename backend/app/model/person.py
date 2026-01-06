from __future__ import annotations

from datetime import date, datetime

from model.phone import PhoneIn, PhoneInDB, PhoneOut
from bson import ObjectId
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from model.address import AddressIn, AddressInDB, AddressOut
from utils import now_utc


class PersonCreate(BaseModel):
    firstName: str = Field(..., min_length=2, max_length=120)
    lastName: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    documentNumber: str = Field(..., min_length=3, max_length=30)
    dateOfBirth: date | None = None
    addresses: list[AddressIn] | None = None
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
