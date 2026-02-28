"""
audio_utils.py - Audio conversion utilities.

Provides functions to:
- Convert between mulaw and PCM (16-bit linear).
- Resample audio.
- Save/load audio to/from WAV files.
- Convert between numpy arrays and bytes.
"""

import numpy as np
import wave
import audioop
from pydub import AudioSegment
from typing import Union, BinaryIO
import io


# ------------------- Mulaw <-> PCM Conversion -------------------

def mulaw_to_pcm(mulaw_bytes: bytes) -> np.ndarray:
    """
    Convert mu-law encoded bytes to 16-bit linear PCM numpy array.

    Args:
        mulaw_bytes: Raw mu-law bytes (e.g., from Twilio/Asterisk).

    Returns:
        numpy array of int16 samples (PCM).
    """
    # audioop's mulaw to linear conversion returns bytes of 16-bit samples
    pcm_bytes = audioop.ulaw2lin(mulaw_bytes, 2)  # 2 bytes per sample (16-bit)
    pcm = np.frombuffer(pcm_bytes, dtype=np.int16)
    return pcm


def pcm_to_mulaw(pcm: np.ndarray) -> bytes:
    """
    Convert 16-bit linear PCM numpy array to mu-law bytes.

    Args:
        pcm: numpy array of int16 samples.

    Returns:
        Raw mu-law bytes.
    """
    # Convert numpy array to bytes
    pcm_bytes = pcm.astype(np.int16).tobytes()
    # audioop's linear to mulaw conversion
    mulaw_bytes = audioop.lin2ulaw(pcm_bytes, 2)
    return mulaw_bytes


# ------------------- Resampling -------------------

def resample(
    audio: np.ndarray,
    orig_sr: int,
    target_sr: int,
    dtype: type = np.int16
) -> np.ndarray:
    """
    Resample audio from orig_sr to target_sr using pydub (simple quality).

    Args:
        audio: numpy array of samples.
        orig_sr: Original sample rate.
        target_sr: Desired sample rate.
        dtype: Data type of the output array (default np.int16).

    Returns:
        Resampled audio as numpy array.
    """
    # Convert numpy to AudioSegment
    audio_bytes = audio.astype(dtype).tobytes()
    seg = AudioSegment(
        data=audio_bytes,
        sample_width=2,  # 16-bit
        frame_rate=orig_sr,
        channels=1
    )
    # Resample
    resampled = seg.set_frame_rate(target_sr)
    # Convert back to numpy
    samples = np.frombuffer(resampled.raw_data, dtype=dtype)
    return samples


# ------------------- File I/O -------------------

def save_wav(
    audio: np.ndarray,
    filename: str,
    sample_rate: int = 16000,
    dtype: type = np.int16
):
    """
    Save numpy array as a WAV file.

    Args:
        audio: numpy array of samples.
        filename: Output file path.
        sample_rate: Sample rate in Hz.
        dtype: Data type (should match audio.dtype).
    """
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 2 bytes for int16
        wf.setframerate(sample_rate)
        wf.writeframes(audio.astype(dtype).tobytes())


def load_wav(filename: str) -> (np.ndarray, int):
    """
    Load a WAV file and return (samples, sample_rate).

    Args:
        filename: Path to WAV file.

    Returns:
        Tuple of (numpy array of int16 samples, sample_rate).
    """
    with wave.open(filename, 'rb') as wf:
        sample_rate = wf.getframerate()
        n_frames = wf.getnframes()
        audio_bytes = wf.readframes(n_frames)
        samples = np.frombuffer(audio_bytes, dtype=np.int16)
    return samples, sample_rate


# ------------------- Byte <-> Numpy -------------------

def bytes_to_pcm(audio_bytes: bytes, dtype: type = np.int16) -> np.ndarray:
    """Convert raw PCM bytes to numpy array."""
    return np.frombuffer(audio_bytes, dtype=dtype)


def pcm_to_bytes(pcm: np.ndarray) -> bytes:
    """Convert numpy PCM array to bytes."""
    return pcm.astype(np.int16).tobytes()
