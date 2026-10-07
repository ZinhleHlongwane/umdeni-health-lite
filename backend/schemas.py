from datetime import date
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    doctor = "doctor"
    patient = "patient"
    family = "family"
    caregiver = "caregiver"


class UserCreate(BaseModel):
    full_name: str = Field(
        min_length=2,
        max_length=120,
    )
    email: EmailStr
    password: str = Field(min_length=8)
    role: UserRole


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: UserRole

    model_config = {
        "from_attributes": True
    }


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PatientProfileCreate(BaseModel):
    date_of_birth: date | None = None

    phone_number: str | None = Field(
        default=None,
        max_length=30,
    )

    preferred_language: str = Field(
        default="English",
        min_length=2,
        max_length=30,
    )

    emergency_contact_name: str | None = Field(
        default=None,
        max_length=120,
    )

    emergency_contact_phone: str | None = Field(
        default=None,
        max_length=30,
    )


class PatientProfileResponse(BaseModel):
    id: int
    user_id: int
    date_of_birth: date | None
    phone_number: str | None
    preferred_language: str
    emergency_contact_name: str | None
    emergency_contact_phone: str | None

    model_config = {
        "from_attributes": True
    }