# voice activity detection whether user is silent or speaking 

import torch
import silero_vad
import numpy as np
from typing import Optional, Callable


class VAD:

    def __init__(
        self,
        sample_rate: int = 16000,
        threshold: float = 0.5,
        min_speech_duration_ms: int = 250,
        min_silence_duration_ms: int = 700,
        on_speech_start: Optional[Callable[[], None]] = None,
        on_speech_end: Optional[Callable[[], None]] = None,
    ):
       
        self.sample_rate = sample_rate
        self.threshold = threshold
        self.min_speech_duration_ms = min_speech_duration_ms
        self.min_silence_duration_ms = min_silence_duration_ms

        self.min_speech_samples = int(sample_rate * min_speech_duration_ms / 1000)
        self.min_silence_samples = int(sample_rate * min_silence_duration_ms / 1000)

        self.model = silero_vad.load_silero_vad()

        self.triggered = False
        self.speech_start_sample = 0
        self.silence_start_sample = 0
        self.current_sample = 0  # cumulative sample count (for timing)

        self.on_speech_start = on_speech_start
        self.on_speech_end = on_speech_end

    def reset(self):
        self.triggered = False # are we currently in speech?
        self.speech_start_sample = 0
        self.silence_start_sample = 0
        self.current_sample = 0

    def process_chunk(self, audio_chunk: np.ndarray) -> bool:
        """
        Returns:
            True if currently in speech state, False otherwise.
        """
        audio_float = audio_chunk.astype(np.float32) / 32768.0

        with torch.no_grad():
            prob = self.model(torch.from_numpy(audio_float), self.sample_rate).item()

        chunk_len = len(audio_chunk)
        self.current_sample += chunk_len

        if prob >= self.threshold:
            if not self.triggered:
                # Possibly start of speech
                if self.speech_start_sample == 0:
                    self.speech_start_sample = self.current_sample - chunk_len
                # Check if we've accumulated enough speech
                speech_duration = self.current_sample - self.speech_start_sample
                if speech_duration >= self.min_speech_samples:
                    self.triggered = True
                    self.silence_start_sample = 0
                    if self.on_speech_start:
                        self.on_speech_start()
            else:
                self.silence_start_sample = 0
        else:
            if self.triggered:
                # In speech, check for silence end
                if self.silence_start_sample == 0:
                    self.silence_start_sample = self.current_sample - chunk_len
                silence_duration = self.current_sample - self.silence_start_sample
                if silence_duration >= self.min_silence_samples:
                    self.triggered = False
                    self.speech_start_sample = 0
                    if self.on_speech_end:
                        self.on_speech_end()
            else:
                self.speech_start_sample = 0

        return self.triggered
