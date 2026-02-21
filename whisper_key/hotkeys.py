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
        self._stop_armed = False  # Armed after Ctrl released post-start → next Ctrl press stops
        self._lock = threading.Lock()
        self._listener = None

    def _on_press(self, key):
        with self._lock:
            if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
                self._ctrl = True
                # Toggle stop: Ctrl press stops recording (only after being armed)
                if self._recording and self._stop_armed:
                    self._recording = False
                    self._stop_armed = False
                    logger.info('Stop hotkey: ctrl press')
                    threading.Thread(target=self._on_stop, daemon=True).start()
                    return

            elif key in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r):
                self._shift = True

            elif key in (keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt, keyboard.Key.alt_gr):
                self._alt = True
                # Toggle stop+enter: Alt press stops recording (only after being armed)
                if self._recording and self._stop_armed:
                    self._recording = False
                    self._stop_armed = False
                    logger.info('Auto-enter hotkey: alt press')
                    if self._on_auto_enter:
                        threading.Thread(target=self._on_auto_enter, daemon=True).start()
                    else:
                        threading.Thread(target=self._on_stop, daemon=True).start()
                    return

            elif key == keyboard.Key.esc and self._recording:
                self._recording = False
                self._stop_armed = False
                logger.info('Cancel hotkey: esc')
                if self._on_cancel:
                    threading.Thread(target=self._on_cancel, daemon=True).start()
                return

            # Toggle start: Ctrl+Shift starts recording
            if self._ctrl and self._shift and not self._recording:
                self._recording = True
                self._stop_armed = False
                logger.info('Start hotkey: ctrl+shift')
                threading.Thread(target=self._on_start, daemon=True).start()

    def _on_release(self, key):
        with self._lock:
            if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
                self._ctrl = False
                # Arm the stop: Ctrl was released after start → next Ctrl press will stop
                if self._recording:
                    self._stop_armed = True
                    logger.debug('Stop armed: ctrl released while recording')

            elif key in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r):
                self._shift = False

            elif key in (keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt, keyboard.Key.alt_gr):
                self._alt = False

    def start(self):
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
            suppress=False,
        )
        self._listener.start()
        logger.info('Hotkey listener started (ctrl+shift=start, ctrl=stop, alt=stop+enter, esc=cancel)')

    def stop(self):
        if self._listener:
            self._listener.stop()
            self._listener = None
        logger.info('Hotkey listener stopped')
