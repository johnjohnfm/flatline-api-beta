from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
import tempfile
import os
import numpy as np
import wave
import contextlib
import scipy.fftpack

app = FastAPI()

def flatten_spectrum(data, sample_width):
    # Normalize
    dtype = np.int16 if sample_width == 2 else np.int8
    audio = np.frombuffer(data, dtype=dtype).astype(np.float32)

    # Apply FFT
    spectrum = np.fft.rfft(audio)
    magnitude = np.abs(spectrum)
    phase = np.angle(spectrum)

    # Flatten magnitude
    avg_mag = np.mean(magnitude)
    flattened_spectrum = avg_mag * np.exp(1j * phase)

    # Inverse FFT
    flattened_audio = np.fft.irfft(flattened_spectrum).astype(dtype)
    return flattened_audio.tobytes()

@app.post("/process")
async def process_audio(file: UploadFile = File(...)):
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_input:
            tmp_input.write(await file.read())
            input_path = tmp_input.name

        with contextlib.closing(wave.open(input_path, 'rb')) as wav_in:
            params = wav_in.getparams()
            channels, sampwidth, framerate, nframes = params[:4]
            frames = wav_in.readframes(nframes)

        # Chunk size: 32 KB (can be tuned)
        chunk_size = 32768
        processed_chunks = []

        # Split stereo channels if needed
        if channels == 2:
            left = frames[0::4] + frames[1::4]
            right = frames[2::4] + frames[3::4]
            processed_left = flatten_spectrum(left, sampwidth)
            processed_right = flatten_spectrum(right, sampwidth)
            # Interleave
            processed = b''.join(
                bytes([processed_left[i], processed_left[i+1], processed_right[i], processed_right[i+1]])
                for i in range(0, len(processed_left), 2)
            )
        else:
            processed = flatten_spectrum(frames, sampwidth)

        # Save output
        output_path = input_path.replace(".wav", "_flat.wav")
        with wave.open(output_path, 'wb') as wav_out:
            wav_out.setparams(params)
            wav_out.writeframes(processed)

        return FileResponse(output_path, filename="FLATLINED.wav", media_type="audio/wav")

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

