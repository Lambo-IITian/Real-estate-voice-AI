import numpy as np
import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
from faster_whisper import WhisperModel
from typing import Optional, Union
import io
import wave


class Transcriber:

    def __init__(
        self,
        model_size: str = "small.en",
        device: str = "cpu",
        compute_type: str = "int8",
        language: Optional[str] = "en",
    ):
    
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.language = language

        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)

    def transcribe_array(
        self,
        audio: np.ndarray,
        sample_rate: int = 16000,
        initial_prompt: Optional[str] = None,
    ) -> str:
        
        audio_float = audio.astype(np.float32) / 32768.0

        # Run transcription
        segments, info = self.model.transcribe(
            audio_float,
            language=self.language,
            initial_prompt=initial_prompt,
            beam_size=1,
            best_of=1,
            patience=1,
            condition_on_previous_text=False,
            temperature=0.0,
            compression_ratio_threshold=2.4,
            no_speech_threshold=0.6,
            log_prob_threshold=-1.0,
            vad_filter=True,          # 🔥 important
            vad_parameters=dict(min_silence_duration_ms=200)
        )

        # Collect all segment texts
        text = " ".join([segment.text for segment in segments])
        return text.strip()

  


