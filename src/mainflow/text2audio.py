from piper import PiperVoice
from pathlib import Path
from typing import Optional
import numpy as np
from configs import settings


class Synthesizer:
    def __init__(self, model_path: Optional[str] = None):

        if model_path:
            model_file = Path(model_path)
        else:
            model_file = Path(settings.PIPER_VOICE)

        if not model_file.exists():
            raise FileNotFoundError(
                f"Voice model not found at: {model_file}"
            )

        self.voice = PiperVoice.load(str(model_file))
        self.voice.config.length_scale = 0.8
        self.sample_rate = self.voice.config.sample_rate
        self._stop_flag = False

    def stop(self):
        self._stop_flag = True

    def synthesize_stream(self, text: str, chunk_callback):
        self._stop_flag = False

        try:
            for chunk in self.voice.synthesize(text):

                if self._stop_flag:
                    break

                # Piper chunk structure
                chunk_np = chunk.audio_int16_array
                chunk_np = np.asarray(chunk_np, dtype=np.int16)

                chunk_callback(chunk_np)

        except Exception as e:
            print(f"TTS error: {e}")