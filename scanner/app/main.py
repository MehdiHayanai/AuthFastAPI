from app.api.routes import router as api_router
from app.core.config import settings
from app.core.database import Base, engine
from app.core.utils import get_current_datetime
from app.middleware.auth_middleware import AutoRefreshMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add auto-refresh middleware
app.add_middleware(AutoRefreshMiddleware)

# Include API routes
app.include_router(api_router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Auth App"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/ping")
def ping():
    return {"message": f"pong {get_current_datetime()}."}
