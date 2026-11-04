"""
Real Bash & Python Execution Engine for the In-Browser Student Web Terminal.
Supports persistent bash navigation, interactive Python REPL (>>>), and the
interactive DPA School Fee Management Menu (python main.py).
"""

from __future__ import annotations

import contextlib
import io
import os
import shlex
import shutil
import subprocess
import sys
import traceback
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


MENU_TEXT = f"""
{Ansi.TEAL}{Ansi.BOLD}================================================================================
🎓 DELHI PUBLIC ACADEMY — INTERACTIVE SCHOOL FEE CONSOLE
================================================================================{Ansi.RESET}
  {Ansi.BOLD}[1]{Ansi.RESET}  List All Enrolled Students (43 Pupils)
  {Ansi.BOLD}[2]{Ansi.RESET}  View Fee Invoices & Balances
  {Ansi.BOLD}[3]{Ansi.RESET}  Record a Fee Payment (UPI / Cash / NetBanking / Cheque)
  {Ansi.BOLD}[4]{Ansi.RESET}  View Overdue Defaulters Register
  {Ansi.BOLD}[5]{Ansi.RESET}  Financial Collection & Revenue Summary
  {Ansi.BOLD}[6]{Ansi.RESET}  View & Verify Digital Receipt (HMAC-SHA256)
  {Ansi.BOLD}[7]{Ansi.RESET}  Enroll New Student Admission
  {Ansi.BOLD}[8]{Ansi.RESET}  Run Automated Unit Tests (20 Tests)
  {Ansi.BOLD}[9]{Ansi.RESET}  Reset Database to Fresh CBSE Demo State
  {Ansi.BOLD}[0]{Ansi.RESET}  Exit Console (Return to Bash Shell)
{Ansi.TEAL}{Ansi.BOLD}================================================================================{Ansi.RESET}
"""


