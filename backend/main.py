from fastapi import FastAPI

from database import Base, engine
import models

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Umdeni Health Lite API",
    description="Backend API for Umdeni Health Lite",
    version="0.1.0",
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