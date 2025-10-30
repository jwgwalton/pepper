"""
FastAPI application for the Pepper Outlook AI Agent
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
from app.routers import auth, graph

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Pepper - Outlook AI Agent",
    description="AI-powered agent for Microsoft Outlook operations",
    version="0.1.0"
)

# Include routers
app.include_router(auth.router)
app.include_router(graph.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Pepper - Outlook AI Agent",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Check if required environment variables are set
    required_env_vars = ["CLIENT_ID", "TENANT_ID", "REDIRECT_URI"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "message": f"Missing required environment variables: {', '.join(missing_vars)}",
                "missing_vars": missing_vars
            }
        )

    return {
        "status": "healthy",
        "message": "Service is running",
        "environment": {
            "client_id_set": bool(os.getenv("CLIENT_ID")),
            "tenant_id_set": bool(os.getenv("TENANT_ID")),
            "redirect_uri_set": bool(os.getenv("REDIRECT_URI"))
        }
    }
