# FLATLINE Spectral Curve Matching DSP
# Version: 1.0
# Purpose: Transparent spectral flattening of audio using STFT and target curve correction
# Target Behavior: Match Waves Equator "Universal Flattening" preset
# Goals for Codex:
# - Optimize CPU and memory usage
# - Suggest structure for GPU or parallel execution
# - Recommend FFT-free alternatives or more efficient DSP structures
# - Modularize if possible

import numpy as np
import scipy.signal

def match_to_target_spectrum(audio: np.ndarray, sr: int, target_curve: str = "flat") -> np.ndarray:
    matched = []
    n_fft = 2048
    hop = n_fft // 2
    epsilon = 1e-8
    max_gain_db = 6.0
    smooth_bins = 12

    for ch in audio:
        # Band-limited pre-filtering
        sos = scipy.signal.butter(2, [30, 20000], btype='bandpass', fs=sr, output='sos')
        ch = scipy.signal.sosfiltfilt(sos, ch)

        # STFT
        f, t, Zxx = scipy.signal.stft(ch, fs=sr, nperseg=n_fft, noverlap=hop, window="hann", boundary='zeros')
        mag = np.abs(Zxx)
        phase = np.angle(Zxx)

        # Log-spectrum
        avg_spectrum_db = 10 * np.log10(np.mean(mag**2, axis=1) + epsilon)

        # Reference curve
        if target_curve == "pink":
            pink_ref = -3.0 * np.log10(f + epsilon)
            pink_ref -= np.max(pink_ref)
            target_db = pink_ref
        else:
            target_db = np.zeros_like(avg_spectrum_db)

        # Delta gain
        eq_curve_db = np.clip(target_db - avg_spectrum_db, -max_gain_db, max_gain_db)
        smoothed_db = np.convolve(eq_curve_db, np.ones(smooth_bins)/smooth_bins, mode='same')

        gain = 10 ** (smoothed_db[:, np.newaxis] / 20)
        Zxx_eq = mag * gain * np.exp(1j * phase)

        # Inverse STFT
        _, ch_out = scipy.signal.istft(Zxx_eq, fs=sr, nperseg=n_fft, noverlap=hop, window="hann")

        # Trim or pad
        if len(ch_out) > len(ch):
            ch_out = ch_out[:len(ch)]
        elif len(ch_out) < len(ch):
            ch_out = np.pad(ch_out, (0, len(ch) - len(ch_out)))

        # LUFS-safe RMS matching
        rms_in = np.sqrt(np.mean(ch**2))
        rms_out = np.sqrt(np.mean(ch_out**2)) + epsilon
        ch_out *= rms_in / rms_out

        matched.append(ch_out)

    return np.stack(matched, axis=0).astype(np.float32)
