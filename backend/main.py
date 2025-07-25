"""
FastAPI Backend for Therapy Chat Application
Main application entry point with CORS configuration and router includes.
"""  

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
import os
from pathlib import Path
from dotenv import load_dotenv
import threading
import io
import sys
sys.path.append(str(Path(__file__).parent / "emotion_detection"))
from emotion_detection.main import run_emotion_detection

load_dotenv()

from routers import auth, sessions, messages, settings as settings_router, audio, reports
from core.config import get_settings
from models.database import init_db

# Get settings
settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title="Therapy Chat API",
    description="AI-powered therapy chat application with voice integration",
    version="2.0.0",
    docs_url="/api/docs" if settings.environment == "development" else None,
    redoc_url="/api/redoc" if settings.environment == "development" else None,
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5000",  # Current Replit app
        "http://localhost:5173",  # Vite dev server
        "https://*.replit.app",   # Replit deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["therapy-sessions"])
app.include_router(messages.router, prefix="/api/messages", tags=["chat-messages"])
app.include_router(settings_router.router, prefix="/api/settings", tags=["user-settings"])
app.include_router(audio.router, prefix="/api/audio", tags=["audio-processing"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])


# Serve static files (React build)
static_dir = Path(__file__).parent.parent / "client" / "dist"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    # Serve React app for all non-API routes
    @app.get("/{path:path}")
    async def serve_spa(path: str):
        """Serve React SPA for all non-API routes"""
        if path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        
        file_path = static_dir / path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        else:
            # Return index.html for SPA routing
            return FileResponse(static_dir / "index.html")

# Global state for emotion detection
emotion_state = {
    'emotion_probs': None,
    'frame': None,
    'stop': False,
    'stopped': False,
    'thread': None
}

@app.post("/api/emotion/start")
def start_emotion_detection():
    if emotion_state.get('thread') and emotion_state['thread'].is_alive():
        return {"success": False, "message": "Emotion detection already running."}
    emotion_state['emotion_probs'] = None
    emotion_state['frame'] = None
    emotion_state['stop'] = False
    emotion_state['stopped'] = False
    t = threading.Thread(target=run_emotion_detection, args=(emotion_state,))
    emotion_state['thread'] = t
    t.start()
    return {"success": True, "message": "Emotion detection started."}

@app.post("/api/emotion/stop")
def stop_emotion_detection():
    emotion_state['stop'] = True
    t = emotion_state.get('thread')
    if t and t.is_alive():
        t.join(timeout=5)
    return {"success": True, "emotion_probs": emotion_state.get('emotion_probs')}

@app.get("/api/emotion/frame")
def get_emotion_frame():
    frame = emotion_state.get('frame')
    if frame is None:
        return JSONResponse({"success": False, "message": "No frame available."}, status_code=404)
    return StreamingResponse(io.BytesIO(frame), media_type="image/jpeg")

@app.get("/api/emotion/probs")
def get_emotion_probs():
    probs = emotion_state.get('emotion_probs')
    if probs is None:
        return {"success": False, "emotion_probs": None}
    return {"success": True, "emotion_probs": probs}

@app.on_event("startup")
async def startup_event():
    """Initialize database and other startup tasks"""
    await init_db()
    print("🚀 Therapy Chat API server started successfully")
    print(f"📊 Environment: {settings.environment}")
    print(f"🗄️  Database: Connected")
    print(f"🎯 API Documentation: /api/docs")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup tasks on shutdown"""
    print("🛑 Therapy Chat API server shutting down")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "environment": settings.environment
    }

@app.get("/api")
async def api_root():
    """API root endpoint with basic information"""
    return {
        "message": "Therapy Chat API",
        "version": "2.0.0",
        "docs": "/api/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development",
        log_level="info"
    )