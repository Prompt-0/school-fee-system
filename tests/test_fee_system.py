"""
Unit test suite for the School Student Fee Management System.
Uses standard library unittest with in-memory or temporary SQLite database.
"""

import os
import tempfile
import unittest
from datetime import date
from decimal import Decimal

from school_fee_system.database import connect_db, initialize_schema, seed_sample_data
from school_fee_system.fee_calculator import FeeCalculator, round_currency
from school_fee_system.models import (
    Student,
    FeeStructure,
    FeeStructureItem,
    FeeTerm,
    DiscountPolicy,
    DiscountType,
    InvoiceStatus,
    PaymentMethod,
)
from school_fee_system.receipt_generator import (
    verify_receipt_hash,
)
from school_fee_system.services import SchoolFeeService


class TestFeeCalculator(unittest.TestCase):
    def setUp(self):
        self.student_standard = Student(
            student_id="STU-TEST-01",
            first_name="Alice",
            last_name="Smith",
            class_id=1,
            parent_name="John Smith",
            parent_email="john@example.com",
            parent_phone="1234567890",
            is_transport_enrolled=False,
            is_hostel_enrolled=False,
        )
        self.student_with_services = Student(
            student_id="STU-TEST-02",
            first_name="Bob",
            last_name="Jones",
            class_id=1,
            parent_name="Mary Jones",
            parent_email="mary@example.com",
            parent_phone="0987654321",
            is_transport_enrolled=True,
            is_hostel_enrolled=True,
        )

        self.structure = FeeStructure(
            id=1,
            name="Grade 10 Term-1",
            class_id=1,
            academic_year="2026-2027",
            term=FeeTerm.TERM_1,
            items=[
                FeeStructureItem(fee_head_id=1, head_name="Tuition", head_code="TUITION", amount=Decimal("1000.00")),
                FeeStructureItem(fee_head_id=2, head_name="Lab", head_code="LAB", amount=Decimal("200.00")),
                FeeStructureItem(fee_head_id=3, head_name="Transport", head_code="TRANSPORT", amount=Decimal("300.00")),
                FeeStructureItem(fee_head_id=4, head_name="Hostel", head_code="HOSTEL", amount=Decimal("500.00")),
            ],
        )

    def test_standard_student_excludes_optional_services(self):
        result = FeeCalculator.compute_student_fees(
            student=self.student_standard,
            structure=self.structure,
            discounts=[],
        )
        # Tuition (1000) + Lab (200) = 1200. Transport & Hostel excluded.
        self.assertEqual(result.subtotal, Decimal("1200.00"))
        self.assertEqual(result.discount_total, Decimal("0.00"))
        self.assertEqual(result.total_payable, Decimal("1200.00"))
        self.assertEqual(len(result.items), 2)

    def test_student_with_all_services_included(self):
        result = FeeCalculator.compute_student_fees(
            student=self.student_with_services,
            structure=self.structure,
            discounts=[],
        )
        # 1000 + 200 + 300 + 500 = 2000.
        self.assertEqual(result.subtotal, Decimal("2000.00"))
        self.assertEqual(result.total_payable, Decimal("2000.00"))
        self.assertEqual(len(result.items), 4)

    def test_percentage_discount_on_tuition(self):
        merit_25 = DiscountPolicy(
            id=1,
            name="25% Merit",
            code="MERIT_25",
            discount_type=DiscountType.PERCENTAGE,
            value=Decimal("25.00"),
            applies_to_head_code="TUITION",
        )
        result = FeeCalculator.compute_student_fees(
            student=self.student_standard,
            structure=self.structure,
            discounts=[merit_25],
        )
        # Tuition discount = 25% of 1000 = 250.
        # Subtotal: 1200, Discount: 250, Total: 950.
        self.assertEqual(result.discount_total, Decimal("250.00"))
        self.assertEqual(result.total_payable, Decimal("950.00"))

    def test_fixed_discount_general(self):
        sibling_flat = DiscountPolicy(
            id=2,
            name="Sibling Discount",
            code="SIBLING_FLAT",
            discount_type=DiscountType.FIXED,
            value=Decimal("150.00"),
            applies_to_head_code=None,
        )
        result = FeeCalculator.compute_student_fees(
            student=self.student_standard,
            structure=self.structure,
            discounts=[sibling_flat],
        )
        self.assertEqual(result.discount_total, Decimal("150.00"))
        self.assertEqual(result.total_payable, Decimal("1050.00"))

    def test_late_fee_calculation_with_grace_period(self):
        due = date(2026, 10, 1)
        # On or before due date
        self.assertEqual(FeeCalculator.calculate_late_fee(due, date(2026, 9, 30)), Decimal("0.00"))
        self.assertEqual(FeeCalculator.calculate_late_fee(due, date(2026, 10, 1)), Decimal("0.00"))

        # Within 7-day grace period (due + 7 days = 2026-10-08)
        self.assertEqual(FeeCalculator.calculate_late_fee(due, date(2026, 10, 8), grace_period_days=7), Decimal("0.00"))

        # 10 days overdue at $5/day
        overdue_date = date(2026, 10, 11)
        self.assertEqual(
            FeeCalculator.calculate_late_fee(due, overdue_date, grace_period_days=7, rate_per_day=Decimal("5.00")),
            Decimal("50.00"),
        )

        # Capped late fee test: 40 days overdue ($200 raw) capped at $150
        far_overdue = date(2026, 11, 10)
        self.assertEqual(
            FeeCalculator.calculate_late_fee(due, far_overdue, max_cap=Decimal("150.00")),
            Decimal("150.00"),
        )


