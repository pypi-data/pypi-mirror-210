"""Common material (constants etc.).
"""
from rich.style import Style
from rich.text import Text
import textual

# Text icons.
TICK: Text = Text("\u2714", style=Style(color="green3", bold=True))
CROSS: Text = Text("\u02df", style=Style(color="red3", bold=True))


def log_info(msg: str) -> None:
    """Log an INFO message using the textual logger.

    WARNING: This can only be used after the textual app has been started."""
    textual.log(f"SquAd INFO # {msg}")


def log_warning(msg: str) -> None:
    """Log a WARNING message using the textual logger.

    WARNING: This can only be used after the textual app has been started."""
    textual.log(f"SquAd WARNING # {msg}")
