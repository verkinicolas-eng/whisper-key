# Journal de développement — whisper-key

## [2026-02-21 session 2] Fix sons + hotkeys

### Bugs corrigés
- [x] **Hotkeys double-fire** : Windows envoie un double événement Ctrl → après stop, _shift=True + 2ème Ctrl déclenchait un start parasite. Fix : `return` inconditionnel après la branche Ctrl dans `_on_press`.
- [x] **Son start silencieux** : périphérique audio en veille au moment du start → PlaySound/Beep trop courts pour survivre au wake-up (~120ms). Fix : start.wav contient 150ms de silence en pré-roll (device se réveille pendant le silence, puis la note joue).
- [x] **Son start "bip aigu"** : remplacé par sine 460Hz/70ms avec fade 8ms, même caractère que stop (440Hz). Deux "tocs" discrets et cohérents.

### Sons finaux
| Son | Fréquence | Durée | Pré-roll |
|-----|-----------|-------|---------|
| start.wav | 460Hz | 70ms | 150ms silence |
| stop.wav | 440Hz | 70ms | aucun |
| cancel.wav | 360Hz | 50ms | aucun |

### Commits
- `3c890bf` : fix sons start/stop en toc discret (sine+fade, pre-roll 150ms)

### État
- sons : ✅ toc discret start et stop
- hotkeys : ✅ toggle fiable, pas de double-fire
- single-instance lock : ✅ port 37891
- Tests manuels T1-T7 : ⏳ à compléter

---

## [2026-02-21] PUBLIC RELEASE v0.1.0

### Actions
- [x] Fix ghost recording (can_start callback dans HotkeyListener)
- [x] Fix VAD mots courts (<2s, vad_filter=False)
- [x] Remplacement winsound.Beep par WAV discrets (520/440/360 Hz)
- [x] Commit final + tag v0.1.0
- [x] Création repo GitHub public
- [x] Push code + tags
- [x] Release v0.1.0 publiée
- [x] Badges ajoutés au README

### Résultat
- whisper-key v0.1.0 PUBLIC : https://github.com/verkinicolas-eng/whisper-key
- Code 100% NVK Labs, dual license GPLv3 + Commercial
- 9/9 tests automatisés + 2 bugs critiques fixés

### Métriques finales
- Tests production : 9/9
- Bugs critiques fixés : 2/2 (ghost recording, VAD courts)
- Architecture : 6 modules propres (config, hotkeys, recorder, transcriber, clipboard, sounds)
- Commits : 7

### Prochaines étapes
1. Tests manuels voix (T1-T7 du PRODUCTION_FINAL_REPORT)
2. Communication (r/Python, r/LocalLLaMA)
3. WinGet manifest
4. PyInstaller build + installer
5. v0.2 : system tray, notifications Windows

---

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
