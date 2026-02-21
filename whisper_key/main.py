import logging
import signal
import socket
import sys
import threading
import time

from . import config
from .hotkeys import HotkeyListener
from .recorder import AudioRecorder
from .transcriber import Transcriber
from .clipboard import copy_and_paste
from . import sounds

_INSTANCE_PORT = 37891  # Arbitrary local port used as single-instance lock


def _acquire_instance_lock():
    """Bind to a local port to ensure only one whisper-key runs at a time."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
    try:
        sock.bind(('127.0.0.1', _INSTANCE_PORT))
        return sock  # Keep open — released when process exits
    except OSError:
        sock.close()
        return None


def _setup_logging(cfg):
    level = getattr(logging, cfg['logging']['level'], logging.INFO)
    log_path = config.get_log_path()
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_path, encoding='utf-8'),
        ],
    )


def main():
    _lock_sock = _acquire_instance_lock()
    if _lock_sock is None:
        print('whisper-key is already running. Only one instance allowed.')
        sys.exit(1)

    cfg = config.load()
    _setup_logging(cfg)
    logger = logging.getLogger(__name__)
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    rec = AudioRecorder(
        device=cfg['audio']['device'],
        max_duration=cfg['audio'].get('max_duration', 300),
    )

    trans = Transcriber(
        model=cfg['whisper']['model'],
        device=cfg['whisper']['device'],
        compute_type=cfg['whisper']['compute_type'],
        language=cfg['whisper']['language'],
    )

    fallback_dir = config.get_fallback_dir()
    auto_paste = cfg['clipboard']['auto_paste']
    max_retries = cfg['clipboard']['max_retries']

    # Guard: prevents a new recording from starting while transcription is running
    _processing = threading.Lock()

    def on_start():
        sounds.play_start()
        print('  🔴 Recording...', flush=True)
        rec.start()

    def _process(auto_enter=False):
        with _processing:
            audio = rec.stop()
            if audio is None:
                print('  ⚠ No audio captured', flush=True)
                return

            text = trans.transcribe(audio, rec.sample_rate)
            if not text:
                print('  ⚠ No speech detected', flush=True)
                return

            print(f'  ✓ "{text}"', flush=True)
            copy_and_paste(
                text,
                auto_paste=auto_paste,
                auto_enter=auto_enter,
                fallback_dir=fallback_dir,
                max_retries=max_retries,
            )

    def on_stop():
        sounds.play_stop()
        threading.Thread(target=_process, kwargs={'auto_enter': False}, daemon=True).start()

    def on_cancel():
        rec.cancel()
        sounds.play_cancel()
        print('  ✗ Recording cancelled', flush=True)

    def on_auto_enter():
        sounds.play_stop()
        threading.Thread(target=_process, kwargs={'auto_enter': True}, daemon=True).start()

    listener = HotkeyListener(
        on_start=on_start,
        on_stop=on_stop,
        on_cancel=on_cancel,
        on_auto_enter=on_auto_enter,
        can_start=lambda: not _processing.locked(),
    )

    shutdown = threading.Event()

    def handle_signal(sig, frame):
        shutdown.set()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    listener.start()

    print('🎤 whisper-key ready!')
    print('   Ctrl+Shift → start  |  Ctrl → stop+paste  |  Alt → stop+paste+Enter  |  Esc → cancel')
    print('   Ctrl+C to quit\n', flush=True)
    logger.info('whisper-key started')

    try:
        shutdown.wait()
    except KeyboardInterrupt:
        pass
    finally:
        listener.stop()
        logger.info('whisper-key stopped')
        print('\nwhisper-key stopped.')


if __name__ == '__main__':
    main()