class RealTerminalEngine:
    """Stateful execution engine supporting Bash, Python REPL, and Interactive CLI Menu."""

    BANNER = f"""{Ansi.TEAL}{Ansi.BOLD}================================================================================
🎓 DELHI PUBLIC ACADEMY — STUDENT DEVELOPER TERMINAL SANDBOX
================================================================================{Ansi.RESET}
{Ansi.WHITE}Welcome! You have a full interactive terminal environment in your browser.{Ansi.RESET}
{Ansi.GRAY}No software setup or local Python installation required. You can tinker with this CLI project directly.{Ansi.RESET}

{Ansi.CYAN}{Ansi.BOLD}📂 Workspace:{Ansi.RESET} ~/school-fee-system (Python 3.12+ / 3.14)
{Ansi.YELLOW}{Ansi.BOLD}💡 Beginner Quick Start Commands:{Ansi.RESET}
  • {Ansi.BOLD}python main.py{Ansi.RESET}                              Launch Interactive Student Fee Console
  • {Ansi.BOLD}python{Ansi.RESET}                                      Start Interactive Python REPL (>>>)
  • {Ansi.BOLD}ls -la{Ansi.RESET}                                      Inspect project files and directories
  • {Ansi.BOLD}cat README.md{Ansi.RESET}                               Read project documentation
  • {Ansi.BOLD}python -m school_fee_system students list{Ansi.RESET}   List all enrolled pupils
  • {Ansi.BOLD}python -m school_fee_system defaulters{Ansi.RESET}      Check overdue fee accounts
  • {Ansi.BOLD}python -m unittest discover tests{Ansi.RESET}          Run all 20 automated unit tests
{Ansi.TEAL}{Ansi.BOLD}================================================================================{Ansi.RESET}
"""

    def __init__(self, project_root: Optional[str] = None):
        if project_root:
            self.project_root = os.path.abspath(project_root)
        else:
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

        # State machine: "bash", "python", "menu", "menu_pay_step1", "menu_pay_step2", "menu_pay_step3", "menu_receipt_step1"
        self.mode = "bash"
        self.pay_temp: Dict[str, Any] = {}

        # Python REPL environment
        self.repl_globals: Dict[str, Any] = {
            "__name__": "__main__",
            "__doc__": "Interactive Python REPL in Student Sandbox",
        }
        # Preload project into REPL namespace
        src_path = os.path.join(self.project_root, "src")
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        if self.project_root not in sys.path:
            sys.path.insert(0, self.project_root)

    def get_service(self):
        from school_fee_system.database import connect_db, initialize_schema
        from school_fee_system.services import SchoolFeeService

        default_db = os.path.join(self.project_root, "dummy_data", "delhi_public_academy_demo.db")
        active_db = os.path.join(self.project_root, "data", "fees.db")
        if not os.path.exists(active_db) and os.path.exists(default_db):
            os.makedirs(os.path.dirname(active_db), exist_ok=True)
            shutil.copyfile(default_db, active_db)

        db_path = active_db if os.path.exists(active_db) else default_db
        conn = connect_db(db_path)
        initialize_schema(conn)
        conn.close()
        return SchoolFeeService(db_path)

    def get_display_path(self) -> str:
        try:
            rel = os.path.relpath(self.current_cwd, self.project_root)
            if rel == ".":
                return "~/school-fee-system"
            return f"~/school-fee-system/{rel}"
        except Exception:
            return self.current_cwd

    def get_prompt_info(self) -> Dict[str, str]:
        if self.mode == "python":
            return {
                "user": "python",
                "host": "repl",
                "path": ">>>",
                "symbol": " ",
            }
        elif self.mode.startswith("menu"):
            if self.mode == "menu_pay_step1":
                return {"user": "dpa", "host": "payment", "path": "Invoice ID", "symbol": ">"}
            elif self.mode == "menu_pay_step2":
                return {"user": "dpa", "host": "payment", "path": "Amount (₹)", "symbol": ">"}
            elif self.mode == "menu_pay_step3":
                return {"user": "dpa", "host": "payment", "path": "Mode [UPI/CASH/NETBANKING/CHEQUE]", "symbol": ">"}
            elif self.mode == "menu_receipt_step1":
                return {"user": "dpa", "host": "receipt", "path": "Receipt No", "symbol": ">"}
            return {
                "user": "dpa",
                "host": "menu",
                "path": "[1-9, 0 exit]",
                "symbol": ">",
            }

        return {
            "user": "student",
            "host": "dpa-box",
            "path": self.get_display_path(),
            "symbol": "$",
        }

    def execute(self, cmd_line: str) -> Dict[str, Any]:
        """Dispatches command execution based on current mode."""
        raw = cmd_line.strip()

        # Handle Python REPL Mode
        if self.mode == "python":
            return self._handle_python_repl(raw)

        # Handle Interactive Menu Mode
        if self.mode.startswith("menu"):
            return self._handle_menu_interaction(raw)

        # Handle Bash Shell Mode
        return self._handle_bash(raw)

    def _handle_bash(self, raw: str) -> Dict[str, Any]:
        if not raw:
            return {"output": "", "exit_code": 0, "prompt": self.get_prompt_info()}

        # 1. Built-in: Clear
        if raw in ("clear", "cls"):
            return {"output": "\033[2J\033[H", "exit_code": 0, "prompt": self.get_prompt_info()}

        # 2. Built-in: Banner
        if raw in ("banner", "welcome"):
            return {"output": self.BANNER, "exit_code": 0, "prompt": self.get_prompt_info()}

        # 3. Built-in: Help / Cheatsheet
        if raw in ("help", "cheatsheet", "guide"):
            return {"output": self._get_help_text(), "exit_code": 0, "prompt": self.get_prompt_info()}

        # 4. Built-in: Reset database
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

        # 5. Interactive Python REPL transition
        if raw in ("python", "python3", "py"):
            self.mode = "python"
            welcome = (
                f"{Ansi.CYAN}{Ansi.BOLD}Python 3.12 (Delhi Public Academy Interactive Sandbox){Ansi.RESET}\n"
                f'Type "help", "copyright", "credits" or "license" for more information.\n'
                f'{Ansi.YELLOW}Type "exit()" or "quit()" to return to bash shell.{Ansi.RESET}\n'
            )
            return {"output": welcome, "exit_code": 0, "prompt": self.get_prompt_info()}

        # 6. Interactive CLI Menu transition
        # Triggered by: python main.py, python run.py, python app.py, python -m school_fee_system, ./main.py
        norm = raw.lower().replace("./", "")
        if norm in (
            "python main.py", "python run.py", "python app.py",
            "python3 main.py", "python3 run.py", "python3 app.py",
            "python -m school_fee_system", "python3 -m school_fee_system",
            "main.py", "run.py", "app.py", "menu"
        ):
            self.mode = "menu"
            return {"output": MENU_TEXT, "exit_code": 0, "prompt": self.get_prompt_info()}

        # 7. cd navigation
        if raw.startswith("cd ") or raw == "cd":
            parts = raw.split(None, 1)
            target = parts[1].strip() if len(parts) > 1 else "~"

            if target in ("~", "~/school-fee-system"):
                dest_dir = self.project_root
            elif target.startswith("~/school-fee-system/"):
                sub = target[len("~/school-fee-system/"):]
                dest_dir = os.path.abspath(os.path.join(self.project_root, sub))
            elif target.startswith("/"):
                dest_dir = self.project_root
            else:
                dest_dir = os.path.abspath(os.path.join(self.current_cwd, target))

            if os.path.isdir(dest_dir):
                self.current_cwd = dest_dir
                return {"output": "", "exit_code": 0, "prompt": self.get_prompt_info()}
            else:
                return {
                    "output": f"bash: cd: {target}: No such file or directory\n",
                    "exit_code": 1,
                    "prompt": self.get_prompt_info(),
                }

        # 8. Security filter
        lowered = raw.lower()
        if "rm -rf /" in lowered or ":(){ :|:& };:" in lowered or lowered.startswith("sudo"):
            return {
                "output": f"{Ansi.RED}Permission denied: Restricted command in student sandbox.{Ansi.RESET}\n",
                "exit_code": 126,
                "prompt": self.get_prompt_info(),
            }

        # 9. Real Subprocess Execution (with stdin=DEVNULL to ensure non-blocking)
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
                stdin=subprocess.DEVNULL,  # Crucial: never hang waiting for stdin
                capture_output=True,
                text=True,
                timeout=15,
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
                "output": f"{Ansi.RED}\n[Command execution timed out after 15 seconds. Infinite loop halted.]{Ansi.RESET}\n",
                "exit_code": 124,
                "prompt": self.get_prompt_info(),
            }
        except Exception as err:
            return {
                "output": f"{Ansi.RED}Execution Error: {err}{Ansi.RESET}\n",
                "exit_code": 1,
                "prompt": self.get_prompt_info(),
            }

    def _handle_python_repl(self, raw: str) -> Dict[str, Any]:
        """Persistent Python REPL evaluation."""
        if not raw:
            return {"output": "", "exit_code": 0, "prompt": self.get_prompt_info()}

        if raw in ("exit()", "quit()", "exit", "quit"):
            self.mode = "bash"
            return {
                "output": f"{Ansi.GRAY}Exited Python REPL. Back to bash shell.{Ansi.RESET}\n",
                "exit_code": 0,
                "prompt": self.get_prompt_info(),
            }

        if raw in ("clear", "clear()", "cls"):
            return {"output": "\033[2J\033[H", "exit_code": 0, "prompt": self.get_prompt_info()}

        # Evaluate code
        stdout_buf = io.StringIO()
        stderr_buf = io.StringIO()

        with contextlib.redirect_stdout(stdout_buf), contextlib.redirect_stderr(stderr_buf):
            try:
                # Try eval first for expressions like: 2 + 2 or x
                code_obj = compile(raw, "<web-repl>", "eval")
                res = eval(code_obj, self.repl_globals)
                if res is not None:
                    print(repr(res))
            except SyntaxError:
                # Fallback to exec for statements like: import x, x = 10, def foo()...
                try:
                    code_obj = compile(raw, "<web-repl>", "exec")
                    exec(code_obj, self.repl_globals)
                except Exception:
                    traceback.print_exc(file=stderr_buf)
            except Exception:
                traceback.print_exc(file=stderr_buf)

        output = stdout_buf.getvalue() + stderr_buf.getvalue()
        return {
            "output": output,
            "exit_code": 0,
            "prompt": self.get_prompt_info(),
        }

    def _handle_menu_interaction(self, raw: str) -> Dict[str, Any]:
        """Interactive state machine for Delhi Public Academy Fee System Console."""
        from school_fee_system.cli import print_table
        from school_fee_system.models import PaymentMethod
        from decimal import Decimal

        # Sub-mode: Payment Flow
        if self.mode == "menu_pay_step1":
            if raw in ("cancel", "q", "0", "exit"):
                self.mode = "menu"
                self.pay_temp.clear()
                return {"output": "Payment cancelled.\n" + MENU_TEXT, "exit_code": 0, "prompt": self.get_prompt_info()}
            if not raw.isdigit():
                return {"output": f"{Ansi.RED}Invalid Invoice ID. Please enter numeric ID (e.g. 1):{Ansi.RESET} ", "exit_code": 1, "prompt": self.get_prompt_info()}
            self.pay_temp["invoice_id"] = int(raw)
            self.mode = "menu_pay_step2"
            return {"output": f"Invoice ID #{raw} selected.\nEnter Payment Amount (₹): ", "exit_code": 0, "prompt": self.get_prompt_info()}

        if self.mode == "menu_pay_step2":
            if raw in ("cancel", "q", "0", "exit"):
                self.mode = "menu"
                self.pay_temp.clear()
                return {"output": "Payment cancelled.\n" + MENU_TEXT, "exit_code": 0, "prompt": self.get_prompt_info()}
            try:
                amt = Decimal(raw)
                if amt <= 0:
                    raise ValueError("Amount must be positive.")
                self.pay_temp["amount"] = amt
                self.mode = "menu_pay_step3"
                return {"output": f"Amount ₹{amt:.2f} set.\nPayment Mode [UPI / CASH / NETBANKING / CHEQUE] (default UPI): ", "exit_code": 0, "prompt": self.get_prompt_info()}
            except Exception:
                return {"output": f"{Ansi.RED}Invalid amount. Enter a valid number (e.g. 5000):{Ansi.RESET} ", "exit_code": 1, "prompt": self.get_prompt_info()}

        if self.mode == "menu_pay_step3":
            method = (raw.upper() if raw else "UPI").strip()
            if method not in ("UPI", "CASH", "NETBANKING", "CHEQUE"):
                method = "UPI"
            inv_id = self.pay_temp.get("invoice_id", 1)
            amt = self.pay_temp.get("amount", Decimal("1000"))
            self.mode = "menu"
            self.pay_temp.clear()
            try:
                service = self.get_service()
                payment, receipt = service.record_payment(
                    invoice_id=inv_id,
                    amount=amt,
                    payment_method=PaymentMethod(method),
                    transaction_id=f"WEB-{method}-PAY",
                )
                res_text = (
                    f"\n{Ansi.GREEN}{Ansi.BOLD}✓ PAYMENT RECORDED SUCCESSFULLY!{Ansi.RESET}\n"
                    f"Receipt Number : {Ansi.WHITE}{Ansi.BOLD}{receipt.receipt_number}{Ansi.RESET}\n"
                    f"Amount Credited: {Ansi.GREEN}₹{payment.amount:.2f}{Ansi.RESET}\n"
                    f"Payment Mode   : {payment.payment_method.value}\n"
                    f"HMAC Signature : {Ansi.CYAN}{receipt.receipt_hash}{Ansi.RESET}\n\n"
                    f"{Ansi.YELLOW}Type 6 to verify this receipt authenticity, or choose another option:{Ansi.RESET}\n"
                )
                return {"output": res_text, "exit_code": 0, "prompt": self.get_prompt_info()}
            except Exception as e:
                return {"output": f"{Ansi.RED}Payment Failed: {e}{Ansi.RESET}\n\n" + MENU_TEXT, "exit_code": 1, "prompt": self.get_prompt_info()}

        # Sub-mode: Receipt Verification Flow
        if self.mode == "menu_receipt_step1":
            self.mode = "menu"
            if not raw or raw in ("cancel", "q", "exit"):
                return {"output": "Cancelled.\n" + MENU_TEXT, "exit_code": 0, "prompt": self.get_prompt_info()}
            service = self.get_service()
            is_valid, receipt = service.verify_receipt_authenticity(raw)
            if not receipt:
                return {"output": f"{Ansi.RED}Receipt {raw} not found in database.{Ansi.RESET}\n\n" + MENU_TEXT, "exit_code": 1, "prompt": self.get_prompt_info()}
            if is_valid:
                amt_str = f"₹{receipt.payment.amount:,.2f}" if receipt.payment else "₹0.00"
                mode_str = receipt.payment.payment_method.value if receipt.payment else "N/A"
                out = (
                    f"\n{Ansi.GREEN}{Ansi.BOLD}✓ VALID CRYPTOGRAPHIC RECEIPT{Ansi.RESET}\n"
                    f"Receipt Number : {receipt.receipt_number}\n"
                    f"Amount Paid    : {amt_str}\n"
                    f"Payment Mode   : {mode_str}\n"
                    f"HMAC Signature : {receipt.receipt_hash}\n\n"
                )
                return {"output": out, "exit_code": 0, "prompt": self.get_prompt_info()}
            else:
                return {"output": f"\n{Ansi.RED}{Ansi.BOLD}✗ TAMPER WARNING: Signature mismatch!{Ansi.RESET}\n\n", "exit_code": 1, "prompt": self.get_prompt_info()}

        # Main Menu Options
        if not raw:
            return {"output": "", "exit_code": 0, "prompt": self.get_prompt_info()}

        if raw in ("0", "exit", "quit", "q"):
            self.mode = "bash"
            return {
                "output": f"{Ansi.GRAY}Exited School Fee Management Console. Back to bash shell.{Ansi.RESET}\n",
                "exit_code": 0,
                "prompt": self.get_prompt_info(),
            }

        service = self.get_service()

        if raw in ("1", "students"):
            students = service.list_students()
            rows = [
                [
                    s.student_id,
                    s.full_name,
                    s.class_name or str(s.class_id),
                    s.parent_name,
                    s.parent_phone,
                    "Yes" if s.is_transport_enrolled else "No",
                    "Yes" if s.is_hostel_enrolled else "No",
                    s.status.value,
                ]
                for s in students
            ]
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                print(f"\n{Ansi.BOLD}ENROLLED SCHOLARS (DELHI PUBLIC ACADEMY):{Ansi.RESET}")
                print_table(["ID", "Name", "Class", "Parent", "Phone", "Transport", "Hostel", "Status"], rows)
            return {"output": buf.getvalue(), "exit_code": 0, "prompt": self.get_prompt_info()}

        if raw in ("2", "invoices"):
            invoices = service.list_invoices()
            rows = [
                [
                    str(inv.id),
                    inv.invoice_number,
                    inv.student_name,
                    inv.class_name or "",
                    f"₹{inv.total_amount:.2f}",
                    f"₹{inv.paid_amount:.2f}",
                    f"₹{inv.balance_due:.2f}",
                    inv.status.value,
                    inv.due_date.isoformat(),
                ]
                for inv in invoices
            ]
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                print(f"\n{Ansi.BOLD}FEE INVOICES & BALANCES:{Ansi.RESET}")
                print_table(["ID", "Invoice #", "Student", "Class", "Total", "Paid", "Balance", "Status", "Due Date"], rows)
            return {"output": buf.getvalue(), "exit_code": 0, "prompt": self.get_prompt_info()}

        if raw in ("3", "pay"):
            self.mode = "menu_pay_step1"
            return {
                "output": f"\n{Ansi.BOLD}RECORD FEE PAYMENT:{Ansi.RESET}\nEnter Invoice ID (e.g. 1): ",
                "exit_code": 0,
                "prompt": self.get_prompt_info(),
            }

        if raw in ("4", "defaulters"):
            defaulters = service.get_defaulters_report()
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                print(f"\n{Ansi.BOLD}OVERDUE FEE DEFAULTERS ({len(defaulters)} accounts):{Ansi.RESET}")
                if not defaulters:
                    print(f"{Ansi.GREEN}✓ All fee accounts up to date!{Ansi.RESET}")
                else:
                    rows = [
                        [
                            d["invoice_number"],
                            d["student_name"],
                            d["class_name"],
                            d["parent_phone"],
                            d["due_date"],
                            f"{d['days_overdue']} days",
                            f"₹{d['balance_due']:.2f}",
                        ]
                        for d in defaulters
                    ]
                    print_table(["Invoice #", "Student", "Class", "Parent Phone", "Due Date", "Overdue By", "Balance Due (₹)"], rows)
            return {"output": buf.getvalue(), "exit_code": 0, "prompt": self.get_prompt_info()}

        if raw in ("5", "reports", "collection"):
            summary = service.get_collection_summary()
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                print(f"\n{Ansi.BOLD}FINANCIAL REVENUE COLLECTION REPORT:{Ansi.RESET}")
                print(f"Total Collected: {Ansi.GREEN}{Ansi.BOLD}₹{summary['total_collected']:,.2f}{Ansi.RESET}")
                print(f"Receipts Issued: {summary['payments_count']}\n")
                rows = [[k, f"₹{v:,.2f}"] for k, v in summary["by_method"].items()]
                print_table(["Payment Mode", "Total Credited (₹)"], rows)
            return {"output": buf.getvalue(), "exit_code": 0, "prompt": self.get_prompt_info()}

        if raw in ("6", "receipt"):
            self.mode = "menu_receipt_step1"
            return {
                "output": f"\n{Ansi.BOLD}RECEIPT AUTHENTICITY VERIFICATION:{Ansi.RESET}\nEnter Receipt Number (e.g. REC-2026-0001): ",
                "exit_code": 0,
                "prompt": self.get_prompt_info(),
            }

        if raw in ("7", "enroll", "add"):
            return {
                "output": (
                    f"\n{Ansi.CYAN}{Ansi.BOLD}Quick Student Admission Command:{Ansi.RESET}\n"
                    f"To enroll a student via CLI with custom details, run:\n"
                    f'  {Ansi.YELLOW}python -m school_fee_system students add --id ADM-2026-050 --first Rohan --last Roy --class-id 1 --parent-name "M. Roy" --phone "+91 98110 99999" --transport{Ansi.RESET}\n'
                ),
                "exit_code": 0,
                "prompt": self.get_prompt_info(),
            }

        if raw in ("8", "tests"):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                print(f"\n{Ansi.BOLD}RUNNING AUTOMATED UNIT TESTS:{Ansi.RESET}")
                import unittest
                loader = unittest.TestLoader()
                suite = loader.discover(os.path.join(self.project_root, "tests"))
                runner = unittest.TextTestRunner(stream=buf, verbosity=2)
                runner.run(suite)
            return {"output": buf.getvalue(), "exit_code": 0, "prompt": self.get_prompt_info()}

        if raw in ("9", "reset"):
            demo_db = os.path.join(self.project_root, "dummy_data", "delhi_public_academy_demo.db")
            active_db = os.path.join(self.project_root, "data", "fees.db")
            if os.path.exists(demo_db):
                os.makedirs(os.path.dirname(active_db), exist_ok=True)
                shutil.copyfile(demo_db, active_db)
                return {
                    "output": f"\n{Ansi.GREEN}{Ansi.BOLD}✓ Database successfully restored to 43-student CBSE demo state!{Ansi.RESET}\n",
                    "exit_code": 0,
                    "prompt": self.get_prompt_info(),
                }

        if raw in ("menu", "help", "?"):
            return {"output": MENU_TEXT, "exit_code": 0, "prompt": self.get_prompt_info()}

        return {
            "output": f"{Ansi.YELLOW}Invalid choice '{raw}'. Enter 1-9 to select, 0 to exit, or 'menu' to show options.{Ansi.RESET}\n",
            "exit_code": 0,
            "prompt": self.get_prompt_info(),
        }

    def _get_help_text(self) -> str:
        return f"""{Ansi.TEAL}{Ansi.BOLD}STUDENT LAB CHEATSHEET & AVAILABLE TERMINAL COMMANDS:{Ansi.RESET}

{Ansi.WHITE}{Ansi.BOLD}1. School Fee System Applications:{Ansi.RESET}
  {Ansi.TEAL}python main.py{Ansi.RESET}                              Launch Interactive Student Fee Console
  {Ansi.TEAL}python{Ansi.RESET}                                      Start Interactive Python REPL (>>>)
  {Ansi.TEAL}python -m school_fee_system --help{Ansi.RESET}          Display full CLI options
  {Ansi.TEAL}python -m school_fee_system students list{Ansi.RESET}   Tabulate all enrolled students
  {Ansi.TEAL}python -m school_fee_system invoices list{Ansi.RESET}   List all fee invoices & due dates
  {Ansi.TEAL}python -m school_fee_system defaulters{Ansi.RESET}      Display overdue fee defaulters
  {Ansi.TEAL}python -m school_fee_system payments record --invoice-id 1 --amount 5000 --method UPI{Ansi.RESET}

{Ansi.WHITE}{Ansi.BOLD}2. Exploring the Project Files:{Ansi.RESET}
  {Ansi.TEAL}ls -la{Ansi.RESET}                                      List all files and subdirectories
  {Ansi.TEAL}pwd{Ansi.RESET}                                         Print current working directory path
  {Ansi.TEAL}cat README.md{Ansi.RESET}                               Print file contents in terminal
  {Ansi.TEAL}cd src{Ansi.RESET}                                      Navigate into source directory
  {Ansi.TEAL}cd ~{Ansi.RESET}                                        Return to project root

{Ansi.WHITE}{Ansi.BOLD}3. Python Tinkering & Testing:{Ansi.RESET}
  {Ansi.TEAL}python -m unittest discover tests{Ansi.RESET}          Run all unit tests
  {Ansi.TEAL}echo "print('Hello, Python!')" > test.py && python test.py{Ansi.RESET}
  {Ansi.TEAL}reset-db{Ansi.RESET}                                     Reset database back to initial demo data
  {Ansi.TEAL}clear{Ansi.RESET}                                        Clear terminal output
"""


# Alias for backward compatibility
TerminalShell = RealTerminalEngine
