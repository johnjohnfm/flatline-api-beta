from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
import numpy as np
import scipy.signal
import soundfile as sf
import io

app = FastAPI()

# CORS setup (adjust for production as needed)
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
        raise HTTPException(status_code=400, detail="Invalid audio format.")

    try:
        data, sr = sf.read(file.file, always_2d=True)  # shape: (samples, channels)
        data = data.T  # shape: (channels, samples)

        flattened = flatten_spectrum(data, sr, gentle=True)
        flattened = flattened.T  # shape: (samples, channels)

        buffer = io.BytesIO()
        sf.write(buffer, flattened, sr, format='WAV')
        buffer.seek(0)

        return StreamingResponse(buffer, media_type="audio/wav", headers={
            "Content-Disposition": f"attachment; filename=flatlined_{file.filename}"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def flatten_spectrum(audio: np.ndarray, sr: int, gentle: bool = True) -> np.ndarray:
    """
    Spectrally flatten stereo or mono audio using gain-safe FFT whitening.

    Args:
        audio (np.ndarray): shape (channels, samples)
        sr (int): sample rate
        gentle (bool): apply soft gain clamping to avoid compression artifacts

    Returns:
        np.ndarray: flattened signal, same shape
    """
    flattened = []
    window = 'hann'
    n_fft = 2048
    hop = n_fft // 2
    epsilon = 1e-6
    min_gain = 0.5
    max_gain = 2.0

    for ch in audio:
        # STFT
        f, t, Zxx = scipy.signal.stft(ch, fs=sr, window=window, nperseg=n_fft, noverlap=hop, boundary='zeros')
        mag = np.abs(Zxx)
        phase = np.angle(Zxx)

        # Mean spectrum
        mean_mag = np.mean(mag, axis=1, keepdims=True)
        mean_mag[mean_mag == 0] = epsilon

        if gentle:
            # Subtle flattening
            gain = 1.0 + (mag - mean_mag) / (mean_mag + epsilon)
            gain = np.clip(gain, min_gain, max_gain)
        else:
            # Aggressive flattening
            gain = mag / mean_mag
            gain = np.clip(gain, 0.0, 10.0)

        Zxx_flat = gain * np.exp(1j * phase)

        # Inverse STFT
        _, ch_out = scipy.signal.istft(Zxx_flat, fs=sr, window=window, nperseg=n_fft, noverlap=hop)

        # Match original length
        if len(ch_out) > len(ch):
            ch_out = ch_out[:len(ch)]
        elif len(ch_out) < len(ch):
            ch_out = np.pad(ch_out, (0, len(ch) - len(ch_out)))

        # LUFS-safe energy matching
        energy_in = np.sqrt(np.mean(ch**2))
        energy_out = np.sqrt(np.mean(ch_out**2)) + epsilon
        ch_out *= energy_in / energy_out

        flattened.append(ch_out)

    return np.stack(flattened, axis=0).astype(np.float32)
