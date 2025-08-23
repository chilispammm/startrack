from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
from pathlib import Path

# Import routers
from app.routers import players, heatmaps, downloads
from app.services.data_loader import data_loader
from app.utils.responses import APIResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AFCON 2023 Analytics API",
    description="Backend API for AFCON 2023 player valuation and performance analysis",
    version="1.0.0",
    docs_url="/docs",  # Enable Swagger UI
    redoc_url="/redoc",  # Enable ReDoc
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(players.router)
app.include_router(heatmaps.router)
app.include_router(downloads.router)

# Startup event - load data when the application starts
@app.on_event("startup")
async def startup_event():
    try:
        # Initialize data loader
        success, message = data_loader.load_data()
        if not success:
            logger.error(f"Failed to load data: {message}")
            # Don't crash the app, but log the error
        else:
            logger.info("Successfully loaded all data")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")

# Health check endpoint
@app.get("/api/v1/health", response_model=dict)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "afcon-analytics-api",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to AFCON 2023 Analytics API",
        "documentation": "/docs",
        "version": "1.0.0"
    }

# Custom exception handler for unhandled exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return APIResponse(
        success=False,
        message="An unexpected error occurred",
        status_code=500
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
