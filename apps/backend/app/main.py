"""
A2A Agent Ecosystem Backend API
FastAPI application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection
from app.api.v1 import agents, groups, reputation, validation, ipfs, tasks, prompts, payments

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 Starting A2A Agent Ecosystem Backend...")
    await connect_to_mongo()
    logger.info("✅ Connected to MongoDB")
    logger.info(f"🌐 Server running on {settings.API_HOST}:{settings.API_PORT}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down...")
    await close_mongo_connection()
    logger.info("✅ Closed MongoDB connection")


app = FastAPI(
    title="A2A Agent Ecosystem API",
    description="Backend API for Agent-to-Agent Ecosystem Infrastructure (ERC-8004 + A2A Protocol)",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "A2A Agent Ecosystem API",
        "version": "0.1.0",
        "docs": "/docs",
        "status": "operational",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "blockchain": {
            "provider": settings.WEB3_PROVIDER_URI,
            "chain_id": settings.CHAIN_ID,
        },
    }


# Include routers
app.include_router(agents.router, prefix="/api/v1/agents", tags=["Agents"])
app.include_router(groups.router, prefix="/api/v1/groups", tags=["Groups"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["Tasks"])
app.include_router(prompts.router, prefix="/api/v1/prompts", tags=["Prompts"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["Payments"])
app.include_router(reputation.router, prefix="/api/v1/reputation", tags=["Reputation"])
app.include_router(validation.router, prefix="/api/v1/validation", tags=["Validation"])
app.include_router(ipfs.router, prefix="/api/v1/ipfs", tags=["IPFS"])


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": str(type(exc).__name__)},
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
    )

