from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
import numpy as np
import scipy.signal
import soundfile as sf
import io

app = FastAPI()

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
        data, sr = sf.read(file.file, always_2d=True)  # (samples, channels)
        data = data.T  # (channels, samples)

        # Apply transparent spectral matching
        flattened = match_to_target_spectrum(data, sr)
        flattened = flattened.T  # (samples, channels)

        buffer = io.BytesIO()
        sf.write(buffer, flattened, sr, format='WAV')
        buffer.seek(0)

        return StreamingResponse(buffer, media_type="audio/wav", headers={
            "Content-Disposition": f"attachment; filename=flatlined_{file.filename}"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def match_to_target_spectrum(audio: np.ndarray, sr: int, target_curve: str = "flat") -> np.ndarray:
    """
    Transparently matches the average spectrum of audio to a flat EQ curve.
    Mimics Waves Equator with shape=flat, tilt=0, and sensitivity ~30%.

    Args:
        audio (np.ndarray): shape (channels, samples)
        sr (int): Sample rate
        target_curve (str): "flat" or "pink"

    Returns:
        np.ndarray: Corrected audio, same shape
    """
    matched = []
    n_fft = 2048
    hop = n_fft // 2
    epsilon = 1e-8
    max_gain_db = 6.0   # limit correction strength
    smooth_bins = 12    # ~1/6 to 1/3 octave smoothing

    for ch in audio:
        f, t, Zxx = scipy.signal.stft(ch, fs=sr, nperseg=n_fft, noverlap=hop, window="hann", boundary='zeros')
        mag = np.abs(Zxx)
        phase = np.angle(Zxx)

        # Compute average power spectrum in dB
        avg_spectrum_db = 10 * np.log10(np.mean(mag**2, axis=1) + epsilon)

        # Create EQ target
        if target_curve == "pink":
            pink_ref = -3.0 * np.log10(f + epsilon)
            pink_ref -= np.max(pink_ref)
            target_db = pink_ref
        else:
            target_db = np.zeros_like(avg_spectrum_db)

        # Compute gain delta
        eq_curve_db = target_db - avg_spectrum_db
        eq_curve_db = np.clip(eq_curve_db, -max_gain_db, max_gain_db)

        # Apply smoothing
        smoothed_db = np.convolve(eq_curve_db, np.ones(smooth_bins)/smooth_bins, mode='same')

        # Convert to linear gain and apply
        gain = 10 ** (smoothed_db[:, np.newaxis] / 20)
        Zxx_eq = mag * gain * np.exp(1j * phase)

        _, ch_out = scipy.signal.istft(Zxx_eq, fs=sr, nperseg=n_fft, noverlap=hop, window="hann")

        # Match length
        if len(ch_out) > len(ch):
            ch_out = ch_out[:len(ch)]
        elif len(ch_out) < len(ch):
            ch_out = np.pad(ch_out, (0, len(ch) - len(ch_out)))

        # Preserve LUFS-like RMS level
        rms_in = np.sqrt(np.mean(ch**2))
        rms_out = np.sqrt(np.mean(ch_out**2)) + epsilon
        ch_out *= rms_in / rms_out

        matched.append(ch_out)

    return np.stack(matched, axis=0).astype(np.float32)
