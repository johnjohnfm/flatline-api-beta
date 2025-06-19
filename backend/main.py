from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os

app = FastAPI()

# Allow frontend (Vercel) access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend domain for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "FLATLINE API is active."}

@app.post("/process")
async def process_audio(file: UploadFile = File(...)):
    try:
        # Save the uploaded file
        input_path = "temp_input.wav"
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # TODO: Add your real audio processing function here
        # For now, we'll simulate processing by copying the file
        output_path = "output.wav"
        shutil.copy(input_path, output_path)

        # Return the file as a downloadable response
        return FileResponse(output_path, media_type="audio/wav", filename="neutralized.wav")

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
