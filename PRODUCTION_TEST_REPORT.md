# Rapport Test Production — whisper-key-local v0.1.0

Date : 2026-02-21
OS : Windows 11 Build 26200
Microphone : Microphone Array (AMD Audio Device) [MME] — device 3
Modèle Whisper : medium / cpu / int8 / langue fr

---

## Résumé exécutif

**Score automatisé : 10/10 ✅**
**Score manuel : À compléter par l'utilisateur (8 scénarios)**

**Correctif appliqué pendant tests** :
- `audio.device` réglé sur `3` (AMD Audio) au lieu de `null` (Voicemod virtuel)
- Ce réglage est désormais persisté dans `%APPDATA%\whisper-key\config.yaml`

---

## Correctifs pré-production (session 2026-02-21)

| # | Bug | Fix | Commit |
|---|-----|-----|--------|
| 1 | WASAPI resampling absent | Auto-detect + soxr | a624814 |
| 2 | Double-enregistrement | threading.Lock | a624814 |
| 3 | soxr absent deps | Ajouté pyproject.toml | a624814 |
| 4 | condition_on_previous_text | Ajouté transcriber.py | a624814 |
| 5 | Max duration absente | config + recorder | a624814 |
| 6 | VAD pre-check absent | vad_filter=True | a624814 |
| 7 | alt_gr absent _on_release | Fix hotkeys.py | fc2099c |
| 8 | shift_l absent _on_release | Fix hotkeys.py | fc2099c |
| 9 | Script whisper-key conflit | Désinstallé PinW v0.6.1 | session |
| 10 | device=null → Voicemod | device=3 dans config | session |

---

## Tests automatisés (10/10)

| Test | Résultat | Détail |
|------|----------|--------|
| A1: Config load | ✅ | Sections présentes |
| A2: device=3 (AMD Audio) | ✅ | Voicemod éliminé |
| A3: Log path accessible | ✅ | %APPDATA%\whisper-key\app.log |
| A4: AudioRecorder device 3 | ✅ | AMD Audio Dev [MME] |
| A5: MME (pas de resampling) | ✅ | needs_resample=False |
| A6: Modèle medium chargé | ✅ | 2.3s |
| A7: Silence 2s → '' | ✅ | VAD filtre, 0.1s |
| A8: Audio <0.3s → '' | ✅ | Guard durée min |
| A9: Fallback dir créé | ✅ | %APPDATA%\whisper-key\transcriptions |
| A10: 0 erreurs dans logs | ✅ | Aucun ERROR |

**+ Tests unitaires hotkeys (10/10)** — voir HOTKEYS_TEST_REPORT.md

---

## Performance mesurée

| Métrique | Valeur | Seuil | Status |
|----------|--------|-------|--------|
| RAM avec modèle medium chargé | ~1010 MB | < 1500 MB | ✅ |
| CPU repos (après chargement) | ~0% | < 5% | ✅ |
| Temps chargement modèle | 2.3s | < 30s | ✅ |
| Temps transcription silence | 0.1s | < 2s | ✅ |

---

## Tests manuels à valider par l'utilisateur

**Lancer whisper-key : `whisper-key`**
**Vérifier clipboard : `Get-Clipboard` dans PowerShell**

| # | Scénario | Résultat |
|---|---------|----------|
| M1 | Dictée phrase courte (10s) → `Ctrl` → coller | [ ] |
| M2 | Dictée longue (30s) → `Ctrl` → coller | [ ] |
| M3 | `Alt` release → coller + Enter automatique | [ ] |
| M4 | `Esc` pendant enregistrement → annulation propre | [ ] |
| M5 | Ctrl+Shift pendant transcription → message "⏳ Still processing" | [ ] |
| M6 | 5 transcriptions consécutives sans crash | [ ] |
| M7 | Fonctionnement dans Chrome / Discord / VS Code | [ ] |
| M8 | Bruit de fond (musique) → transcription correcte | [ ] |

### Instructions
```powershell
# Terminal 1 : lancer
whisper-key

# Terminal 2 : observer logs en direct
Get-Content $env:APPDATA\whisper-key\app.log -Wait -Tail 20

# Après chaque test, vérifier clipboard :
Get-Clipboard
```

---

## Logs de démarrage (référence)

```
2026-02-21 16:36:10 - whisper_key.recorder - INFO - Audio device: Microphone Array (AMD Audio Dev [MME]
Loading Whisper model [medium] on cpu/int8...
  Whisper model [medium] ready.
2026-02-21 16:36:12 - whisper_key.hotkeys - INFO - Hotkey listener started
🎤 whisper-key ready!
```

Aucune erreur au démarrage. ✅

---

## Verdict automatisé

🟢 **PIPELINE VALIDÉ — 10/10 composants opérationnels**

Le code est prêt pour la phase manuelle. Une fois M1-M8 validés par l'utilisateur,
la distribution publique (GitHub + PyInstaller + WinGet) peut commencer.

---

## Décision distribution

| Condition | Requis | Status |
|-----------|--------|--------|
| Tests automatisés | 10/10 | ✅ 10/10 |
| Tests hotkeys | 10/10 | ✅ 10/10 |
| Tests manuels voix | 8/8 | ⏳ à faire |
| 0 crash sur 5 min | obligatoire | ⏳ à faire |
| RAM < 1500 MB | OK | ✅ ~1010 MB |
| Copyright 100% NVK Labs | obligatoire | ✅ |
| Dual license en place | obligatoire | ✅ |

**GO pour usage personnel quotidien** ✅
**GO pour GitHub public** → après validation M1-M8
