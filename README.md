# whisper-key

[![Release](https://img.shields.io/github/v/release/verkinicolas-eng/whisper-key)](https://github.com/verkinicolas-eng/whisper-key/releases)
[![License](https://img.shields.io/badge/license-GPLv3%20%2F%20Commercial-blue)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-brightgreen)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Windows-orange)](https://www.microsoft.com/windows)
[![Stars](https://img.shields.io/github/stars/verkinicolas-eng/whisper-key?style=social)](https://github.com/verkinicolas-eng/whisper-key)

**Local, private speech-to-text for Windows with global hotkeys.**

Dictate text anywhere on your PC using keyboard shortcuts. Everything runs locally — no cloud, no subscription, no data sent anywhere.

---

## Features

- **Ctrl+Shift** to start recording
- **Ctrl** (release) to stop and paste transcribed text
- **Alt** (release) to stop, paste, and press Enter
- **Esc** to cancel
- Powered by [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (CTranslate2)
- WASAPI auto-detection with soxr resampling
- VAD filter — silence returns nothing, no hallucinations
- Clipboard retry with exponential backoff + file fallback
- YAML config in `%APPDATA%\whisper-key\config.yaml`

---

## Install

```
pip install whisper-key
whisper-key
```

Or from source:
```
git clone https://github.com/verkinicolas-eng/whisper-key
cd whisper-key
pip install -e .
whisper-key
```

---

## Usage

Launch `whisper-key` in a terminal (or set it to auto-start).

| Shortcut | Action |
|----------|--------|
| Ctrl+Shift | Start recording |
| Ctrl (release) | Stop + transcribe + paste |
| Alt / AltGr (release) | Stop + transcribe + paste + Enter |
| Esc | Cancel recording |

---

## Configuration

Edit `%APPDATA%\whisper-key\config.yaml` (created on first run):

```yaml
whisper:
  model: medium      # tiny, base, small, medium, large-v3
  device: cpu        # cpu or cuda
  compute_type: int8
  language: fr       # language code or null for auto-detect

audio:
  device: null       # null = default microphone
  max_duration: 300  # max recording seconds

clipboard:
  auto_paste: true
  max_retries: 5
```

---

## License

Dual license:
- **GPLv3** for individuals, students, and open-source projects (free)
- **Commercial** for businesses (€49/seat) — contact via GitHub Discussions

Copyright (c) 2026 Nicolas Verki (NVK Labs)

---

## Architecture

5 focused modules:

| File | Role |
|------|------|
| `config.py` | YAML config, paths |
| `hotkeys.py` | pynput global listener |
| `recorder.py` | sounddevice + WASAPI/soxr |
| `transcriber.py` | faster-whisper + VAD |
| `clipboard.py` | retry + file fallback |
| `main.py` | orchestration |
