from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="CloudOps API",
    description="Cloud Infrastructure and Incident Management Platform",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Welcome to CloudOps",
        "status": "running"
    }


@app.get("/health/live")
def health_check():
    return {
        "status": "healthy"
    }