"""
Web Terminal Subproject for School Student Fee Management System.
In-browser interactive terminal console with ANSI colors and CBSE accounts CLI.
"""

from web_terminal.shell import TerminalShell
from web_terminal.server import run_terminal_server

__all__ = ["TerminalShell", "run_terminal_server"]
