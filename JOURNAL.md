# Journal de développement — whisper-key

## [2026-02-21] Création du projet from scratch

### Contexte
Objectif : dictée vocale locale Windows avec dual license GPLv3 + Commercial.
Décision de créer un nouveau projet (code 100% original, copyright NVK Labs).

### Stack choisie
- faster-whisper (MIT) — transcription locale
- sounddevice (MIT) — capture microphone
- pynput (LGPL) — global hotkeys sans admin
- pyperclip (MIT) + pyautogui (BSD-3) — clipboard et paste
- PyYAML (MIT) — configuration

### Architecture
```
whisper_key/
├── main.py        # Point d'entrée, orchestration
├── config.py      # YAML config + chemins %APPDATA%\whisper-key\
├── hotkeys.py     # Listener pynput (ctrl+shift/ctrl/alt/esc)
├── recorder.py    # AudioRecorder sounddevice
├── transcriber.py # WhisperModel faster-whisper
└── clipboard.py   # copy_and_paste avec retry exponentiel + fallback fichier
```

### Innovation clipboard
- Retry jusqu'à 5x avec backoff exponentiel (0.1s → 1.6s)
- Fallback : sauvegarde dans %APPDATA%\whisper-key\transcriptions\
- Architecture plus propre que les implémentations existantes

### Raccourcis
- Ctrl+Shift : démarrer l'enregistrement
- Ctrl (release) : arrêter + transcrire + coller
- Alt (release) : arrêter + transcrire + coller + Entrée
- Esc : annuler sans transcrire

### Prochaines étapes
- [ ] Installer et tester (`pip install -e .`)
- [ ] Valider les hotkeys pynput sur Windows
- [ ] Build PyInstaller
- [ ] README.md
- [ ] WinGet manifest
- [ ] Git init + premier push GitHub

---
