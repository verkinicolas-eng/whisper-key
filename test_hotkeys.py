"""
Test unitaire des hotkeys whisper-key — mode TOGGLE
Appelle directement les handlers _on_press/_on_release (pas de simulation clavier)
"""
import sys
import time
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, 'C:/Users/nicol/Dev/whisper-key-local')

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
    status = '✅' if condition else '❌'
    line = f'{status} {name}' + (f'  [{detail}]' if detail else '')
    results.append((condition, line))
    print(line)


print('\n=== TEST HOTKEYS MODE TOGGLE whisper-key v0.1 ===\n')

# T1: Ctrl+Shift démarre l'enregistrement
l, c = make_listener()
press(l, keyboard.Key.ctrl_l, keyboard.Key.shift)
time.sleep(0.05)
check('T1: Ctrl+Shift démarre', c['start'] == 1, f"start={c['start']}")

# T2: Ctrl release ARME le stop (pas de stop immédiat)
l, c = make_listener()
press(l, keyboard.Key.ctrl_l, keyboard.Key.shift)
time.sleep(0.05)
release(l, keyboard.Key.ctrl_l)
time.sleep(0.05)
check('T2: Ctrl release arme (pas stop immédiat)',
      c['stop'] == 0 and l._stop_armed,
      f"stop={c['stop']} armed={l._stop_armed}")

# T3: Ctrl press (après armement) → stop
l, c = make_listener()
press(l, keyboard.Key.ctrl_l, keyboard.Key.shift)
time.sleep(0.05)
release(l, keyboard.Key.ctrl_l)   # arm
time.sleep(0.05)
press(l, keyboard.Key.ctrl_l)     # stop
time.sleep(0.05)
check('T3: Ctrl press arrête (après armement)',
      c['start'] == 1 and c['stop'] == 1,
      f"start={c['start']} stop={c['stop']}")

# T4: Ctrl press SANS armement = pas de stop
l, c = make_listener()
press(l, keyboard.Key.ctrl_l, keyboard.Key.shift)
time.sleep(0.05)
press(l, keyboard.Key.ctrl_l)  # ctrl held (part of combo), NOT armed → should NOT stop
time.sleep(0.05)
check('T4: Ctrl press sans armement ignoré',
      c['stop'] == 0 and l._recording,
      f"stop={c['stop']} recording={l._recording}")

# T5: Esc annule l'enregistrement en cours
l, c = make_listener()
press(l, keyboard.Key.ctrl_l, keyboard.Key.shift)
time.sleep(0.05)
press(l, keyboard.Key.esc)
time.sleep(0.05)
check('T5: Esc annule', c['cancel'] == 1, f"cancel={c['cancel']}")

# T6: Esc sans enregistrement ignoré
l, c = make_listener()
press(l, keyboard.Key.esc)
time.sleep(0.05)
check('T6: Esc sans enregistrement ignoré', c['cancel'] == 0, f"cancel={c['cancel']}")

# T7: Alt press (après armement) → stop + enter
l, c = make_listener()
press(l, keyboard.Key.ctrl_l, keyboard.Key.shift)
time.sleep(0.05)
release(l, keyboard.Key.ctrl_l)     # arm
time.sleep(0.05)
press(l, keyboard.Key.alt_l)        # alt press → auto-enter
time.sleep(0.05)
check('T7: Alt press → stop+Enter (après armement)',
      c['auto_enter'] == 1, f"auto_enter={c['auto_enter']}")

# T8: Alt press SANS armement = pas de stop
l, c = make_listener()
press(l, keyboard.Key.ctrl_l, keyboard.Key.shift)
time.sleep(0.05)
press(l, keyboard.Key.alt_l)  # alt press but NOT armed
time.sleep(0.05)
check('T8: Alt press sans armement ignoré',
      c['auto_enter'] == 0 and l._recording,
      f"auto_enter={c['auto_enter']} recording={l._recording}")

# T9: Cycle complet toggle (start → release → stop → restart)
l, c = make_listener()
press(l, keyboard.Key.ctrl_l, keyboard.Key.shift)    # cycle 1 start
time.sleep(0.05)
release(l, keyboard.Key.ctrl_l)                       # arm
release(l, keyboard.Key.shift)
time.sleep(0.05)
press(l, keyboard.Key.ctrl_l)                         # cycle 1 stop
time.sleep(0.05)
release(l, keyboard.Key.ctrl_l)
time.sleep(0.05)
press(l, keyboard.Key.ctrl_l, keyboard.Key.shift)    # cycle 2 start
time.sleep(0.05)
check('T9: Cycle complet toggle (2 starts, 1 stop)',
      c['start'] == 2 and c['stop'] == 1,
      f"start={c['start']} stop={c['stop']}")

# T10: ctrl_r + shift_l (touches droite/gauche) détectés
l, c = make_listener()
press(l, keyboard.Key.ctrl_r, keyboard.Key.shift_l)
time.sleep(0.05)
check('T10: ctrl_r + shift_l détectés', c['start'] == 1, f"start={c['start']}")

# Résumé
print(f'\n{"="*50}')
passed = sum(1 for ok, _ in results if ok)
failed = len(results) - passed
print(f'RÉSULTAT : {passed}/{len(results)} tests passés')
if failed == 0:
    print('🟢 GO — logique toggle 100% validée')
else:
    for ok, line in results:
        if not ok:
            print(f'  → {line}')
print('='*50)

sys.exit(0 if failed == 0 else 1)
