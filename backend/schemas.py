from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    doctor = "doctor"
    patient = "patient"
    family = "family"
    caregiver = "caregiver"


class AppointmentStatus(str, Enum):
    scheduled = "scheduled"
    completed = "completed"
    cancelled = "cancelled"


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


class ConsultationCreate(BaseModel):
    patient_id: int

    reason: str = Field(
        min_length=2,
        max_length=255,
    )

    diagnosis: str | None = Field(
        default=None,
        max_length=255,
    )

    notes: str | None = None


class ConsultationResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    consultation_date: datetime
    reason: str
    diagnosis: str | None
    notes: str | None

    model_config = {
        "from_attributes": True
    }


class MedicationCreate(BaseModel):
    patient_id: int
    consultation_id: int | None = None

    medication_name: str = Field(
        min_length=2,
        max_length=120,
    )

    dosage: str = Field(
        min_length=1,
        max_length=120,
    )

    frequency: str = Field(
        min_length=2,
        max_length=120,
    )

    duration: str | None = Field(
        default=None,
        max_length=120,
    )

    instructions: str | None = None


class MedicationResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    consultation_id: int | None
    medication_name: str
    dosage: str
    frequency: str
    duration: str | None
    instructions: str | None
    prescribed_at: datetime

    model_config = {
        "from_attributes": True
    }


class AppointmentCreate(BaseModel):
    patient_id: int
    appointment_date: datetime

    reason: str = Field(
        min_length=2,
        max_length=255,
    )

    notes: str | None = None


class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    appointment_date: datetime
    reason: str
    status: AppointmentStatus
    notes: str | None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }