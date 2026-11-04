"""
Real Bash & Python Execution Engine for the In-Browser Student Web Terminal.
Executes real shell commands in the project workspace with virtual environment Python.
"""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
from typing import Dict, List, Optional, Tuple, Any


class Ansi:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    CYAN = "\033[36m"
    TEAL = "\033[38;2;45;212;191m"
    GRAY = "\033[38;2;148;163;184m"
    WHITE = "\033[37m"


class RealTerminalEngine:
    """Executes real shell and Python commands in the project workspace."""

    BANNER = f"""{Ansi.TEAL}{Ansi.BOLD}================================================================================
🎓 DELHI PUBLIC ACADEMY — STUDENT DEVELOPER TERMINAL SANDBOX
================================================================================{Ansi.RESET}
{Ansi.WHITE}Welcome! You have a full interactive terminal environment in your browser.{Ansi.RESET}
{Ansi.GRAY}No software setup or local Python installation required. You can tinker with this CLI project directly.{Ansi.RESET}

{Ansi.CYAN}{Ansi.BOLD}📂 Workspace:{Ansi.RESET} ~/school-fee-system (Python 3.12+ / 3.14)
{Ansi.YELLOW}{Ansi.BOLD}💡 Beginner Quick Start Commands:{Ansi.RESET}
  • {Ansi.BOLD}ls -la{Ansi.RESET}                                      Inspect project files and directories
  • {Ansi.BOLD}cat README.md{Ansi.RESET}                               Read project documentation
  • {Ansi.BOLD}python -m school_fee_system --help{Ansi.RESET}          View all CLI commands
  • {Ansi.BOLD}python -m school_fee_system students list{Ansi.RESET}   List all enrolled pupils
  • {Ansi.BOLD}python -m school_fee_system invoices list{Ansi.RESET}   List student fee invoices
  • {Ansi.BOLD}python -m school_fee_system defaulters{Ansi.RESET}      Check overdue fee accounts
  • {Ansi.BOLD}python -m school_fee_system payments record --invoice-id 1 --amount 5000 --method UPI{Ansi.RESET}
  • {Ansi.BOLD}python -m school_fee_system receipts view REC-2026-0001{Ansi.RESET}
  • {Ansi.BOLD}python -m unittest discover tests{Ansi.RESET}          Run all 20 automated unit tests
{Ansi.TEAL}{Ansi.BOLD}================================================================================{Ansi.RESET}
"""

    def __init__(self, project_root: Optional[str] = None):
        if project_root:
            self.project_root = os.path.abspath(project_root)
        else:
            # Walk up to find the root directory containing pyproject.toml
            current = os.path.dirname(os.path.abspath(__file__))
            while current and current != os.path.dirname(current):
                if os.path.exists(os.path.join(current, "pyproject.toml")):
                    break
                current = os.path.dirname(current)
            self.project_root = current or os.getcwd()

        self.current_cwd = self.project_root

        # Virtualenv python detection
        self.venv_bin = os.path.join(self.project_root, ".venv", "bin")
        if not os.path.isdir(self.venv_bin):
            self.venv_bin = ""

    def get_display_path(self) -> str:
        try:
            rel = os.path.relpath(self.current_cwd, self.project_root)
            if rel == ".":
                return "~/school-fee-system"
            return f"~/school-fee-system/{rel}"
        except Exception:
            return self.current_cwd

    def get_prompt_info(self) -> Dict[str, str]:
        return {
            "user": "student",
            "host": "dpa-box",
            "path": self.get_display_path(),
            "symbol": "$",
        }

    def execute(self, cmd_line: str) -> Dict[str, Any]:
        """Executes a command line string and returns output, returncode, and updated cwd."""
        raw = cmd_line.strip()
        if not raw:
            return {
                "output": "",
                "exit_code": 0,
                "prompt": self.get_prompt_info(),
            }

        # 1. Built-in: Clear screen
        if raw in ("clear", "cls"):
            return {
                "output": "\033[2J\033[H",
                "exit_code": 0,
                "prompt": self.get_prompt_info(),
            }

        # 2. Built-in: Banner
        if raw in ("banner", "welcome"):
            return {
                "output": self.BANNER,
                "exit_code": 0,
                "prompt": self.get_prompt_info(),
            }

        # 3. Built-in: Help / Cheatsheet
        if raw in ("help", "cheatsheet", "guide"):
            return {
                "output": self._get_help_text(),
                "exit_code": 0,
                "prompt": self.get_prompt_info(),
            }

        # 4. Built-in: Reset database to fresh demo state
        if raw in ("reset-db", "restore-data"):
            demo_db = os.path.join(self.project_root, "dummy_data", "delhi_public_academy_demo.db")
            active_db = os.path.join(self.project_root, "data", "fees.db")
            if os.path.exists(demo_db):
                os.makedirs(os.path.dirname(active_db), exist_ok=True)
                shutil.copyfile(demo_db, active_db)
                return {
                    "output": f"{Ansi.GREEN}{Ansi.BOLD}✓ Database successfully restored to 43-student CBSE demo state!{Ansi.RESET}\n",
                    "exit_code": 0,
                    "prompt": self.get_prompt_info(),
                }
            return {
                "output": f"{Ansi.RED}Could not locate demo database at {demo_db}{Ansi.RESET}\n",
                "exit_code": 1,
                "prompt": self.get_prompt_info(),
            }

        # 5. Handle directory navigation (cd)
        if raw.startswith("cd ") or raw == "cd":
            parts = raw.split(None, 1)
            target = parts[1].strip() if len(parts) > 1 else "~"
            
            if target == "~" or target == "~/school-fee-system":
                dest_dir = self.project_root
            elif target.startswith("~/school-fee-system/"):
                sub = target[len("~/school-fee-system/"):]
                dest_dir = os.path.abspath(os.path.join(self.project_root, sub))
            elif target.startswith("/"):
                # Constrain inside workspace for security
                dest_dir = self.project_root
            else:
                dest_dir = os.path.abspath(os.path.join(self.current_cwd, target))

            if os.path.isdir(dest_dir):
                self.current_cwd = dest_dir
                return {
                    "output": "",
                    "exit_code": 0,
                    "prompt": self.get_prompt_info(),
                }
            else:
                return {
                    "output": f"bash: cd: {target}: No such file or directory\n",
                    "exit_code": 1,
                    "prompt": self.get_prompt_info(),
                }

        # 6. Safety check for prohibited system destruction commands
        lowered = raw.lower()
        if "rm -rf /" in lowered or ":(){ :|:& };:" in lowered or lowered.startswith("sudo"):
            return {
                "output": f"{Ansi.RED}Permission denied: Restricted command in student sandbox.{Ansi.RESET}\n",
                "exit_code": 126,
                "prompt": self.get_prompt_info(),
            }

        # 7. Check if student typed plain 'python' without arguments
        if raw in ("python", "python3", "py"):
            return {
                "output": (
                    f"{Ansi.YELLOW}Interactive Python Mode Tip:{Ansi.RESET}\n"
                    f"To test Python code in this terminal, you can run:\n"
                    f"  1. One-line code: {Ansi.BOLD}python -c \"import school_fee_system; print('Ready!')\"{Ansi.RESET}\n"
                    f"  2. CLI project  : {Ansi.BOLD}python -m school_fee_system --help{Ansi.RESET}\n"
                    f"  3. Create script: {Ansi.BOLD}echo \"print(2 + 2)\" > calc.py && python calc.py{Ansi.RESET}\n"
                    f"  4. Run tests    : {Ansi.BOLD}python -m unittest discover tests{Ansi.RESET}\n"
                ),
                "exit_code": 0,
                "prompt": self.get_prompt_info(),
            }

        # 8. Execute in real subshell with virtualenv environment
        env = os.environ.copy()
        src_path = os.path.join(self.project_root, "src")
        env["PYTHONPATH"] = f"{src_path}:{self.project_root}:{env.get('PYTHONPATH', '')}"
        if self.venv_bin and os.path.isdir(self.venv_bin):
            env["PATH"] = f"{self.venv_bin}:{env.get('PATH', '')}"
        env["PYTHONUNBUFFERED"] = "1"
        env["TERM"] = "xterm-256color"

        try:
            proc = subprocess.run(
                raw,
                shell=True,
                cwd=self.current_cwd,
                env=env,
                capture_output=True,
                text=True,
                timeout=20,  # 20s timeout protects from infinite loops in student code
            )
            stdout = proc.stdout or ""
            stderr = proc.stderr or ""
            combined = stdout + stderr

            return {
                "output": combined,
                "exit_code": proc.returncode,
                "prompt": self.get_prompt_info(),
            }
        except subprocess.TimeoutExpired:
            return {
                "output": f"{Ansi.RED}\n[Command execution timed out after 20 seconds. Infinite loop stopped.]{Ansi.RESET}\n",
                "exit_code": 124,
                "prompt": self.get_prompt_info(),
            }
        except Exception as err:
            return {
                "output": f"{Ansi.RED}Execution Error: {err}{Ansi.RESET}\n",
                "exit_code": 1,
                "prompt": self.get_prompt_info(),
            }

    def _get_help_text(self) -> str:
        return f"""{Ansi.TEAL}{Ansi.BOLD}STUDENT LAB CHEATSHEET & AVAILABLE TERMINAL COMMANDS:{Ansi.RESET}

{Ansi.WHITE}{Ansi.BOLD}1. Exploring the Project Files:{Ansi.RESET}
  {Ansi.TEAL}ls -la{Ansi.RESET}                                      List all files and subdirectories
  {Ansi.TEAL}pwd{Ansi.RESET}                                         Print current working directory path
  {Ansi.TEAL}cat README.md{Ansi.RESET}                               Print file contents in terminal
  {Ansi.TEAL}cd src/school_fee_system{Ansi.RESET}                   Navigate into package directory
  {Ansi.TEAL}cd ~{Ansi.RESET}                                          Return to project root

{Ansi.WHITE}{Ansi.BOLD}2. Running the Python School Fee System:{Ansi.RESET}
  {Ansi.TEAL}python -m school_fee_system --help{Ansi.RESET}          Display full CLI options and commands
  {Ansi.TEAL}python -m school_fee_system students list{Ansi.RESET}   Tabulate all enrolled students
  {Ansi.TEAL}python -m school_fee_system invoices list{Ansi.RESET}   List all fee invoices & due dates
  {Ansi.TEAL}python -m school_fee_system defaulters{Ansi.RESET}      Display overdue fee defaulters
  {Ansi.TEAL}python -m school_fee_system reports collection{Ansi.RESET} Show collection summary by payment method
  {Ansi.TEAL}python -m school_fee_system payments record --invoice-id 1 --amount 5000 --method UPI{Ansi.RESET}
  {Ansi.TEAL}python -m school_fee_system receipts view REC-2026-0001{Ansi.RESET}
  {Ansi.TEAL}python -m school_fee_system receipts verify REC-2026-0001{Ansi.RESET}

{Ansi.WHITE}{Ansi.BOLD}3. Python Tinkering & Testing:{Ansi.RESET}
  {Ansi.TEAL}python -m unittest discover tests{Ansi.RESET}          Run all unit tests
  {Ansi.TEAL}python -c "import school_fee_system; print(school_fee_system.__doc__)"{Ansi.RESET}
  {Ansi.TEAL}echo "print('Hello, Python!')" > test.py && python test.py{Ansi.RESET}
  {Ansi.TEAL}reset-db{Ansi.RESET}                                     Reset database back to initial demo data
  {Ansi.TEAL}clear{Ansi.RESET}                                        Clear terminal output
"""


# Alias for backward compatibility
TerminalShell = RealTerminalEngine
