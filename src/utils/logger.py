"""
logger.py - Colored terminal logger for the AI assistant.

Provides a simple logging interface with different colors for:
- User input
- AI responses
- Agent outputs (intent, entities, sentiment)
- System info
- Errors
- MoM generation
"""

import sys
import time
from datetime import datetime
from typing import Optional

# Try to import colorama; if not available, fallback to no colors
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)  # initialize colorama
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False
    # Create dummy color classes
    class Fore:
        BLACK = CYAN = GREEN = YELLOW = RED = MAGENTA = BLUE = WHITE = RESET = ''
    class Back:
        BLACK = CYAN = GREEN = YELLOW = RED = MAGENTA = BLUE = WHITE = RESET = ''
    class Style:
        BRIGHT = DIM = NORMAL = RESET_ALL = ''


class Logger:
    """
    A simple logger with colored output.

    Usage:
        logger = Logger(debug=True)
        logger.info("System ready")
        logger.user("Hello, I need help")
        logger.ai("I can help you")
        logger.agent("Intent", "order_inquiry")
        logger.error("Something went wrong")
    """

    def __init__(self, debug: bool = False, log_to_file: Optional[str] = None):
        """
        Initialize logger.

        Args:
            debug: If True, print debug messages.
            log_to_file: Optional path to a log file. If provided, all output
                         is also appended to this file (without colors).
        """
        self.debug_mode = debug
        self.log_file = log_to_file
        if log_to_file:
            # Ensure directory exists? We'll assume it's handled elsewhere.
            pass

    def _write(self, message: str, color: str = '', style: str = '') -> None:
        """Internal method to print and optionally log to file."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        colored = f"{color}{style}[{timestamp}] {message}{Style.RESET_ALL}"
        print(colored)
        if self.log_file:
            # Write without colors to file
            plain = f"[{timestamp}] {message}"
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(plain + '\n')

    def info(self, message: str) -> None:
        """General information (cyan)."""
        self._write(f"[INFO] {message}", Fore.CYAN)

    def debug(self, message: str) -> None:
        """Debug information (blue) – only printed if debug_mode is True."""
        if self.debug_mode:
            self._write(f"[DEBUG] {message}", Fore.BLUE)

    def error(self, message: str) -> None:
        """Error message (red)."""
        self._write(f"[ERROR] {message}", Fore.RED, Style.BRIGHT)

    def warning(self, message: str) -> None:
        """Warning message (yellow)."""
        self._write(f"[WARNING] {message}", Fore.YELLOW)

    def user(self, message: str) -> None:
        """User input (green)."""
        self._write(f"[USER] {message}", Fore.GREEN)

    def ai(self, message: str) -> None:
        """AI response (magenta)."""
        self._write(f"[AI] {message}", Fore.MAGENTA)

    def agent(self, agent_name: str, output: str) -> None:
        """
        Agent output (blue). 
        Example: agent("Intent", "order_inquiry")
        """
        self._write(f"[AGENT:{agent_name}] {output}", Fore.BLUE)

    def mom(self, message: str) -> None:
        """Minutes of Meeting output (white on cyan background)."""
        self._write(f"[MOM] {message}", Back.CYAN + Fore.BLACK, Style.BRIGHT)

    def system(self, message: str) -> None:
        """System message (white on black)."""
        self._write(f"[SYSTEM] {message}", Fore.WHITE, Style.DIM)

    def separator(self, char: str = '-', length: int = 50) -> None:
        """Print a separator line for visual clarity."""
        sep = char * length
        self._write(sep, Fore.WHITE, Style.DIM)

    def blank_line(self) -> None:
        """Print an empty line."""
        print()


# Global instance for easy import (optional)
logger = Logger(debug=True)

