# Features checklist — whisper-key nouveau vs ancien

## Critiques (OBLIGATOIRES)

- [x] **Hotkeys globaux**
  - Ctrl+Shift démarre l'enregistrement
  - Ctrl (release) arrête et transcrit
  - Alt (release) arrête + transcrit + Enter
  - Esc annule
  - Fonctionne en arrière-plan via pynput global listener
  - Guard `_processing` : impossible de démarrer pendant transcription

- [x] **Capture audio**
  - Détecte microphone par défaut Windows
  - Détection automatique WASAPI → resampling via soxr si nécessaire
  - Support MME (pas de resampling nécessaire)
  - Max duration configurable (300s par défaut)

- [x] **Transcription Whisper**
  - faster-whisper, modèle medium par défaut
  - `condition_on_previous_text=False` → pas d'hallucinations
  - Language auto-detect ou forcé (fr par défaut)
  - Durée min 0.3s → skip si trop court

- [x] **Clipboard handling**
  - Texte copié + Ctrl+V simulé automatiquement
  - Retry exponentiel (5 tentatives : 0.1→1.6s)
  - Fallback fichier si retry échoue (`%APPDATA%\whisper-key\transcriptions\`)
  - Logs détaillés à chaque étape

- [x] **VAD (Voice Activity Detection)**
  - Intégré dans faster-whisper (`vad_filter=True`)
  - Ne transcrit pas le silence → résultat vide = aucune action
  - Paramètre `min_silence_duration_ms=300`

- [x] **Configuration YAML**
  - Fichier persistant dans `%APPDATA%\whisper-key\config.yaml`
  - Valeurs par défaut si absent
  - Sections : hotkeys, whisper, audio, clipboard, logging

- [x] **Robustesse**
  - Lock `_processing` : pas de double traitement
  - Thread daemon pour transcription : n'empêche pas le shutdown
  - Logs dans `%APPDATA%\whisper-key\app.log`
  - Cancel propre via `rec.cancel()`

## Améliorations vs ancien (BONUS)

- [x] **Architecture modulaire** : 5 fichiers clairs vs monolithe 14+ fichiers
- [x] **Copyright 100% NVK Labs** : dual license GPLv3 + Commercial
- [x] **pynput** : cross-platform, pas besoin de global-hotkeys Windows-only
- [x] **WASAPI auto-detect** : fallback transparent, plus robuste
- [x] **Config YAML** plus lisible que JSON
- [ ] Notifications système (à faire en v0.2)
- [ ] System tray icon (à faire en v0.2)
- [ ] VAD temps-réel auto-stop sur silence (à faire en v0.2)
- [ ] WinGet distribution (à faire après build PyInstaller)
