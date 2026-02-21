import logging
import threading
import time

import numpy as np
import sounddevice as sd

logger = logging.getLogger(__name__)

_WHISPER_RATE = 16000
_WASAPI_REOPEN_DELAY = 0.05
_POLL_INTERVAL_MS = 100


class AudioRecorder:
    def __init__(self, device=None, max_duration=300):
        self._device = device
        self._max_duration = max_duration
        self._frames = []
        self._stream = None
        self._lock = threading.Lock()
        self._recording_start = None

        self._native_rate, self._needs_resample = self._detect_device_rate(device)
        self._log_device_info(device)

    def _detect_device_rate(self, device):
        try:
            info = sd.query_devices(device) if device is not None else sd.query_devices(kind='input')
            host_name = sd.query_hostapis(info['hostapi'])['name']
            native_rate = int(info['default_samplerate'])
            needs_resample = 'wasapi' in host_name.lower() and native_rate != _WHISPER_RATE
            return native_rate, needs_resample
        except Exception as e:
            logger.warning(f'Could not detect device rate, assuming 16kHz: {e}')
            return _WHISPER_RATE, False

    def _log_device_info(self, device):
        try:
            info = sd.query_devices(device) if device is not None else sd.query_devices(kind='input')
            host_name = sd.query_hostapis(info['hostapi'])['name']
            resample_note = f' (resampling {self._native_rate}→{_WHISPER_RATE}Hz)' if self._needs_resample else ''
            logger.info(f'Audio device: {info["name"]} [{host_name}]{resample_note}')
        except Exception as e:
            logger.warning(f'Could not query device info: {e}')

    def start(self):
        with self._lock:
            self._frames = []
            self._recording_start = time.time()

        if self._needs_resample:
            time.sleep(_WASAPI_REOPEN_DELAY)

        record_rate = self._native_rate if self._needs_resample else _WHISPER_RATE

        self._stream = sd.InputStream(
            device=self._device,
            samplerate=record_rate,
            channels=1,
            dtype='float32',
            callback=self._callback,
        )
        self._stream.start()
        logger.info(f'Recording started at {record_rate}Hz')

    def _callback(self, indata, frames, time_info, status):
        if status:
            logger.warning(f'Audio callback status: {status}')
        with self._lock:
            if self._recording_start is not None:
                elapsed = time.time() - self._recording_start
                if self._max_duration and elapsed >= self._max_duration:
                    logger.warning(f'Max duration {self._max_duration}s reached')
                    return
                self._frames.append(indata.copy())

    def stop(self):
        with self._lock:
            if self._stream is None:
                return None
            self._stream.stop()
            self._stream.close()
            self._stream = None
            frames = list(self._frames)
            self._frames = []
            self._recording_start = None

        if not frames:
            logger.warning('No audio frames captured')
            return None

        audio = np.concatenate(frames, axis=0).flatten()

        if self._needs_resample:
            audio = self._resample(audio)

        duration = len(audio) / _WHISPER_RATE
        logger.info(f'Recording stopped: {duration:.2f}s')
        return audio

    def _resample(self, audio: np.ndarray) -> np.ndarray:
        try:
            import soxr
            return soxr.resample(audio, self._native_rate, _WHISPER_RATE).astype(np.float32)
        except ImportError:
            logger.error('soxr not installed — cannot resample WASAPI audio. Install with: pip install soxr')
            return audio

    def cancel(self):
        with self._lock:
            if self._stream is not None:
                self._stream.stop()
                self._stream.close()
                self._stream = None
            self._frames = []
            self._recording_start = None
        logger.info('Recording cancelled')

    @property
    def sample_rate(self):
        return _WHISPER_RATE
