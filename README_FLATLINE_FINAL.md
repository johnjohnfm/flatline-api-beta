[![Deployed](https://img.shields.io/badge/deployed-yes-black)](https://flatline-api-beta.onrender.com)
[![License](https://img.shields.io/badge/license-CUSTOM-yellow)](LICENSE.txt)
[![Engine](https://img.shields.io/badge/engine-FLATLINE-blue)](https://johnjohnfm.uk)
[![Version](https://img.shields.io/badge/version-v1.0.0-informational)]()
[![Status](https://img.shields.io/badge/status-STABLE-brightgreen)]()

---

#### AUTHENTIC AUDIO | ENGINEERED FOR SOUND

FLATLINE is not a filter.  
It is a surgical-grade neutralizer—built for tonal truth and high-fidelity flattening.  
Every element in this repo adheres to the AUTHENTIC AUDIO engineering standard:  
**Function. Clarity. Tactility. Performance.**

---
# FLATLINE — AUTHENTIC AUDIO Web API  
*A real-time frequency neutralization tool engineered for absolute tonal integrity.*

[![Render Status](https://img.shields.io/badge/deployed-yes-green)](https://flatline-api-beta.onrender.com)
[![License](https://img.shields.io/badge/license-Custom-orange)](LICENSE.txt)

---

## 🧠 Overview

FLATLINE is a precision audio processor designed to **neutralize spectral tilt** in WAV files — perfect for pre-master balancing, post-mix cleanup, and automated tone correction.

Inspired by **Waves Equator**, FLATLINE applies a **transparent, smoothed spectral curve** that gently reshapes your mix without compression artifacts, distortion, or tonal damage.

Built for producers, engineers, and AI audio researchers who need fast, high-fidelity flattening on demand.

---

## ⚙️ Core Features

- ✅ Spectral flattening with **transparent EQ logic**
- 🎛️ Mimics **Waves Equator** with smoothed ±6dB correction
- 🎚️ LUFS-safe (no gain/level shift)
- 🧼 No dynamic compression or destructive filtering
- 🎧 Native support for WAV, FLAC, AIFF (mono + stereo)
- ⚡️ FastAPI-powered, deployable in seconds
- 🌐 Frontend widget designed to integrate seamlessly with AUTHENTIC AUDIO workflows

---

## 🔬 DSP Overview

1. Converts audio to STFT (Short-Time Fourier Transform)
2. Computes the average spectral curve
3. Calculates the difference from a reference curve (e.g. flat, pink)
4. Applies smoothed EQ-style gain correction (±6dB max)
5. Reconstructs audio with original phase and matched LUFS

**No whitening. No multiband compression. No gimmicks. Just balance.**

---

## 🧰 API Usage

### 🔊 `/neutralize/`

Upload a file and receive a flattened version in return.

**Request**  
`POST /neutralize/`  
Content-Type: `multipart/form-data`

**Form Field**
- `file`: your audio file (.wav, .aiff, .flac)

**Example:**

```bash
curl -F "file=@your_mix.wav" https://flatline-api-beta.onrender.com/neutralize/ -o flatlined.wav
```

---

## 🚀 Local Setup

```bash
git clone https://github.com/YOUR_USERNAME/flatline-api.git
cd flatline-api
pip install -r requirements.txt
uvicorn main:app --reload --port 10000
```

Then test it locally via:
```bash
curl -F "file=@your_mix.wav" http://localhost:10000/neutralize/ -o flatlined.wav
```

---

## 🛠 Tech Stack

- Python 3.11+
- FastAPI
- NumPy / SciPy / SoundFile
- CORS-enabled for frontend widgets
- Deployed via [Render](https://render.com)

---

## 🗂 File Layout

```bash
├── main.py            # API and DSP engine
├── flatline_ui_final.js  # Widget interaction logic (refactored)
├── index.html         # Web UI
├── style_refactored.css # AUTHENTIC AUDIO compliant UI styles
├── requirements.txt   # Dependencies
├── render.yaml        # Render deployment config
├── LICENSE.txt        # Custom license (© JOHNJOHNFM)
```

---

## 📜 License

© 2025 **JOHN E. REYNOLDS / JOHNJOHNFM**  
All rights reserved.  
This repository is published under a [custom license](LICENSE.txt) and may not be copied, sold, or redistributed without permission.

---

## 🤝 Acknowledgments

Built using 🧠 and ears.  
Inspired by **Waves Equator**, **Tonelux Tilt**, and the pursuit of spectral truth.

> “Define your code. Design your sound.” — [johnjohnfm.uk](https://johnjohnfm.uk)
