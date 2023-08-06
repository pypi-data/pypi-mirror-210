#!/usr/bin/env python
"""The entry module for the Squeck application."""
import argparse
import os
import sys
from typing import Optional

from rich.style import Style
from textual.app import App
from textual.widgets import Header
from squonk2.environment import Environment

from squeck.widgets.env import EnvWidget

# Users set SQUONK2_LOGFILE to enable logging
# e.g. "export SQUONK2_LOGFILE=./squad.log"
_LOG: Optional[str] = os.environ.get("SQUONK2_LOGFILE")

# Read the version file
with open(
    os.path.join(os.path.dirname(__file__), "VERSION"), "r", encoding="utf8"
) as f:
    __version__ = f.read().strip()


class Squeck(App):  # type: ignore
    """An example of a very simple Textual App"""

    async def on_load(self) -> None:
        """initialisation - prior to application starting - bind keys."""
        await self.bind("Q", "quit", "Quit")

    async def on_mount(self) -> None:
        """Widget initialisation - application start"""

        # An informative header
        await self.view.dock(
            Header(
                style=Style(color="bright_white", bgcolor="red3", bold=True),
                clock=False,
            ),
            edge="top",
        )

        envs = (EnvWidget(name) for name in Environment.load())
        await self.view.dock(*envs, edge="top")


def main() -> int:
    """Application entry point, called when the module is executed."""

    parser = argparse.ArgumentParser(prog="squeck", description="Squonk2 Deck (Squeck)")
    parser.add_argument(
        "--enable-stderr",
        help="Used for debug. Normally stderr is hidden from"
        " the console to avoid disturbing the textual"
        " framework. But when there are problems we"
        " need to see the stderr stream. Set this"
        " to allow stderr to appear ion the console.",
        action="store_true",
    )
    args = parser.parse_args()

    # Load environments file - simply to test its validity
    _ = Environment.load()

    # Redirect stderr to avoid any potential SSL errors
    # e.g. the 'ssl.SSLCertVerificationError'
    # which will get written to the output stream
    # from interfering with the TUI.
    #
    # We can't write to stdout/stderr and use Textual.
    if not args.enable_stderr:
        sys.stderr = open(os.devnull, "w", encoding="utf-8")

    # Run our app class
    Squeck.run(title=f"squeck v{__version__}", log=_LOG)

    # If we get here, return 0 to indicate success
    # after restoring stderr.
    if not args.enable_stderr:
        sys.stderr.close()
    return 0


# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------
if __name__ == "__main__":

    _RET_VAL: int = main()
    if _RET_VAL != 0:
        sys.exit(_RET_VAL)
