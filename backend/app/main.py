
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.db.session import engine

from app.api.v1.auth import router as auth_router
from app.api.v1.access import router as access_router


app = FastAPI(
    title=settings.APP_NAME,
    description="Cloud Infrastructure and Incident Management Platform",
    version="1.0.0"
)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register API routers
app.include_router(
    auth_router,
    prefix="/api/v1"
)

app.include_router(
    access_router,
    prefix="/api/v1"
)


@app.get("/")
def root():

    return {
        "message": "Welcome to CloudOps",
        "status": "running"
    }


@app.get("/health/live")
def liveness():

    return {
        "status": "healthy",
        "application": "CloudOps API"
    }


@app.get("/health/ready")
def readiness():

    try:

        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "ready",
            "database": "connected"
        }

    except SQLAlchemyError:

        raise HTTPException(
            status_code=503,
            detail={
                "status": "not ready",
                "database": "unavailable"
            }
        )
