import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file (if it exists)
load_dotenv()

# Project root directory (two levels up from this file)
ROOT_DIR = Path(__file__).parent.parent.parent

# ----------------------------------------------------------------------
# Required API Keys
# ----------------------------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
reasoning_key = os.getenv("GEMINI_API_KEY")
clarify_key = os.getenv("clarify_key")
intent_key = os.getenv("intent_key")
entity_key = os.getenv("entity_key")
mom_key = os.getenv("mom_key")
sentiment_key = os.getenv("sentiment_key")
supervisor_key = os.getenv("supervisor_key")
summarizer_key = os.getenv("summarizer_key")
response_key = os.getenv("response_key")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment or .env file")

# ----------------------------------------------------------------------
# Model Configuration
# ----------------------------------------------------------------------
# Gemini model name (e.g., "gemini-1.5-flash", "gemini-1.5-pro")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Faster-Whisper model size (tiny.en, base.en, small.en, etc.)
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small.en")

# Piper TTS voice name (will be downloaded on first use)
PIPER_VOICE = str(ROOT_DIR / "src" / "voices" / "en_US-hfc_female-medium.onnx")

# ----------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------
# Directory for storing call recordings
RECORDINGS_DIR = ROOT_DIR / "recordings"
RECORDINGS_DIR.mkdir(exist_ok=True)

# Directory for storing generated Minutes of Meeting
MOM_DIR = ROOT_DIR / "mom"
MOM_DIR.mkdir(exist_ok=True)

# Log file (optional)
LOG_FILE = ROOT_DIR / "call.log"

# ----------------------------------------------------------------------
# Audio Settings
# ----------------------------------------------------------------------
SAMPLE_RATE = 16000          # Hz, for VAD/STT/TTS (Piper may use 22050 internally)
CHUNK_SIZE = 512            # frames per buffer
CHANNELS = 1                  # mono

# VAD parameters
VAD_THRESHOLD = 0.5
VAD_MIN_SPEECH_MS = 250
VAD_MIN_SILENCE_MS = 700

# ----------------------------------------------------------------------
# Debug / Development
# ----------------------------------------------------------------------
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# ----------------------------------------------------------------------
# Telephony (for future Asterisk integration)
# ----------------------------------------------------------------------
# These will be used when integrating with a phone line
ASTERISK_HOST = os.getenv("ASTERISK_HOST", "localhost")
ASTERISK_PORT = int(os.getenv("ASTERISK_PORT", "4573"))