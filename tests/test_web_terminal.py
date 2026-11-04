"""
Unit tests for the Web Terminal Subproject (shell engine, ANSI table rendering, and commands).
"""

import os
import tempfile
import unittest
from decimal import Decimal

from school_fee_system.database import connect_db, initialize_schema, seed_sample_data
from school_fee_system.models import FeeTerm
from school_fee_system.services import SchoolFeeService
from web_terminal.shell import TerminalShell, _strip_ansi, format_currency


class TestWebTerminalShell(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.db_path = self.temp_db.name
        self.service = SchoolFeeService(db_path=self.db_path)

        conn = connect_db(self.db_path)
        try:
            initialize_schema(conn)
            seed_sample_data(conn)
        finally:
            conn.close()

        # Seed at least one invoice for testing
        self.test_invoice = self.service.generate_student_invoice(
            student_id="STU-2026-001",
            academic_year="2026-2027",
            term=FeeTerm.TERM_1,
        )
        self.shell = TerminalShell(service=self.service)

    def tearDown(self):
        try:
            os.remove(self.db_path)
        except OSError:
            pass

    def test_help_command(self):
        output = self.shell.execute("help")
        plain = _strip_ansi(output)
        self.assertIn("AVAILABLE COMMANDS & CHEATSHEET", plain)
        self.assertIn("students list", plain)
        self.assertIn("defaulters", plain)
        self.assertIn("invoices", plain)

    def test_kpis_command(self):
        output = self.shell.execute("kpis")
        plain = _strip_ansi(output)
        self.assertIn("DELHI PUBLIC ACADEMY", plain)
        self.assertIn("ACTIVE PUPILS", plain)
        self.assertIn("TOTAL COLLECTED", plain)

    def test_students_list(self):
        output = self.shell.execute("students list")
        plain = _strip_ansi(output)
        self.assertIn("ENROLLED STUDENTS", plain)
        self.assertIn("STU-2026-001", plain)
        self.assertIn("Aarav Sharma", plain)

    def test_students_view(self):
        output = self.shell.execute("students view STU-2026-001")
        plain = _strip_ansi(output)
        self.assertIn("STUDENT ACCOUNT STATEMENT: Aarav Sharma", plain)
        self.assertIn("Billed:", plain)
        self.assertIn("Paid:", plain)

    def test_invoices_list(self):
        output = self.shell.execute("invoices list")
        plain = _strip_ansi(output)
        self.assertIn("FEE INVOICES", plain)
        self.assertIn(self.test_invoice.invoice_number, plain)

    def test_invoices_view(self):
        output = self.shell.execute(f"invoices view {self.test_invoice.invoice_number}")
        plain = _strip_ansi(output)
        self.assertIn(f"INVOICE DETAILS: {self.test_invoice.invoice_number}", plain)
        self.assertIn("Tuition Fee", plain)
        self.assertIn("Total Payable:", plain)

    def test_pay_and_receipts_workflow(self):
        # Record payment
        pay_out = self.shell.execute(f"pay {self.test_invoice.id} 5000 UPI TX-SHELL-99 Admin")
        plain_pay = _strip_ansi(pay_out)
        self.assertIn("PAYMENT RECORDED SUCCESSFULLY", plain_pay)
        self.assertIn("₹5,000.00", plain_pay)
        self.assertIn("OFFICIAL FEE PAYMENT RECEIPT", plain_pay)

        # View receipt
        rec_out = self.shell.execute("receipts view REC-2026-0001")
        plain_rec = _strip_ansi(rec_out)
        self.assertIn("DELHI PUBLIC ACADEMY", plain_rec)
        self.assertIn("REC-2026-0001", plain_rec)

        # Verify receipt
        ver_out = self.shell.execute("receipts verify REC-2026-0001")
        plain_ver = _strip_ansi(ver_out)
        self.assertIn("VERIFIED", plain_ver)

    def test_defaulters_command(self):
        output = self.shell.execute("defaulters")
        plain = _strip_ansi(output)
        self.assertIn("FEE DEFAULTERS LIST", plain)

    def test_reports_collection_command(self):
        output = self.shell.execute("reports collection")
        plain = _strip_ansi(output)
        self.assertIn("FINANCIAL REVENUE COLLECTION REPORT", plain)
        self.assertIn("Total Collected:", plain)

    def test_unknown_command(self):
        output = self.shell.execute("gibberish_command_xyz")
        plain = _strip_ansi(output)
        self.assertIn("Command not recognized", plain)


if __name__ == "__main__":
    unittest.main()
