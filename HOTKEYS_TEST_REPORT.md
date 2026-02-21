# Rapport de tests hotkeys — whisper-key v0.1.0

Date : 2026-02-21
Méthode : Tests unitaires directs sur `HotkeyListener._on_press` / `._on_release`

---

## Bugs détectés et corrigés pendant les tests

### Bug #7 — alt_gr et alt absents de `_on_release`
- **Sévérité :** Majeur
- **Symptôme :** Alt Gr (clavier fr/be) ne déclenchait pas stop+Enter
- **Fix :** Ajouté `keyboard.Key.alt` et `keyboard.Key.alt_gr` dans le tuple de `_on_release`
- **Status :** ✅ Corrigé

### Bug #8 — shift_l absent de `_on_release`
- **Sévérité :** Mineur
- **Symptôme :** Shift gauche restait "coincé" dans `_shift=True` après relâchement
- **Fix :** Ajouté `keyboard.Key.shift_l` dans le tuple `_on_release`
- **Status :** ✅ Corrigé

---

## Résultats des tests

| # | Test | Résultat |
|---|------|----------|
| T1 | Ctrl+Shift démarre l'enregistrement | ✅ PASS |
| T2 | Ctrl release arrête et déclenche transcription | ✅ PASS |
| T3 | shift_l (touche gauche explicite) détecté | ✅ PASS |
| T4 | ctrl_r + shift_r (touches droites) détectés | ✅ PASS |
| T5 | Esc annule l'enregistrement en cours | ✅ PASS |
| T6 | Esc sans enregistrement actif est ignoré | ✅ PASS |
| T7 | Alt release = stop + coller + Enter | ✅ PASS |
| T8 | Pas de double démarrage (Ctrl+Shift réappuyé pendant enregistrement) | ✅ PASS |
| T9 | Reprise d'enregistrement possible après un stop complet | ✅ PASS |
| T10 | Alt Gr détecté (clavier fr/be) | ✅ PASS |

**Score : 10/10**

---

## Verdict

🟢 **GO — Logique hotkeys validée à 100%**

Tous les cas nominaux et les cas limites passent.
Le nouveau `whisper-key` peut remplacer `whisper-key-local` pour l'usage personnel.

---

## Hotkeys validés

| Combinaison | Action |
|-------------|--------|
| Ctrl+Shift (appui) | Démarre l'enregistrement |
| Ctrl (relâche) | Arrête + transcrit + colle |
| Alt / Alt Gr (relâche) | Arrête + transcrit + colle + Enter |
| Esc (pendant enregistrement) | Annule sans transcrire |
| Ctrl+Shift (pendant transcription) | Ignoré (guard `_processing`) |
