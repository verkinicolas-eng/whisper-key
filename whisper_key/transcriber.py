import logging
import numpy as np
from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)

_MIN_DURATION_S = 0.3


class Transcriber:
    def __init__(self, model='medium', device='cpu', compute_type='int8', language='fr'):
        self._language = language if language != 'auto' else None
        logger.info(f'Loading Whisper model: {model} ({device}, {compute_type})')
        self._model = WhisperModel(model, device=device, compute_type=compute_type)
        logger.info('Whisper model ready')

    def transcribe(self, audio: np.ndarray, sample_rate: int) -> str:
        duration = len(audio) / sample_rate
        if duration < _MIN_DURATION_S:
            logger.info(f'Audio too short ({duration:.2f}s), skipping')
            return ''

        logger.info(f'Transcribing {duration:.2f}s of audio...')
        segments, info = self._model.transcribe(
            audio,
            language=self._language,
            beam_size=5,
            vad_filter=True,
            vad_parameters={'min_silence_duration_ms': 300},
        )
        text = ' '.join(s.text.strip() for s in segments).strip()
        lang = info.language
        conf = info.language_probability
        logger.info(f'Transcription done: lang={lang} ({conf:.0%}) → "{text}"')
        return text
