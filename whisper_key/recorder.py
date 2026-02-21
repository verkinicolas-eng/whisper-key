import logging
import threading
import numpy as np
import sounddevice as sd

logger = logging.getLogger(__name__)


class AudioRecorder:
    def __init__(self, device=None, sample_rate=16000):
        self._device = device
        self._sample_rate = sample_rate
        self._frames = []
        self._stream = None
        self._lock = threading.Lock()

    def start(self):
        with self._lock:
            self._frames = []
            self._stream = sd.InputStream(
                device=self._device,
                samplerate=self._sample_rate,
                channels=1,
                dtype='float32',
                callback=self._callback,
            )
            self._stream.start()
        logger.info(f'Recording started (device={self._device}, rate={self._sample_rate}Hz)')

    def _callback(self, indata, frames, time, status):
        if status:
            logger.warning(f'Audio callback status: {status}')
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

        if not frames:
            logger.warning('No audio frames captured')
            return None

        audio = np.concatenate(frames, axis=0).flatten()
        duration = len(audio) / self._sample_rate
        logger.info(f'Recording stopped: {duration:.2f}s of audio')
        return audio

    def cancel(self):
        with self._lock:
            if self._stream is not None:
                self._stream.stop()
                self._stream.close()
                self._stream = None
            self._frames = []
        logger.info('Recording cancelled')

    @property
    def sample_rate(self):
        return self._sample_rate
