import logging
import signal
import sys
import time

from . import config
from .hotkeys import HotkeyListener
from .recorder import AudioRecorder
from .transcriber import Transcriber
from .clipboard import copy_and_paste


def _setup_logging(cfg):
    level = getattr(logging, cfg['logging']['level'], logging.INFO)
    handlers = [logging.StreamHandler(sys.stdout)]

    log_path = config.get_log_path()
    handlers.append(logging.FileHandler(log_path, encoding='utf-8'))

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers,
    )


def main():
    cfg = config.load()
    _setup_logging(cfg)
    logger = logging.getLogger(__name__)

    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    rec = AudioRecorder(
        device=cfg['audio']['device'],
        sample_rate=cfg['audio']['sample_rate'],
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

    def on_start():
        print('  🔴 Recording...', flush=True)
        rec.start()

    def on_stop(auto_enter=False):
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

    def on_cancel():
        rec.cancel()
        print('  ✗ Recording cancelled', flush=True)

    def on_auto_enter():
        on_stop(auto_enter=True)

    listener = HotkeyListener(
        on_start=on_start,
        on_stop=on_stop,
        on_cancel=on_cancel,
        on_auto_enter=on_auto_enter,
    )

    shutdown = [False]

    def handle_signal(sig, frame):
        shutdown[0] = True

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    listener.start()

    print('🎤 whisper-key ready!')
    print('   Ctrl+Shift → record  |  Ctrl → stop  |  Alt → stop+Enter  |  Esc → cancel')
    print('   Ctrl+C to quit\n', flush=True)

    logger.info('whisper-key started')

    try:
        while not shutdown[0]:
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        listener.stop()
        logger.info('whisper-key stopped')
        print('\nwhisper-key stopped.')


if __name__ == '__main__':
    main()
