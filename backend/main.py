from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import numpy as np
import scipy.fftpack
import scipy.io.wavfile as wav
import os
import io
import soundfile as sf

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "FLATLINE API is active."}

@app.post("/process")
async def process_audio(file: UploadFile = File(...)):
    try:
        # Save uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_in:
            contents = await file.read()
            temp_in.write(contents)
            temp_in_path = temp_in.name

        # Read audio with soundfile (supports multiple formats and stereo)
        data, samplerate = sf.read(temp_in_path)
        os.remove(temp_in_path)  # Clean up input temp file

        # Handle mono vs. stereo
        if data.ndim == 1:
            data = data[:, np.newaxis]

        # Spectral flattening per channel
        flat_data = []
        for ch in range(data.shape[1]):
            signal = data[:, ch]
            spectrum = np.fft.rfft(signal)
            magnitude = np.abs(spectrum)
            phase = np.angle(spectrum)

            # Apply flattening (simple mean-based normalization)
            mean_mag = np.mean(magnitude)
            flat_mag = np.ones_like(magnitude) * mean_mag

            flattened = flat_mag * np.exp(1j * phase)
            flattened_signal = np.fft.irfft(flattened)

            # Match length and clip to original dynamic range
            flattened_signal = flattened_signal[:len(signal)]
            flattened_signal = np.clip(flattened_signal, -1.0, 1.0)

            flat_data.append(flattened_signal)

        # Recombine channels
        output = np.stack(flat_data, axis=-1)

        # Write to temp WAV file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_out:
            sf.write(temp_out.name, output, samplerate)
            temp_out.seek(0)
            return StreamingResponse(
                open(temp_out.name, "rb"),
                media_type="audio/wav",
                headers={"Content-Disposition": f"attachment; filename=neutralized.wav"}
            )

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
