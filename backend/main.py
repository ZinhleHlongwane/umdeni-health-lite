from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    status,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

import models
from auth import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from database import Base, engine, get_db
from schemas import (
    ConsultationCreate,
    ConsultationResponse,
    PatientProfileCreate,
    PatientProfileResponse,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Umdeni Health Lite API",
    description="Backend API for Umdeni Health Lite",
    version="0.6.0",
)

security = HTTPBearer()


def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials,
    db: Session,
):
    try:
        payload = decode_access_token(
            credentials.credentials
        )
        user_id = int(payload["sub"])

    except (ValueError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )

    user = db.get(
        models.User,
        user_id,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return user


def require_role(required_role: str):
    def role_checker(
        credentials: HTTPAuthorizationCredentials = Depends(
            security
        ),
        db: Session = Depends(get_db),
    ):
        user = get_authenticated_user(
            credentials,
            db,
        )

        if user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"{required_role.capitalize()} "
                    "access required."
                ),
            )

        return user

    return role_checker


@app.get("/")
def root():
    return {
        "message": "Umdeni Health Lite API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "umdeni-health-lite-api",
        "database": "connected",
    }


@app.post(
    "/api/users/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = db.scalar(
        select(models.User).where(
            models.User.email == user.email
        )
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A user with this email "
                "already exists."
            ),
        )

    new_user = models.User(
        full_name=user.full_name,
        email=user.email,
        password_hash=hash_password(
            user.password
        ),
        role=user.role.value,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.post(
    "/api/auth/login",
    response_model=TokenResponse,
)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
):
    user = db.scalar(
        select(models.User).where(
            models.User.email
            == credentials.email
        )
    )

    if not user or not verify_password(
        credentials.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    token = create_access_token(
        user_id=user.id,
        email=user.email,
        role=user.role,
    )

    return TokenResponse(
        access_token=token,
    )


@app.get(
    "/api/users/me",
    response_model=UserResponse,
)
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    ),
    db: Session = Depends(get_db),
):
    return get_authenticated_user(
        credentials,
        db,
    )


@app.get("/api/doctor/dashboard")
def doctor_dashboard(
    current_user: models.User = Depends(
        require_role("doctor")
    ),
):
    return {
        "message": (
            "Doctor dashboard access granted"
        ),
        "user": {
            "id": current_user.id,
            "full_name": current_user.full_name,
            "email": current_user.email,
            "role": current_user.role,
        },
    }


@app.get("/api/patient/dashboard")
def patient_dashboard(
    current_user: models.User = Depends(
        require_role("patient")
    ),
):
    return {
        "message": (
            "Patient dashboard access granted"
        ),
        "user": {
            "id": current_user.id,
            "full_name": current_user.full_name,
            "email": current_user.email,
            "role": current_user.role,
        },
    }


@app.post(
    "/api/patient/profile",
    response_model=PatientProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_patient_profile(
    profile: PatientProfileCreate,
    current_user: models.User = Depends(
        require_role("patient")
    ),
    db: Session = Depends(get_db),
):
    existing_profile = db.scalar(
        select(models.PatientProfile).where(
            models.PatientProfile.user_id
            == current_user.id
        )
    )

    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Patient profile already exists."
            ),
        )

    patient_profile = models.PatientProfile(
        user_id=current_user.id,
        date_of_birth=profile.date_of_birth,
        phone_number=profile.phone_number,
        preferred_language=(
            profile.preferred_language
        ),
        emergency_contact_name=(
            profile.emergency_contact_name
        ),
        emergency_contact_phone=(
            profile.emergency_contact_phone
        ),
    )

    db.add(patient_profile)
    db.commit()
    db.refresh(patient_profile)

    return patient_profile


@app.get(
    "/api/patient/profile",
    response_model=PatientProfileResponse,
)
def get_patient_profile(
    current_user: models.User = Depends(
        require_role("patient")
    ),
    db: Session = Depends(get_db),
):
    profile = db.scalar(
        select(models.PatientProfile).where(
            models.PatientProfile.user_id
            == current_user.id
        )
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found.",
        )

    return profile


@app.post(
    "/api/doctor/consultations",
    response_model=ConsultationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_consultation(
    consultation: ConsultationCreate,
    current_user: models.User = Depends(
        require_role("doctor")
    ),
    db: Session = Depends(get_db),
):
    patient = db.get(
        models.User,
        consultation.patient_id,
    )

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found.",
        )

    if patient.role != "patient":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Selected user is not a patient."
            ),
        )

    new_consultation = models.Consultation(
        patient_id=patient.id,
        doctor_id=current_user.id,
        reason=consultation.reason,
        diagnosis=consultation.diagnosis,
        notes=consultation.notes,
    )

    db.add(new_consultation)
    db.commit()
    db.refresh(new_consultation)

    return new_consultation


@app.get(
    "/api/patient/consultations",
    response_model=list[ConsultationResponse],
)
def get_patient_consultations(
    current_user: models.User = Depends(
        require_role("patient")
    ),
    db: Session = Depends(get_db),
):
    consultations = db.scalars(
        select(models.Consultation)
        .where(
            models.Consultation.patient_id
            == current_user.id
        )
        .order_by(
            models.Consultation.consultation_date.desc()
        )
    ).all()

    return consultations