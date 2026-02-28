"""
- handles input and output of the audio using pyaudio
- Capture audio chunks from the default microphone.
- Gracefully start and stop streams.
"""

import pyaudio
import numpy as np
from typing import Optional, Generator


class AudioStream:
    def __init__(self, rate: int = 16000, chunk: int = 1024, channels: int = 1):
        
        self.FORMAT = pyaudio.paInt16  
        self.CHANNELS = channels
        self.RATE = rate
        self.CHUNK = chunk

        self.audio = pyaudio.PyAudio()
        self.input_stream: Optional[pyaudio.Stream] = None # hold microphone stream object
        self.output_stream: Optional[pyaudio.Stream] = None # hold speaker stream object
        self.is_recording = False

    def list_devices(self):
        """Print available audio devices (useful for debugging)."""
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            print(f"{i}: {info['name']} - {info['maxInputChannels']} in, {info['maxOutputChannels']} out")

    def start_input_stream(self, device_index: Optional[int] = None):
        
        if self.input_stream is not None:
            self.stop_input_stream()

        self.input_stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=self.CHUNK,
            stream_callback=None  # blocking read mode
        )
        self.is_recording = True

    def stop_input_stream(self):
        if self.input_stream:
            self.input_stream.stop_stream()
            self.input_stream.close()
            self.input_stream = None
        self.is_recording = False

    def read_chunk(self) -> np.ndarray:
        if self.input_stream is None:
            raise RuntimeError("Input stream not started.")
        try:
            data = self.input_stream.read(self.CHUNK, exception_on_overflow=False)
        except Exception as e:
            print(f"⚠️ Audio read error: {e}")
            return np.zeros(self.CHUNK, dtype=np.int16)

        return np.frombuffer(data, dtype=np.int16)

    def generate_chunks(self) -> Generator[np.ndarray, None, None]:
        if self.input_stream is None:
            self.start_input_stream()
        while self.is_recording:
            try:
                yield self.read_chunk() # each time when main.py loop asks it gives audio chunk
            except Exception as e:
                print(f"Error reading audio chunk: {e}")
                break

    def play_audio(self, audio_data: np.ndarray):
        # Open output stream if not already open
        if self.output_stream is None:
            self.output_stream = self.audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                output=True,
                frames_per_buffer=self.CHUNK
            )
        self.output_stream.write(audio_data.tobytes())

    def play_audio_chunk(self, audio_chunk: np.ndarray):
        if self.output_stream is None:
            self.output_stream = self.audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                output=True,
                frames_per_buffer=self.CHUNK
            )
        self.output_stream.write(audio_chunk.tobytes())

    def close(self):
        self.stop_input_stream()
        if self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()
            self.output_stream = None
        self.audio.terminate()

