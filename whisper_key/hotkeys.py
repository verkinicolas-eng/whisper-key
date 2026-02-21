import logging
import threading
from pynput import keyboard

logger = logging.getLogger(__name__)


class HotkeyListener:
    def __init__(self, on_start, on_stop, on_cancel=None, on_auto_enter=None):
        self._on_start = on_start
        self._on_stop = on_stop
        self._on_cancel = on_cancel
        self._on_auto_enter = on_auto_enter

        self._ctrl = False
        self._shift = False
        self._alt = False
        self._recording = False
        self._lock = threading.Lock()
        self._listener = None

    def _on_press(self, key):
        with self._lock:
            if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
                self._ctrl = True
            elif key in (keyboard.Key.shift, keyboard.Key.shift_r):
                self._shift = True
            elif key in (keyboard.Key.alt_l, keyboard.Key.alt_r):
                self._alt = True
            elif key == keyboard.Key.esc and self._recording:
                self._recording = False
                logger.info('Cancel hotkey pressed')
                if self._on_cancel:
                    threading.Thread(target=self._on_cancel, daemon=True).start()
                return

            if self._ctrl and self._shift and not self._recording:
                self._recording = True
                logger.info('Start hotkey pressed: ctrl+shift')
                threading.Thread(target=self._on_start, daemon=True).start()

    def _on_release(self, key):
        with self._lock:
            if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
                self._ctrl = False
                if self._recording:
                    self._recording = False
                    logger.info('Stop modifier released: ctrl')
                    threading.Thread(target=self._on_stop, daemon=True).start()
            elif key in (keyboard.Key.shift, keyboard.Key.shift_r):
                self._shift = False
            elif key in (keyboard.Key.alt_l, keyboard.Key.alt_r):
                self._alt = False
                if self._recording:
                    self._recording = False
                    logger.info('Auto-enter hotkey: alt')
                    if self._on_auto_enter:
                        threading.Thread(target=self._on_auto_enter, daemon=True).start()
                    else:
                        threading.Thread(target=self._on_stop, daemon=True).start()

    def start(self):
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
            suppress=False,
        )
        self._listener.start()
        logger.info('Hotkey listener started (ctrl+shift=record, ctrl=stop, alt=stop+enter, esc=cancel)')

    def stop(self):
        if self._listener:
            self._listener.stop()
            self._listener = None
        logger.info('Hotkey listener stopped')
