# main.py — Refactored for stability and clarity

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import soundfile as sf
import io
import os
import numpy as np

app = FastAPI(title="FLATLINE API", version="1.0")

# CORS setup (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "FLATLINE API is running"}

@app.post("/neutralize/")
async def neutralize_audio(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        data, sr = sf.read(io.BytesIO(contents))

        # Dummy spectral flattening – normalize to -1 to 1
        data = data / np.max(np.abs(data))

        # Save output to memory
        buffer = io.BytesIO()
        sf.write(buffer, data, sr, format='WAV')
        buffer.seek(0)

        return StreamingResponse(buffer, media_type="audio/wav")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.post("/analyze/")
async def analyze_data(file: UploadFile = File(...)):
    try:
        # Placeholder for actual spectral clustering logic
        contents = await file.read()
        # Simulate response
        return {"message": "Analyze endpoint not yet implemented"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")
