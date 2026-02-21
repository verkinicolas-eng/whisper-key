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
    # Beep() uses the Windows PC speaker API (winmm MessageBeep pathway), completely
    # independent of the audio mixer. PlaySound() can silently fail when called from
    # a pynput daemon thread at the same moment PortAudio opens the input stream.
    # Beep() is guaranteed to play regardless of audio device state.
    winsound.Beep(500, 80)  # 500 Hz, 80 ms — subtle, distinct from stop (440 Hz WAV)


def play_stop() -> None:
    _play(_STOP_WAV)


def play_cancel() -> None:
    _play(_CANCEL_WAV)
