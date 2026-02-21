import logging

import numpy as np
from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)

_MIN_DURATION_S = 0.3
_WHISPER_RATE = 16000


class Transcriber:
    def __init__(self, model='medium', device='cpu', compute_type='int8', language='fr'):
        self._language = None if language == 'auto' else language
        print(f'Loading Whisper model [{model}] on {device}/{compute_type}...')
        self._model = WhisperModel(model, device=device, compute_type=compute_type)
        print(f'  Whisper model [{model}] ready.')

    def transcribe(self, audio: np.ndarray, sample_rate: int = _WHISPER_RATE) -> str:
        if audio is None or len(audio) == 0:
            return ''

        duration = len(audio) / sample_rate
        if duration < _MIN_DURATION_S:
            logger.info(f'Audio too short ({duration:.2f}s < {_MIN_DURATION_S}s), skipping')
            return ''

        audio = audio.flatten().astype(np.float32)

        # Disable VAD for short recordings (<2s): catches single words like "oui", "non", "ok"
        # VAD can silently drop short speech if surrounded by minimal silence
        use_vad = duration >= 2.0

        segments, info = self._model.transcribe(
            audio,
            language=self._language,
            beam_size=5,
            condition_on_previous_text=False,
            vad_filter=use_vad,
            vad_parameters={'min_silence_duration_ms': 300} if use_vad else {},
            no_speech_threshold=0.8,   # default 0.6 — less aggressive rejection of short words
            log_prob_threshold=-1.5,   # default -1.0 — more tolerant for quiet/short audio
        )

        text = ' '.join(s.text.strip() for s in segments).strip()
        logger.info(f'Transcribed ({info.language} {info.language_probability:.0%}, {duration:.1f}s): "{text}"')
        return text
