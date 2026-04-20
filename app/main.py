"""
This is the main application file for the fraud detection system.
It initializes the FastAPI application and includes the API endpoints.
"""

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.endpoints import router as api_router

app = FastAPI(
    title="Proactive Fraud Detection System",
    description="A system combining ML and honeypot technology to detect and combat digital payment fraud.",
    version="0.0.1",
)

# 1. Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, suitable for local development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],   # Allows all headers
)

# 2. Mount the API router
app.include_router(api_router, prefix="/api")

# 3. Add endpoints for additional pages
@app.get("/analytics", response_class=FileResponse)
async def read_analytics():
    return "static/analytics.html"

@app.get("/settings", response_class=FileResponse)
async def read_settings():
    return "static/settings.html"

@app.get("/checkout", response_class=FileResponse)
async def read_checkout():
    return "static/checkout.html"

# 4. Mount the static directory to serve the frontend (must come after other routes)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
