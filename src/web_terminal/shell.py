"""
Interactive Terminal Shell Engine for Delhi Public Academy Fee Management.
Processes text commands and generates ANSI-colored tabular and formatted terminal output.
"""

from __future__ import annotations

import argparse
import shlex
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Any

from school_fee_system.models import (
    Student,
    StudentStatus,
    FeeTerm,
    InvoiceStatus,
    PaymentMethod,
    Payment,
    Receipt,
)
from school_fee_system.receipt_generator import ReceiptFormatter
from school_fee_system.services import SchoolFeeService


# ANSI Escape Codes for Terminal Styling
class Ansi:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    
    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    TEAL = "\033[38;2;45;212;191m"
    ORANGE = "\033[38;2;251;146;60m"
    GRAY = "\033[38;2;148;163;184m"

    # Background colors
    BG_TEAL = "\033[48;2;15;118;110m"
    BG_DARK = "\033[48;2;15;23;42m"
    BG_RED = "\033[48;2;185;28;28m"
    BG_GREEN = "\033[48;2;21;128;61m"


def format_currency(val: Any) -> str:
    """Formats numeric amount as Indian Rupees."""
    try:
        d = Decimal(str(val))
        return f"₹{d:,.2f}"
    except Exception:
        return str(val)


def colorize_status(status_str: str) -> str:
    s = status_str.upper()
    if s == "PAID":
        return f"{Ansi.GREEN}{Ansi.BOLD}● PAID{Ansi.RESET}"
    elif s == "PARTIALLY_PAID":
        return f"{Ansi.CYAN}{Ansi.BOLD}◐ PARTIAL{Ansi.RESET}"
    elif s == "UNPAID":
        return f"{Ansi.YELLOW}{Ansi.BOLD}○ UNPAID{Ansi.RESET}"
    elif s == "OVERDUE":
        return f"{Ansi.RED}{Ansi.BOLD}▲ OVERDUE{Ansi.RESET}"
    elif s == "CANCELLED":
        return f"{Ansi.GRAY}{Ansi.DIM}✕ CANCELLED{Ansi.RESET}"
    return status_str


def render_ascii_table(headers: List[str], rows: List[List[str]], col_align: Optional[List[str]] = None) -> str:
    """Renders a high-fidelity Unicode box-drawing table with colors."""
    if not rows:
        return f"{Ansi.GRAY}  (No matching records found){Ansi.RESET}\n"

    num_cols = len(headers)
    widths = [len(h) for h in headers]
    for row in rows:
        for idx in range(num_cols):
            val = str(row[idx]) if idx < len(row) else ""
            # Strip ANSI escape codes to calculate visual width accurately
            clean_len = len(_strip_ansi(val))
            if clean_len > widths[idx]:
                widths[idx] = clean_len

    aligns = col_align or ["left"] * num_cols

    top_border = "┌─" + "─┬─".join("─" * w for w in widths) + "─┐"
    header_sep = "├─" + "─┼─".join("─" * w for w in widths) + "─┤"
    bottom_border = "└─" + "─┴─".join("─" * w for w in widths) + "─┘"

    lines = [f"{Ansi.GRAY}{top_border}{Ansi.RESET}"]

    # Header line
    hdr_cells = []
    for idx, h in enumerate(headers):
        hdr_cells.append(f"{Ansi.TEAL}{Ansi.BOLD}{h.ljust(widths[idx])}{Ansi.RESET}")
    lines.append(f"{Ansi.GRAY}│ {Ansi.RESET}" + f"{Ansi.GRAY} │ {Ansi.RESET}".join(hdr_cells) + f"{Ansi.GRAY} │{Ansi.RESET}")
    lines.append(f"{Ansi.GRAY}{header_sep}{Ansi.RESET}")

    # Rows
    for r in rows:
        row_cells = []
        for idx in range(num_cols):
            val = str(r[idx]) if idx < len(r) else ""
            clean_len = len(_strip_ansi(val))
            pad_needed = max(0, widths[idx] - clean_len)
            
            if aligns[idx] == "right":
                cell_text = (" " * pad_needed) + val
            elif aligns[idx] == "center":
                left_pad = pad_needed // 2
                right_pad = pad_needed - left_pad
                cell_text = (" " * left_pad) + val + (" " * right_pad)
            else:
                cell_text = val + (" " * pad_needed)
            row_cells.append(cell_text)
        lines.append(f"{Ansi.GRAY}│ {Ansi.RESET}" + f"{Ansi.GRAY} │ {Ansi.RESET}".join(row_cells) + f"{Ansi.GRAY} │{Ansi.RESET}")

    lines.append(f"{Ansi.GRAY}{bottom_border}{Ansi.RESET}")
    return "\n".join(lines) + "\n"


