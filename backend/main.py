from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
import numpy as np
import soundfile as sf
import io
import scipy.signal

app = FastAPI()

# Allow all origins during dev — you can restrict this later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/neutralize/")
async def neutralize_audio(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(('.wav', '.flac', '.aiff', '.aif')):
        raise HTTPException(status_code=400, detail="Invalid audio format. Please upload a WAV, FLAC, or AIFF file.")

    try:
        data, sr = sf.read(file.file, always_2d=True)  # (n_samples, n_channels)
        data = data.T  # -> (n_channels, n_samples)

        flattened = flatten_spectrum(data, sr)
        flattened = flattened.T  # back to (n_samples, n_channels)

        # Write to buffer
        buffer = io.BytesIO()
        sf.write(buffer, flattened, sr, format='WAV')
        buffer.seek(0)

        return StreamingResponse(buffer, media_type="audio/wav", headers={
            "Content-Disposition": f"attachment; filename=flatlined_{file.filename}"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def flatten_spectrum(audio: np.ndarray, sr: int) -> np.ndarray:
    """
    Applies basic spectral flattening to stereo or mono audio.
    Each channel is processed independently using FFT whitening.
    """
    flattened = []
    for ch in audio:
        # Short-Time Fourier Transform (windowed FFT)
        f, t, Zxx = scipy.signal.stft(ch, fs=sr, nperseg=2048, noverlap=1024)
        mag = np.abs(Zxx)
        phase = np.angle(Zxx)

        # Mean spectrum across time
        mean_mag = np.mean(mag, axis=1, keepdims=True)
        mean_mag[mean_mag == 0] = 1e-6

        # Normalize spectral energy
        whitened_mag = mag / mean_mag
        flattened_Zxx = whitened_mag * np.exp(1j * phase)

        # Inverse STFT
        _, flattened_ch = scipy.signal.istft(flattened_Zxx, fs=sr, nperseg=2048, noverlap=1024)
        # Trim/pad to original length
        if len(flattened_ch) > ch.shape[0]:
            flattened_ch = flattened_ch[:ch.shape[0]]
        elif len(flattened_ch) < ch.shape[0]:
            flattened_ch = np.pad(flattened_ch, (0, ch.shape[0] - len(flattened_ch)))
        flattened.append(flattened_ch)

    return np.stack(flattened, axis=0)
