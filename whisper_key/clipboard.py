import logging
import os
import time
from datetime import datetime

import pyperclip
import pyautogui

logger = logging.getLogger(__name__)

_PASTE_DELAY = 0.05


def copy_and_paste(text: str, auto_paste: bool = True, auto_enter: bool = False,
                   fallback_dir: str = None, max_retries: int = 5) -> bool:
    if not text:
        return False

    if not _copy_with_retry(text, max_retries, fallback_dir):
        return False

    if auto_paste or auto_enter:
        time.sleep(_PASTE_DELAY)
        pyautogui.hotkey('ctrl', 'v')
        logger.info('Auto-pasted via Ctrl+V')

    if auto_enter:
        time.sleep(_PASTE_DELAY)
        pyautogui.press('enter')
        logger.info('Auto-enter sent')

    return True


def _copy_with_retry(text: str, max_retries: int, fallback_dir: str) -> bool:
    for attempt in range(max_retries):
        try:
            pyperclip.copy(text)
            logger.info(f'Copied to clipboard ({len(text)} chars)')
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                wait = 0.1 * (2 ** attempt)
                logger.warning(f'Clipboard locked (attempt {attempt+1}/{max_retries}), retry in {wait:.1f}s: {e}')
                time.sleep(wait)
            else:
                logger.error(f'Clipboard inaccessible after {max_retries} attempts: {e}')

    if fallback_dir:
        _save_to_file(text, fallback_dir)
    return False


def _save_to_file(text: str, fallback_dir: str):
    try:
        os.makedirs(fallback_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        path = os.path.join(fallback_dir, f'transcription_{timestamp}.txt')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
        logger.warning(f'Clipboard unavailable → saved to {path}')
        print(f'  ⚠ Transcription saved to {path}')
    except Exception as e:
        logger.error(f'Failed to save transcription to file: {e}')
