from fastapi import FastAPI
import os
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .api.auth import router as auth_router
from .api.tasks import router as tasks_router
from .api import errors
from .database import engine, create_db_and_tables
from .hf_inference import router as hf_router
from .chatbot import router as chatbot_router
from .api.routes import mcp_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler - creates tables on startup"""
    # Startup: Create tables if they don't exist
    if engine:
        create_db_and_tables()
    yield
    # Shutdown: cleanup if needed


# Create FastAPI application
app = FastAPI(
    title="Todo API",
    description="RESTful API for multi-user todo management with JWT authentication",
    version="1.0.0",
    lifespan=lifespan
)


# Configure CORS properly
# Default to development settings if ENVIRONMENT is not set or is "development"
environment = os.getenv("ENVIRONMENT", "[production]")
if environment == "production":
    origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://front-6sdg16hl8-syed-ali-razas-projects.vercel.app",  # Old Frontend URL
        "https://front-wheat-sigma-99.vercel.app/"  # Current Frontend URL
    ]
else:
    origins = [
        os.getenv("FRONTEND_URL", "https://front-wheat-sigma-99.vercel.app/"),
        "https://front-6sdg16hl8-syed-ali-razas-projects.vercel.app",  # Old Frontend URL fallback
        "https://front-wheat-sigma-99.vercel.app/",# Current Frontend URL
        "http://localhost:3000"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],

)

# Register global exception handlers
app.add_exception_handler(500, errors.general_exception_handler)
app.add_exception_handler(422, errors.validation_exception_handler)

# Include routers
app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(hf_router)
app.include_router(chatbot_router)
app.include_router(mcp_router)


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Todo API is running",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
