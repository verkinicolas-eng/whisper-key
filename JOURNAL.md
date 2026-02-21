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

## [2026-02-21] Validation complète + migration en production

### Phase validation (avant migration)

#### 8 tests composants
| Test | Résultat |
|------|----------|
| config.load() | OK |
| config.get_log_path() | OK |
| AudioRecorder import | OK — native_rate=44100, needs_resample=False |
| clipboard copy | OK |
| HotkeyListener import | OK |
| Transcriber chargement modèle | OK — medium/cpu/int8 |
| Transcriber + silence 2s | OK — retourne '' (VAD filtre) |
| pip install -e . | OK |

#### 10 tests hotkeys (unitaires, _on_press/_on_release directs)
- T1-T10 : 10/10 PASS
- Script : test_hotkeys.py
- Rapport : HOTKEYS_TEST_REPORT.md

#### Bugs supplémentaires trouvés pendant tests
- shift_l absent de _on_release → fix commit fc2099c
- alt et alt_gr absents de _on_release → fix commit fc2099c

### Phase migration

#### Actions effectuées
- [x] Backup ancien projet (code PinW) → whisper-key-local.BACKUP_20260221_162653
- [x] Renommage whisper-key (NVK Labs) → whisper-key-local
- [x] Copie watchdog.ps1 et launch-dev.ps1 dans nouveau projet
- [x] Réinstallation pip depuis nouveau chemin (editable, pointe C:\Users\nicol\Dev\whisper-key-local)
- [x] README.md créé
- [x] CLAUDE.md créé

#### Structure finale
```
C:\Users\nicol\Dev\
├── whisper-key-local\              ← ACTIF (code NVK Labs)
│   ├── whisper_key/ (5 modules)
│   ├── LICENSE (Dual GPLv3+Commercial)
│   ├── README.md, CLAUDE.md, JOURNAL.md
│   ├── VALIDATION_REPORT.md, HOTKEYS_TEST_REPORT.md
│   ├── watchdog.ps1, launch-dev.ps1
│   └── pyproject.toml
│
└── whisper-key-local.BACKUP_20260221_162653\  ← ARCHIVÉ (code PinW)
    └── [ne plus utiliser — supprimer après 1 semaine sans problème]
```

### Résultat
- Code 100% NVK Labs en production
- Dual license GPLv3 + Commercial prête
- Tous tests validés (18/18)
- `whisper-key` command pointe sur nouveau code

### Prochaines étapes
1. Tester en production réelle (Ctrl+Shift → parler → Ctrl)
2. Supprimer .BACKUP après 1 semaine sans problème
3. Créer repo GitHub public verkinicolas-eng/whisper-key
4. Build PyInstaller + installer.iss
5. WinGet submission
6. v0.2 : system tray, VAD temps-réel, notifications

---
