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
    # Synchronous: must complete before recorder opens the audio stream.
    # On Windows MME, opening a new stream interrupts any concurrent winsound playback.
    # on_start() already runs in its own daemon thread, so blocking 70ms is fine.
    winsound.PlaySound(_START_WAV, winsound.SND_FILENAME | winsound.SND_NODEFAULT)


def play_stop() -> None:
    _play(_STOP_WAV)


def play_cancel() -> None:
    _play(_CANCEL_WAV)
