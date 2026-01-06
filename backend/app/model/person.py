from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from utils import now_utc
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class PersonCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    birth_date: Optional[date] = None

class PersonUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=120)
    email: Optional[EmailStr] = None
    birth_date: Optional[date] = None

class PersonOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: EmailStr
    birth_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

class PersonInDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., alias="_id")  
    name: str
    email: EmailStr
    birth_date: Optional[date] = None
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(default_factory=now_utc)