def _strip_ansi(text: str) -> str:
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


class TerminalShell:
    """Command processor that powers the in-browser terminal."""

    BANNER = f"""{Ansi.TEAL}{Ansi.BOLD}
  ██████╗ ██████╗  █████╗     ████████╗███████╗██████╗ ███╗   ███╗██╗███╗   ██╗ █████╗ ██╗     
  ██╔══██╗██╔══██╗██╔══██╗    ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║████╗  ██║██╔══██╗██║     
  ██║  ██║██████╔╝███████║       ██║   █████╗  ██████╔╝██╔████╔██║██║██╔██╗ ██║███████║██║     
  ██║  ██║██╔═══╝ ██╔══██║       ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║╚██╗██║██╔══██║██║     
  ██████╔╝██║     ██║  ██║       ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║██║  ██║███████╗
  ╚═════╝ ╚═╝     ╚═╝  ╚═╝       ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝
{Ansi.RESET}{Ansi.WHITE}{Ansi.BOLD}   Delhi Public Academy — CBSE Affiliation #1030492 | Terminal Fee Console v2.0{Ansi.RESET}
{Ansi.GRAY}   Type {Ansi.TEAL}{Ansi.BOLD}help{Ansi.RESET}{Ansi.GRAY} to view available commands. Press {Ansi.TEAL}{Ansi.BOLD}TAB{Ansi.RESET}{Ansi.GRAY} for auto-completion.{Ansi.RESET}
"""

    def __init__(self, service: Optional[SchoolFeeService] = None):
        self.service = service or SchoolFeeService()

    def execute(self, cmd_line: str) -> str:
        """Executes a single command line and returns formatted terminal text."""
        trimmed = cmd_line.strip()
        if not trimmed:
            return ""

        try:
            tokens = shlex.split(trimmed)
        except ValueError as e:
            return f"{Ansi.RED}Parse Error: {e}{Ansi.RESET}\n"

        cmd = tokens[0].lower()
        args = tokens[1:]

        try:
            if cmd in ("help", "?"):
                return self._cmd_help(args)
            elif cmd in ("kpi", "kpis", "dashboard", "summary"):
                return self._cmd_kpis(args)
            elif cmd in ("student", "students"):
                return self._cmd_students(args)
            elif cmd in ("invoice", "invoices", "bill", "bills"):
                return self._cmd_invoices(args)
            elif cmd in ("pay", "payment", "payments"):
                return self._cmd_pay(args)
            elif cmd in ("receipt", "receipts"):
                return self._cmd_receipts(args)
            elif cmd in ("defaulter", "defaulters", "overdue"):
                return self._cmd_defaulters(args)
            elif cmd in ("report", "reports", "collection"):
                return self._cmd_reports(args)
            elif cmd in ("classes", "class"):
                return self._cmd_classes(args)
            elif cmd in ("banner", "logo"):
                return self.BANNER
            elif cmd == "version":
                return f"{Ansi.TEAL}{Ansi.BOLD}Delhi Public Academy Fee Terminal Console{Ansi.RESET} v2.0.0 (Python {Ansi.YELLOW}3.12+{Ansi.RESET}, SQLite WAL, CBSE Edition)\n"
            elif cmd in ("clear", "cls"):
                return "\033[2J\033[H"
            else:
                return (
                    f"{Ansi.RED}Command not recognized: '{cmd}'.{Ansi.RESET}\n"
                    f"Type {Ansi.TEAL}{Ansi.BOLD}help{Ansi.RESET} to inspect all valid terminal commands.\n"
                )
        except Exception as exc:
            return f"{Ansi.RED}{Ansi.BOLD}Execution Error:{Ansi.RESET} {exc}\n"

    # -------------------------------------------------------------------------
    # Command Implementations
    # -------------------------------------------------------------------------
    def _cmd_help(self, args: List[str]) -> str:
        out = [
            f"{Ansi.BOLD}{Ansi.WHITE}AVAILABLE COMMANDS & CHEATSHEET:{Ansi.RESET}\n",
            f"  {Ansi.TEAL}{Ansi.BOLD}kpis{Ansi.RESET}                                Display real-time school financial KPIs",
            f"  {Ansi.TEAL}{Ansi.BOLD}students list{Ansi.RESET} [opts]                   List enrolled pupils ({Ansi.GRAY}--class <id>, --search <name>{Ansi.RESET})",
            f"  {Ansi.TEAL}{Ansi.BOLD}students view{Ansi.RESET} <student_id>             View student profile & complete account ledger",
            f"  {Ansi.TEAL}{Ansi.BOLD}invoices list{Ansi.RESET} [opts]                   List fee invoices ({Ansi.GRAY}--status <PAID/UNPAID/OVERDUE>{Ansi.RESET})",
            f"  {Ansi.TEAL}{Ansi.BOLD}invoices view{Ansi.RESET} <invoice_id>             View detailed invoice with fee head breakdown",
            f"  {Ansi.TEAL}{Ansi.BOLD}invoices generate{Ansi.RESET} <stu_id> [term]       Generate quarterly fee invoice for student",
            f"  {Ansi.TEAL}{Ansi.BOLD}pay{Ansi.RESET} <inv_id> <amount> [method] [tx]   Record fee payment ({Ansi.GRAY}UPI, CASH, NET_BANKING, etc.{Ansi.RESET})",
            f"  {Ansi.TEAL}{Ansi.BOLD}receipts view{Ansi.RESET} <rec_number>             Render official ASCII receipt with SHA-256 seal",
            f"  {Ansi.TEAL}{Ansi.BOLD}receipts verify{Ansi.RESET} <rec_number>           Cryptographically verify digital audit seal",
            f"  {Ansi.TEAL}{Ansi.BOLD}defaulters{Ansi.RESET}                            List all overdue accounts with days & parent phone",
            f"  {Ansi.TEAL}{Ansi.BOLD}reports collection{Ansi.RESET}                    Summary of fee collections by payment method",
            f"  {Ansi.TEAL}{Ansi.BOLD}classes{Ansi.RESET}                               List all classes and grade sections",
            f"  {Ansi.TEAL}{Ansi.BOLD}theme{Ansi.RESET} <teal|matrix|amber|cyber>       Switch terminal color palette",
            f"  {Ansi.TEAL}{Ansi.BOLD}clear{Ansi.RESET}                                Clear terminal screen",
            f"  {Ansi.TEAL}{Ansi.BOLD}banner{Ansi.RESET}                               Display school crest & affiliation metadata",
            "",
            f"{Ansi.GRAY}Tip: You can use abbreviations: {Ansi.WHITE}'kpi'{Ansi.GRAY}, {Ansi.WHITE}'stu list'{Ansi.GRAY}, {Ansi.WHITE}'inv list'{Ansi.GRAY}, {Ansi.WHITE}'def'{Ansi.RESET}\n",
        ]
        return "\n".join(out)

    def _cmd_kpis(self, args: List[str]) -> str:
        kpis = self.service.get_kpis()
        active = kpis["active_students"]
        collected = format_currency(kpis["total_collected"])
        outstanding = format_currency(kpis["total_outstanding"])
        defaulters = str(kpis["defaulters_count"])

        out = [
            f"{Ansi.TEAL}{Ansi.BOLD}┌────────────────────────────────────────────────────────────────────────┐{Ansi.RESET}",
            f"{Ansi.TEAL}{Ansi.BOLD}│         DELHI PUBLIC ACADEMY — REAL-TIME FINANCIAL SUMMARY             │{Ansi.RESET}",
            f"{Ansi.TEAL}{Ansi.BOLD}├──────────────────┬──────────────────┬──────────────────┬───────────────┤{Ansi.RESET}",
            f"│ {Ansi.GRAY}ACTIVE PUPILS{Ansi.RESET}    │ {Ansi.GRAY}TOTAL COLLECTED{Ansi.RESET}  │ {Ansi.GRAY}OUTSTANDING DUES{Ansi.RESET} │ {Ansi.GRAY}DEFAULTERS{Ansi.RESET}      │",
            f"│ {Ansi.WHITE}{Ansi.BOLD}{str(active).center(16)}{Ansi.RESET} │ {Ansi.GREEN}{Ansi.BOLD}{collected.center(16)}{Ansi.RESET} │ {Ansi.YELLOW}{Ansi.BOLD}{outstanding.center(16)}{Ansi.RESET} │ {Ansi.RED}{Ansi.BOLD}{defaulters.center(13)}{Ansi.RESET} │",
            f"{Ansi.TEAL}{Ansi.BOLD}└──────────────────┴──────────────────┴──────────────────┴───────────────┘{Ansi.RESET}",
            "",
        ]
        return "\n".join(out)

    def _cmd_students(self, args: List[str]) -> str:
        sub = args[0].lower() if args else "list"
        sub_args = args[1:]

        if sub == "list":
            class_id = None
            search = None
            idx = 0
            while idx < len(sub_args):
                if sub_args[idx] in ("--class", "-c") and idx + 1 < len(sub_args):
                    class_id = int(sub_args[idx + 1])
                    idx += 2
                elif sub_args[idx] in ("--search", "-s") and idx + 1 < len(sub_args):
                    search = sub_args[idx + 1]
                    idx += 2
                else:
                    search = sub_args[idx]
                    idx += 1

            students = self.service.list_students(class_id=class_id, search=search)
            headers = ["Adm. No.", "Student Name", "Class", "Parent Name", "Parent Contact", "Transport", "Hostel"]
            rows = []
            for s in students:
                rows.append([
                    f"{Ansi.CYAN}{s.student_id}{Ansi.RESET}",
                    f"{Ansi.BOLD}{s.full_name}{Ansi.RESET}",
                    s.class_name or str(s.class_id),
                    s.parent_name,
                    s.parent_phone,
                    f"{Ansi.GREEN}Yes{Ansi.RESET}" if s.is_transport_enrolled else f"{Ansi.GRAY}No{Ansi.RESET}",
                    f"{Ansi.GREEN}Yes{Ansi.RESET}" if s.is_hostel_enrolled else f"{Ansi.GRAY}No{Ansi.RESET}",
                ])
            return f"\n{Ansi.BOLD}ENROLLED STUDENTS ({len(students)} records):{Ansi.RESET}\n" + render_ascii_table(headers, rows)

        elif sub in ("view", "statement", "profile"):
            if not sub_args:
                return f"{Ansi.RED}Usage: students view <student_id>{Ansi.RESET}\n"
            stu_id = sub_args[0]
            stmt = self.service.get_student_statement(stu_id)
            stu: Student = stmt["student"]
            invoices = stmt["invoices"]
            total_b = format_currency(stmt.get("total_invoiced", Decimal("0.00")))
            total_p = format_currency(stmt.get("total_paid", Decimal("0.00")))
            total_o = format_currency(stmt.get("balance", Decimal("0.00")))

            out = [
                f"\n{Ansi.TEAL}{Ansi.BOLD}STUDENT ACCOUNT STATEMENT: {stu.full_name} ({stu.student_id}){Ansi.RESET}",
                f"{Ansi.GRAY}Class: {Ansi.WHITE}{stu.class_name}{Ansi.GRAY} | Parent: {Ansi.WHITE}{stu.parent_name} ({stu.parent_phone}){Ansi.GRAY} | Email: {stu.parent_email}{Ansi.RESET}",
                f"{Ansi.GRAY}Transport: {Ansi.WHITE}{'Enrolled' if stu.is_transport_enrolled else 'No'}{Ansi.GRAY} | Hostel: {Ansi.WHITE}{'Enrolled' if stu.is_hostel_enrolled else 'No'}{Ansi.RESET}\n",
                f"Financial Summary: Billed: {Ansi.BOLD}{total_b}{Ansi.RESET} | Paid: {Ansi.GREEN}{Ansi.BOLD}{total_p}{Ansi.RESET} | Outstanding: {Ansi.RED}{Ansi.BOLD}{total_o}{Ansi.RESET}\n",
                f"{Ansi.BOLD}INVOICE HISTORY:{Ansi.RESET}",
            ]

            headers = ["Invoice #", "Term", "Due Date", "Billed (₹)", "Paid (₹)", "Balance (₹)", "Status"]
            rows = []
            for inv in invoices:
                rows.append([
                    f"{Ansi.CYAN}{inv.invoice_number}{Ansi.RESET}",
                    inv.term.value,
                    str(inv.due_date),
                    format_currency(inv.total_payable),
                    format_currency(inv.paid_amount),
                    format_currency(inv.balance_amount),
                    colorize_status(inv.status.value),
                ])
            out.append(render_ascii_table(headers, rows, col_align=["left", "left", "left", "right", "right", "right", "center"]))
            return "\n".join(out)

        return f"{Ansi.RED}Unknown students subcommand: '{sub}'. Try: list, view{Ansi.RESET}\n"

    def _cmd_invoices(self, args: List[str]) -> str:
        sub = args[0].lower() if args else "list"
        sub_args = args[1:]

        if sub == "list":
            status_enum = None
            stu_id = None
            idx = 0
            while idx < len(sub_args):
                if sub_args[idx] in ("--status", "-s") and idx + 1 < len(sub_args):
                    st_val = sub_args[idx + 1].upper()
                    try:
                        status_enum = InvoiceStatus(st_val)
                    except ValueError:
                        pass
                    idx += 2
                elif sub_args[idx] in ("--student", "-u") and idx + 1 < len(sub_args):
                    stu_id = sub_args[idx + 1]
                    idx += 2
                else:
                    idx += 1

            invoices = self.service.list_invoices(student_id=stu_id, status=status_enum)
            headers = ["Invoice #", "Student", "Class", "Term", "Due Date", "Payable (₹)", "Paid (₹)", "Balance (₹)", "Status"]
            rows = []
            for inv in invoices:
                rows.append([
                    f"{Ansi.CYAN}{inv.invoice_number}{Ansi.RESET}",
                    inv.student_name or inv.student_id,
                    inv.class_name or "-",
                    inv.term.value,
                    str(inv.due_date),
                    format_currency(inv.total_payable),
                    format_currency(inv.paid_amount),
                    format_currency(inv.balance_amount),
                    colorize_status(inv.status.value),
                ])
            return f"\n{Ansi.BOLD}FEE INVOICES ({len(invoices)} records):{Ansi.RESET}\n" + render_ascii_table(
                headers, rows, col_align=["left", "left", "left", "left", "left", "right", "right", "right", "center"]
            )

        elif sub == "view":
            if not sub_args:
                return f"{Ansi.RED}Usage: invoices view <invoice_id_or_number>{Ansi.RESET}\n"
            inv_ref = sub_args[0]
            inv = self.service.get_invoice(inv_ref)
            if not inv:
                return f"{Ansi.RED}Invoice '{inv_ref}' not found.{Ansi.RESET}\n"

            out = [
                f"\n{Ansi.TEAL}{Ansi.BOLD}INVOICE DETAILS: {inv.invoice_number}{Ansi.RESET}",
                f"{Ansi.GRAY}Student: {Ansi.WHITE}{inv.student_name} ({inv.student_id}){Ansi.GRAY} | Class: {Ansi.WHITE}{inv.class_name}{Ansi.RESET}",
                f"{Ansi.GRAY}Term: {Ansi.WHITE}{inv.term.value}{Ansi.GRAY} | Academic Year: {Ansi.WHITE}{inv.academic_year}{Ansi.RESET}",
                f"{Ansi.GRAY}Issue Date: {inv.issue_date} | Due Date: {Ansi.YELLOW if inv.status == InvoiceStatus.OVERDUE else Ansi.WHITE}{inv.due_date}{Ansi.RESET}",
                f"Status: {colorize_status(inv.status.value)}\n",
                f"{Ansi.BOLD}BILLING ITEMIZATION:{Ansi.RESET}",
            ]

            headers = ["Fee Head", "Gross Amount", "Concession", "Net Amount"]
            rows = []
            for it in inv.items:
                rows.append([
                    it.head_name,
                    format_currency(it.amount),
                    format_currency(it.discount_amount),
                    format_currency(it.net_amount),
                ])
            out.append(render_ascii_table(headers, rows, col_align=["left", "right", "right", "right"]))
            out.append(
                f"Subtotal: {format_currency(inv.subtotal)} | Discounts: -{format_currency(inv.discount_total)} | Late Fee: +{format_currency(inv.late_fee)}"
            )
            out.append(
                f"{Ansi.BOLD}Total Payable: {Ansi.TEAL}{format_currency(inv.total_payable)}{Ansi.RESET} | "
                f"Paid: {Ansi.GREEN}{format_currency(inv.paid_amount)}{Ansi.RESET} | "
                f"Outstanding Balance: {Ansi.RED if inv.balance_amount > 0 else Ansi.GREEN}{Ansi.BOLD}{format_currency(inv.balance_amount)}{Ansi.RESET}\n"
            )
            return "\n".join(out)

        elif sub == "generate":
            if not sub_args:
                return f"{Ansi.RED}Usage: invoices generate <student_id> [term] [academic_year]{Ansi.RESET}\n"
            stu_id = sub_args[0]
            term_str = sub_args[1].upper() if len(sub_args) > 1 else "TERM_1"
            year = sub_args[2] if len(sub_args) > 2 else "2026-2027"
            try:
                term = FeeTerm(term_str)
            except ValueError:
                return f"{Ansi.RED}Invalid term: {term_str}. Choose from: TERM_1, TERM_2, QUARTER_1..4, ANNUAL{Ansi.RESET}\n"

            inv = self.service.generate_student_invoice(student_id=stu_id, academic_year=year, term=term)
            return (
                f"{Ansi.GREEN}✓ Successfully generated invoice {Ansi.BOLD}{inv.invoice_number}{Ansi.RESET} "
                f"for student {stu_id}.\n"
                f"  Total Payable: {format_currency(inv.total_payable)} | Due Date: {inv.due_date}\n"
            )

        return f"{Ansi.RED}Unknown invoices subcommand: '{sub}'. Try: list, view, generate{Ansi.RESET}\n"

    def _cmd_pay(self, args: List[str]) -> str:
        if len(args) < 2:
            return f"{Ansi.RED}Usage: pay <invoice_id> <amount> [method: UPI/CASH/etc] [transaction_id] [cashier]{Ansi.RESET}\n"

        inv_id = int(args[0])
        amount = Decimal(args[1])
        method_str = args[2].upper() if len(args) > 2 else "UPI"
        tx_id = args[3] if len(args) > 3 else "UPI-COUNTER"
        cashier = args[4] if len(args) > 4 else "Terminal Cashier"

        try:
            method = PaymentMethod(method_str)
        except ValueError:
            method = PaymentMethod.UPI

        payment, receipt = self.service.record_payment(
            invoice_id=inv_id,
            amount=amount,
            payment_method=method,
            transaction_id=tx_id,
            cashier_name=cashier,
        )

        out = [
            f"\n{Ansi.GREEN}{Ansi.BOLD}✓ PAYMENT RECORDED SUCCESSFULLY!{Ansi.RESET}",
            f"  Payment Ref   : {Ansi.WHITE}{payment.payment_ref}{Ansi.RESET}",
            f"  Amount Credited: {Ansi.GREEN}{Ansi.BOLD}{format_currency(payment.amount)}{Ansi.RESET}",
            f"  Payment Mode  : {payment.payment_method.value} (Tx: {payment.transaction_id})",
            f"  Receipt Issued: {Ansi.CYAN}{Ansi.BOLD}{receipt.receipt_number}{Ansi.RESET}",
            f"  Digital Seal  : {Ansi.GRAY}{receipt.receipt_hash[:32]}...{Ansi.RESET}\n",
            ReceiptFormatter.format_text(receipt),
            "",
        ]
        return "\n".join(out)

    def _cmd_receipts(self, args: List[str]) -> str:
        if not args:
            return f"{Ansi.RED}Usage: receipts view <receipt_number> OR receipts verify <receipt_number>{Ansi.RESET}\n"

        sub = args[0].lower()
        if sub in ("verify", "check"):
            rec_num = args[1] if len(args) > 1 else ""
            if not rec_num:
                return f"{Ansi.RED}Usage: receipts verify <receipt_number>{Ansi.RESET}\n"
            is_valid, msg = self.service.verify_receipt(rec_num)
            if is_valid:
                return f"{Ansi.GREEN}{Ansi.BOLD}✓ VERIFIED:{Ansi.RESET} {msg}\n"
            else:
                return f"{Ansi.RED}{Ansi.BOLD}✗ TAMPER DETECTED:{Ansi.RESET} {msg}\n"

        rec_num = args[1] if sub in ("view", "print", "show") and len(args) > 1 else args[0]
        rec = self.service.get_receipt(rec_num)
        if not rec:
            return f"{Ansi.RED}Receipt '{rec_num}' not found in database.{Ansi.RESET}\n"
        return "\n" + ReceiptFormatter.format_text(rec) + "\n"

    def _cmd_defaulters(self, args: List[str]) -> str:
        min_days = 0
        if args and args[0].isdigit():
            min_days = int(args[0])

        report = self.service.get_defaulters_report(min_days_overdue=min_days)
        headers = ["Invoice #", "Student Name", "Class", "Guardian Phone", "Due Date", "Overdue", "Balance Due"]
        rows = []
        for r in report:
            rows.append([
                f"{Ansi.CYAN}{r['invoice_number']}{Ansi.RESET}",
                f"{Ansi.BOLD}{r['student_name']}{Ansi.RESET}",
                r["class_name"],
                f"{Ansi.YELLOW}{r['parent_phone']}{Ansi.RESET}",
                str(r["due_date"]),
                f"{Ansi.RED}{r['days_overdue']} days{Ansi.RESET}",
                f"{Ansi.RED}{Ansi.BOLD}{format_currency(r['balance_due'])}{Ansi.RESET}",
            ])
        return (
            f"\n{Ansi.RED}{Ansi.BOLD}FEE DEFAULTERS LIST ({len(report)} overdue accounts):{Ansi.RESET}\n"
            + render_ascii_table(headers, rows, col_align=["left", "left", "left", "left", "left", "right", "right"])
        )

    def _cmd_reports(self, args: List[str]) -> str:
        sub = args[0].lower() if args else "collection"
        if sub == "collection":
            summary = self.service.get_collection_summary()
            out = [
                f"\n{Ansi.TEAL}{Ansi.BOLD}FINANCIAL REVENUE COLLECTION REPORT{Ansi.RESET}",
                f"Total Collected: {Ansi.GREEN}{Ansi.BOLD}{format_currency(summary['total_collected'])}{Ansi.RESET}",
                f"Receipts Issued: {Ansi.WHITE}{summary['payments_count']}{Ansi.RESET}\n",
                f"{Ansi.BOLD}COLLECTION BY PAYMENT METHOD:{Ansi.RESET}",
            ]
            headers = ["Payment Mode", "Total Credited (₹)"]
            rows = []
            for method, amt in summary["by_method"].items():
                rows.append([method, format_currency(amt)])
            out.append(render_ascii_table(headers, rows, col_align=["left", "right"]))
            return "\n".join(out)

        return f"{Ansi.RED}Unknown report: '{sub}'. Try: collection{Ansi.RESET}\n"

    def _cmd_classes(self, args: List[str]) -> str:
        classes = self.service.get_classes()
        headers = ["Class ID", "Section Name", "Grade Level"]
        rows = [[str(c.id), c.name, f"Grade {c.grade_level}"] for c in classes]
        return f"\n{Ansi.BOLD}ACADEMIC CLASSES ({len(classes)} classes):{Ansi.RESET}\n" + render_ascii_table(headers, rows)