class TestSchoolFeeServiceIntegration(unittest.TestCase):
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

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_seed_data_loaded_successfully(self):
        classes = self.service.get_classes()
        self.assertGreaterEqual(len(classes), 4)

        students = self.service.list_students()
        self.assertGreaterEqual(len(students), 5)

        heads = self.service.get_fee_heads()
        self.assertTrue(any(h.code == "TUITION" for h in heads))

    def test_generate_invoice_lifecycle_and_discounts(self):
        # STU-2026-001 (Aarav) has 25% merit discount on tuition (₹12,000 * 25% = ₹3,000)
        inv = self.service.generate_student_invoice(
            student_id="STU-2026-001",
            academic_year="2026-2027",
            term=FeeTerm.TERM_1,
        )
        self.assertIsNotNone(inv.id)
        self.assertTrue(inv.invoice_number.startswith("INV-"))
        self.assertEqual(inv.status, InvoiceStatus.UNPAID)
        self.assertEqual(inv.discount_total, Decimal("3000.00"))
        self.assertEqual(inv.paid_amount, Decimal("0.00"))
        self.assertGreater(inv.total_payable, Decimal("0.00"))

        # Duplicate invoice attempt must raise error
        with self.assertRaises(ValueError):
            self.service.generate_student_invoice(
                student_id="STU-2026-001",
                academic_year="2026-2027",
                term=FeeTerm.TERM_1,
            )

    def test_partial_and_full_payment_with_receipt_verification(self):
        inv = self.service.generate_student_invoice(
            student_id="STU-2026-002",
            academic_year="2026-2027",
            term=FeeTerm.TERM_1,
        )
        total = inv.total_payable

        # 1. Partial payment: Pay half
        half_amt = round_currency(total / Decimal("2.00"))
        pay1, rec1 = self.service.record_payment(
            invoice_id=inv.id,
            amount=half_amt,
            payment_method=PaymentMethod.CASH,
            transaction_id="COUNTER-101",
            cashier_name="Cashier John",
        )
        self.assertEqual(pay1.amount, half_amt)
        self.assertTrue(rec1.receipt_number.startswith("REC-"))

        # Check invoice status is PARTIALLY_PAID
        inv_updated = self.service.get_invoice(inv.id)
        self.assertEqual(inv_updated.status, InvoiceStatus.PARTIALLY_PAID)
        self.assertEqual(inv_updated.paid_amount, half_amt)
        self.assertEqual(inv_updated.balance_amount, total - half_amt)

        # Cryptographic verification of receipt 1
        is_valid, msg = self.service.verify_receipt(rec1.receipt_number)
        self.assertTrue(is_valid)

        # 2. Complete remaining balance
        rem = inv_updated.balance_amount
        pay2, rec2 = self.service.record_payment(
            invoice_id=inv.id,
            amount=rem,
            payment_method=PaymentMethod.UPI,
            transaction_id="UPI-TX-998877",
            cashier_name="Cashier John",
        )
        inv_final = self.service.get_invoice(inv.id)
        self.assertEqual(inv_final.status, InvoiceStatus.PAID)
        self.assertEqual(inv_final.balance_amount, Decimal("0.00"))

        # Overpayment should be prevented
        with self.assertRaises(ValueError):
            self.service.record_payment(
                invoice_id=inv.id,
                amount=Decimal("10.00"),
                payment_method=PaymentMethod.CASH,
                transaction_id="FAIL",
            )

    def test_tampered_receipt_fails_verification(self):
        inv = self.service.generate_student_invoice(
            student_id="STU-2026-004",
            academic_year="2026-2027",
            term=FeeTerm.TERM_1,
        )
        pay, rec = self.service.record_payment(
            invoice_id=inv.id,
            amount=Decimal("100.00"),
            payment_method=PaymentMethod.CASH,
            transaction_id="COUNTER-TX",
        )

        # Tamper check directly with hash verification function
        is_authentic = verify_receipt_hash(
            receipt_number=rec.receipt_number,
            payment_ref=pay.payment_ref,
            amount=Decimal("999.00"),  # Tampered amount!
            student_id="STU-2026-004",
            date_str=rec.created_at.isoformat(),
            expected_hash=rec.receipt_hash,
        )
        self.assertFalse(is_authentic)

    def test_reports_and_csv_export(self):
        # Generate and pay one invoice to have metrics
        inv = self.service.generate_student_invoice(
            student_id="STU-2026-005",
            academic_year="2026-2027",
            term=FeeTerm.TERM_1,
        )
        self.service.record_payment(
            invoice_id=inv.id,
            amount=Decimal("200.00"),
            payment_method=PaymentMethod.BANK_TRANSFER,
            transaction_id="WIRE-12345",
        )

        kpis = self.service.get_kpis()
        self.assertGreaterEqual(kpis["active_students"], 5)
        self.assertGreaterEqual(kpis["total_collected"], Decimal("200.00"))

        col_csv = self.service.export_collection_csv()
        self.assertIn("Payment Ref", col_csv)
        self.assertIn("WIRE-12345", col_csv)

        def_csv = self.service.export_defaulters_csv()
        self.assertIn("Invoice #", def_csv)


if __name__ == "__main__":
    unittest.main()
