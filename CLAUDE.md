# whisper-key — Claude Code Context

## Session précédente : 2026-02-21 (COMPLÈTE)

### Ce qui a été fait
1. Analyse juridique → code PinW non exploitable pour dual license → réécriture from scratch
2. Architecture 6 modules créée (config, hotkeys, recorder, transcriber, clipboard, sounds)
3. Bugs critiques fixés :
   - Audio deadlock (stop() libère lock avant stream.stop())
   - Hotkeys toggle (flag _stop_armed)
   - Ghost recording (can_start callback avant _recording=True)
   - VAD mots courts (désactivé pour audio <2s)
   - Sons WAV discrets générés (520/440/360 Hz)
   - **Triple paste (3 instances simultanées)** → single-instance lock port 37891
4. GitHub public créé, Release v0.1.0 publiée

### État actuel
- **GitHub** : https://github.com/verkinicolas-eng/whisper-key
- **Release** : v0.1.0 publiée
- **Bugs restants** : triple paste CORRIGÉ (single-instance lock), mots courts ("oui") à valider
- **Tests manuels voix** : T1-T7 du PRODUCTION_FINAL_REPORT.md à compléter

### Prochaine session
1. Tester mots courts ("oui", "non") après fix no_speech_threshold + log_prob_threshold
2. Tests manuels T1-T7 complets
3. Commit final + communication (Reddit, HN)
4. Build PyInstaller + WinGet manifest

---

## Projet
Speech-to-text local pour Windows 11. Code 100% NVK Labs (Nicolas Verki).
**Pas de code PinW ici.** L'ancien projet PinW est archivé dans whisper-key-local.BACKUP_20260221_162653.

## Localisation
- Repo actif : `C:\Users\nicol\Dev\whisper-key-local\`
- Config runtime : `%APPDATA%\whisper-key\config.yaml`
- Logs : `%APPDATA%\whisper-key\app.log`
- Transcriptions fallback : `%APPDATA%\whisper-key\transcriptions\`

## Architecture (6 modules)
```
whisper_key/
├── config.py       YAML config + chemins %APPDATA%
├── hotkeys.py      pynput listener global (Ctrl+Shift, Ctrl, Alt, Esc) + can_start callback
├── recorder.py     sounddevice + détection WASAPI + resampling soxr
├── transcriber.py  faster-whisper medium/cpu/int8 + VAD adaptatif (<2s=off, >=2s=on)
├── clipboard.py    retry 5x exponentiel + fallback fichier
├── sounds.py       WAV discrets via winsound.PlaySound (520/440/360 Hz)
└── main.py         orchestration + single-instance lock (port 37891) + can_start guard
```

## Hotkeys (mode TOGGLE)
- `Ctrl+Shift` : démarre l'enregistrement (beep start.wav)
- `Ctrl` release puis `Ctrl` press : arrête + transcrit + colle (beep stop.wav)
- `Alt` press (après arm) : arrête + transcrit + colle + Enter (beep stop.wav)
- `Esc` : annule sans transcrire (beep cancel.wav)

## Micro (important)
- Micro par défaut = Voicemod (virtuel, ne capte rien)
- Forcer device 3 (AMD Audio) dans config :
  ```yaml
  audio:
    device: 3
  ```

## Pièges connus
- **JAMAIS lancer `whisper-key &` en background** → multiple instances → triple paste
- Le single-instance lock (port 37891) prévient le problème mais éviter quand même
- Si "encore running" après Ctrl+C : vérifier qu'aucun python avec whisper ne tourne

## Commandes utiles
```powershell
# Lancer (TOUJOURS en foreground, jamais &)
whisper-key

# Vérifier instances actives
netstat -ano | findstr 37891

# Tuer toutes instances si bloqué
taskkill /F /IM python.exe

# Logs live
Get-Content $env:APPDATA\whisper-key\app.log -Wait -Tail 30

# Tests hotkeys
python -X utf8 test_hotkeys.py

# Réinstaller après modif
pip install -e . --break-system-packages
```

## Licence
Dual : GPLv3 (particuliers) + Commercial €49/siège (entreprises)
Copyright (c) 2026 Nicolas Verki (NVK Labs)
