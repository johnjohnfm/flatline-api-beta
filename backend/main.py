import numpy as np
import scipy.signal

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
        # FFT
        f, t, Zxx = scipy.signal.stft(ch, fs=sr, window=window, nperseg=n_fft, noverlap=hop, boundary='zeros')
        mag = np.abs(Zxx)
        phase = np.angle(Zxx)

        # Mean magnitude (spectral envelope)
        mean_mag = np.mean(mag, axis=1, keepdims=True)
        mean_mag[mean_mag == 0] = epsilon

        if gentle:
            # Gently nudge toward flat, not divide
            gain = 1.0 + (mag - mean_mag) / (mean_mag + epsilon)
            gain = np.clip(gain, min_gain, max_gain)
        else:
            # Hard flatten
            gain = mag / mean_mag
            gain = np.clip(gain, 0.0, 10.0)

        Zxx_flat = gain * np.exp(1j * phase)

        # Inverse FFT
        _, ch_out = scipy.signal.istft(Zxx_flat, fs=sr, window=window, nperseg=n_fft, noverlap=hop)

        # Match original length
        if len(ch_out) > len(ch):
            ch_out = ch_out[:len(ch)]
        elif len(ch_out) < len(ch):
            ch_out = np.pad(ch_out, (0, len(ch) - len(ch_out)))

        # Match LUFS/RMS energy to input
        energy_in = np.sqrt(np.mean(ch**2))
        energy_out = np.sqrt(np.mean(ch_out**2)) + epsilon
        ch_out *= energy_in / energy_out

        flattened.append(ch_out)

    return np.stack(flattened, axis=0)
