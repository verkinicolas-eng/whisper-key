"""Async WAV sound playback using winsound (no extra dependencies)."""
import os
import threading
import winsound

_SOUNDS_DIR = os.path.join(os.path.dirname(__file__), 'assets', 'sounds')

_START_WAV = os.path.join(_SOUNDS_DIR, 'start.wav')
_STOP_WAV = os.path.join(_SOUNDS_DIR, 'stop.wav')
_CANCEL_WAV = os.path.join(_SOUNDS_DIR, 'cancel.wav')


def _play(path: str) -> None:
    """Play WAV file in a daemon thread (non-blocking)."""
    threading.Thread(
        target=lambda: winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_NODEFAULT),
        daemon=True,
    ).start()


def play_start() -> None:
    # Async + 200ms: Windows audio device may need 80-120ms to wake from power-save.
    # A short Beep (80ms) ends before the device finishes waking -> silent.
    # 200ms guarantees the tail end is audible after wake-up (~80ms silent + 120ms heard).
    # rec.start() takes ~400ms to initialize, so the sound completes well before recording.
    threading.Thread(target=lambda: winsound.Beep(500, 200), daemon=True).start()


def play_stop() -> None:
    _play(_STOP_WAV)


def play_cancel() -> None:
    _play(_CANCEL_WAV)
