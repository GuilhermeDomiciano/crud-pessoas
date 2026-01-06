from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from utils import now_utc


class PersonCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    birth_date: date | None = None


class PersonUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=120)
    email: EmailStr | None = None
    birth_date: date | None = None


class PersonOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: EmailStr
    birth_date: date | None = None
    created_at: datetime
    updated_at: datetime


class PersonInDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., alias="_id")
    name: str
    email: EmailStr
    birth_date: date | None = None
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(default_factory=now_utc)
