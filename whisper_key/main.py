import logging
import signal
import sys
import threading
import time
import winsound

from . import config
from .hotkeys import HotkeyListener
from .recorder import AudioRecorder
from .transcriber import Transcriber
from .clipboard import copy_and_paste


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


def _beep(freq, duration_ms):
    threading.Thread(target=lambda: winsound.Beep(freq, duration_ms), daemon=True).start()


def main():
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
        if _processing.locked():
            print('  ⏳ Still processing previous recording, please wait...', flush=True)
            return
        _beep(1000, 150)
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
        _beep(800, 150)
        threading.Thread(target=_process, kwargs={'auto_enter': False}, daemon=True).start()

    def on_cancel():
        rec.cancel()
        _beep(600, 100)
        print('  ✗ Recording cancelled', flush=True)

    def on_auto_enter():
        _beep(800, 150)
        threading.Thread(target=_process, kwargs={'auto_enter': True}, daemon=True).start()

    listener = HotkeyListener(
        on_start=on_start,
        on_stop=on_stop,
        on_cancel=on_cancel,
        on_auto_enter=on_auto_enter,
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
