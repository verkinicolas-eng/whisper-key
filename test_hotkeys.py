"""
Test unitaire des hotkeys whisper-key
Appelle directement les handlers _on_press/_on_release (pas de simulation clavier)
"""
import sys
import time
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, 'C:/Users/nicol/Dev/whisper-key')

from pynput import keyboard
from whisper_key.hotkeys import HotkeyListener

results = []


def make_listener():
    callbacks = {'start': 0, 'stop': 0, 'cancel': 0, 'auto_enter': 0}

    def on_start():
        callbacks['start'] += 1

    def on_stop():
        callbacks['stop'] += 1

    def on_cancel():
        callbacks['cancel'] += 1

    def on_auto_enter():
        callbacks['auto_enter'] += 1

    listener = HotkeyListener(on_start, on_stop, on_cancel, on_auto_enter)
    return listener, callbacks


def press(listener, *keys):
    for k in keys:
        listener._on_press(k)


def release(listener, *keys):
    for k in keys:
        listener._on_release(k)


def check(name, condition, detail=''):
    status = '✅ PASS' if condition else '❌ FAIL'
    line = f'{status} — {name}' + (f'  [{detail}]' if detail else '')
    results.append((status, line))
    print(line)


print('\n=== TEST HOTKEYS whisper-key v0.1 ===\n')

# T1: Ctrl+Shift démarre l'enregistrement
l, c = make_listener()
press(l, keyboard.Key.ctrl_l, keyboard.Key.shift)
time.sleep(0.05)
check('T1: Ctrl+Shift démarre l\'enregistrement', c['start'] == 1, f"start={c['start']}")

# T2: Ctrl release arrête et transcrit
l, c = make_listener()
press(l, keyboard.Key.ctrl_l, keyboard.Key.shift)
time.sleep(0.05)
release(l, keyboard.Key.ctrl_l)
time.sleep(0.05)
check('T2: Ctrl release arrête', c['start'] == 1 and c['stop'] == 1, f"start={c['start']} stop={c['stop']}")

# T3: shift_l détecté (touche gauche explicite)
l, c = make_listener()
press(l, keyboard.Key.ctrl_l, keyboard.Key.shift_l)
time.sleep(0.05)
check('T3: shift_l détecté', c['start'] == 1, f"start={c['start']}")

# T4: ctrl_r + shift_r détectés (clés droites)
l, c = make_listener()
press(l, keyboard.Key.ctrl_r, keyboard.Key.shift_r)
time.sleep(0.05)
check('T4: ctrl_r + shift_r détectés', c['start'] == 1, f"start={c['start']}")

# T5: Esc annule l'enregistrement en cours
l, c = make_listener()
press(l, keyboard.Key.ctrl_l, keyboard.Key.shift)
time.sleep(0.05)
press(l, keyboard.Key.esc)
time.sleep(0.05)
check('T5: Esc annule l\'enregistrement', c['cancel'] == 1, f"cancel={c['cancel']}")

# T6: Esc sans enregistrement est ignoré
l, c = make_listener()
press(l, keyboard.Key.esc)
time.sleep(0.05)
check('T6: Esc sans enregistrement ignoré', c['cancel'] == 0, f"cancel={c['cancel']}")

# T7: Alt release déclenche stop + Enter
l, c = make_listener()
press(l, keyboard.Key.ctrl_l, keyboard.Key.shift)
time.sleep(0.05)
press(l, keyboard.Key.alt_l)
release(l, keyboard.Key.alt_l)
time.sleep(0.05)
check('T7: Alt release = stop+Enter', c['auto_enter'] == 1, f"auto_enter={c['auto_enter']}")

# T8: Pas de double démarrage (Ctrl+Shift réappuyé pendant enregistrement)
l, c = make_listener()
press(l, keyboard.Key.ctrl_l, keyboard.Key.shift)
time.sleep(0.05)
# Simuler re-pression Ctrl+Shift pendant enregistrement → doit être ignoré
press(l, keyboard.Key.shift_r)
time.sleep(0.05)
check('T8: Pas de double démarrage', c['start'] == 1, f"start={c['start']}")

# T9: Reprise d'enregistrement après un stop complet
l, c = make_listener()
# Premier cycle
press(l, keyboard.Key.ctrl_l, keyboard.Key.shift)
time.sleep(0.05)
release(l, keyboard.Key.ctrl_l)
time.sleep(0.05)
# Relâcher shift pour état propre
release(l, keyboard.Key.shift)
# Deuxième cycle
press(l, keyboard.Key.ctrl_l, keyboard.Key.shift)
time.sleep(0.05)
check('T9: Reprise après stop possible', c['start'] == 2 and c['stop'] == 1,
      f"start={c['start']} stop={c['stop']}")

# T10: alt_gr déclenche aussi auto-enter (clavier fr/be)
l, c = make_listener()
press(l, keyboard.Key.ctrl_l, keyboard.Key.shift)
time.sleep(0.05)
press(l, keyboard.Key.alt_gr)
release(l, keyboard.Key.alt_gr)
time.sleep(0.05)
check('T10: alt_gr détecté (clavier fr/be)', c['auto_enter'] == 1, f"auto_enter={c['auto_enter']}")

# Résumé
passed = sum(1 for s, _ in results if '✅' in s)
failed = sum(1 for s, _ in results if '❌' in s)
print(f'\n{"="*45}')
print(f'RÉSULTAT : {passed}/10 tests passés')
if failed == 0:
    print('🟢 GO — logique hotkeys 100% validée')
else:
    print(f'🔴 {failed} test(s) échoué(s) — voir détails ci-dessus')
print('='*45)

sys.exit(0 if failed == 0 else 1)
