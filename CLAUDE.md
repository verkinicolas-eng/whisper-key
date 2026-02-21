# whisper-key — Claude Code Context

## Projet
Speech-to-text local pour Windows 11. Code 100% NVK Labs (Nicolas Verki).
**Pas de code PinW ici.** L'ancien projet PinW est archivé dans whisper-key-local.BACKUP_20260221_162653.

## Localisation
- Repo actif : `C:\Users\nicol\Dev\whisper-key-local\`
- Config runtime : `%APPDATA%\whisper-key\config.yaml`
- Logs : `%APPDATA%\whisper-key\app.log`
- Transcriptions fallback : `%APPDATA%\whisper-key\transcriptions\`

## Architecture (5 modules)
```
whisper_key/
├── config.py       YAML config + chemins %APPDATA%
├── hotkeys.py      pynput listener global (Ctrl+Shift, Ctrl, Alt, Esc)
├── recorder.py     sounddevice + détection WASAPI + resampling soxr
├── transcriber.py  faster-whisper medium/cpu/int8 + VAD filter
├── clipboard.py    retry 5x exponentiel + fallback fichier
└── main.py         orchestration + guard _processing
```

## Hotkeys
- `Ctrl+Shift` : démarre l'enregistrement
- `Ctrl` (release) : arrête + transcrit + colle
- `Alt` / `AltGr` (release) : arrête + transcrit + colle + Enter
- `Esc` : annule sans transcrire

## Micro (important)
- Micro par défaut = Voicemod (virtuel, ne capte rien)
- Forcer device 3 (AMD Audio) dans config si problème audio :
  ```yaml
  audio:
    device: 3
  ```

## Commandes utiles
```powershell
# Lancer
whisper-key

# Lancer avec watchdog (relance auto si crash)
.\watchdog.ps1

# Tests hotkeys
python -X utf8 test_hotkeys.py

# Réinstaller après modif
pip install -e . --break-system-packages
```

## État validé (2026-02-21)
- 8 tests composants : OK
- 10 tests hotkeys : 10/10
- Bugs corrigés : WASAPI resampling, double-enregistrement, soxr deps,
  condition_on_previous_text, max_duration, VAD filter,
  shift_l release, alt_gr release

## Prochaine session
1. Test en production (parler → Ctrl → vérifier clipboard)
2. Créer repo GitHub public `verkinicolas-eng/whisper-key`
3. Build PyInstaller + installer.iss
4. WinGet submission
5. v0.2 : system tray, VAD temps-réel, notifications

## Licence
Dual : GPLv3 (particuliers) + Commercial €49/siège (entreprises)
Copyright (c) 2026 Nicolas Verki (NVK Labs)
