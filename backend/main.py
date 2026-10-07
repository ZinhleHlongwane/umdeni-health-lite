from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

import models
from auth import hash_password
from database import Base, engine, get_db
from schemas import UserCreate, UserResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Umdeni Health Lite API",
    description="Backend API for Umdeni Health Lite",
    version="0.2.0",
)


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
            detail="A user with this email already exists.",
        )

    new_user = models.User(
        full_name=user.full_name,
        email=user.email,
        password_hash=hash_password(user.password),
        role=user.role.value,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user