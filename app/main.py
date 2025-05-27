from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
from dotenv import load_dotenv

# Import routers
from .routers import files, search, ocr

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Quote Search API",
    description="API for searching quotes in documents using OCR and semantic search",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(files.router, prefix="/api/files", tags=["files"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(ocr.router, prefix="/api/ocr", tags=["ocr"])

@app.get("/")
async def root():
    return {"message": "Welcome to Quote Search API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 