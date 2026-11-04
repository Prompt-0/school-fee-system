"""
Business Service Layer orchestrating database persistence, domain logic,
invoice lifecycle, payment recording, and reporting.
"""

from __future__ import annotations

import csv
import io
import json
import sqlite3
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Tuple, Dict, Any

from school_fee_system.database import connect_db
from school_fee_system.fee_calculator import FeeCalculator, round_currency
from school_fee_system.models import (
    Student,
    StudentStatus,
    ClassSection,
    FeeHead,
    FeeStructure,
    FeeStructureItem,
    FeeTerm,
    DiscountPolicy,
    DiscountType,
    Invoice,
    InvoiceItem,
    InvoiceStatus,
    Payment,
    PaymentMethod,
    Receipt,
)
from school_fee_system.receipt_generator import (
    compute_receipt_hash,
    verify_receipt_hash,
)


class SchoolFeeService:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        return connect_db(self.db_path)

    # -------------------------------------------------------------------------
    # Students & Classes
    # -------------------------------------------------------------------------
    def get_classes(self) -> List[ClassSection]:
        conn = self._get_connection()
        try:
            rows = conn.execute("SELECT id, name, grade_level, created_at FROM classes ORDER BY grade_level, name").fetchall()
            return [ClassSection(id=r["id"], name=r["name"], grade_level=r["grade_level"]) for r in rows]
        finally:
            conn.close()

    def add_class(self, name: str, grade_level: int) -> ClassSection:
        conn = self._get_connection()
        try:
            with conn:
                cur = conn.cursor()
                cur.execute("INSERT INTO classes (name, grade_level) VALUES (?, ?)", (name, grade_level))
                return ClassSection(id=cur.lastrowid, name=name, grade_level=grade_level)
        finally:
            conn.close()

    def get_student(self, student_id: str) -> Optional[Student]:
        conn = self._get_connection()
        try:
            row = conn.execute(
                """SELECT s.*, c.name as class_name 
                   FROM students s 
                   JOIN classes c ON s.class_id = c.id 
                   WHERE s.student_id = ?""",
                (student_id,),
            ).fetchone()
            if not row:
                return None
            return Student(
                student_id=row["student_id"],
                first_name=row["first_name"],
                last_name=row["last_name"],
                class_id=row["class_id"],
                parent_name=row["parent_name"],
                parent_email=row["parent_email"],
                parent_phone=row["parent_phone"],
                is_transport_enrolled=bool(row["is_transport_enrolled"]),
                is_hostel_enrolled=bool(row["is_hostel_enrolled"]),
                status=StudentStatus(row["status"]),
                class_name=row["class_name"],
            )
        finally:
            conn.close()

    def list_students(self, class_id: Optional[int] = None, search: Optional[str] = None) -> List[Student]:
        conn = self._get_connection()
        try:
            query = """SELECT s.*, c.name as class_name 
                       FROM students s 
                       JOIN classes c ON s.class_id = c.id 
                       WHERE 1=1"""
            params: List[Any] = []
            if class_id:
                query += " AND s.class_id = ?"
                params.append(class_id)
            if search:
                query += " AND (s.first_name LIKE ? OR s.last_name LIKE ? OR s.student_id LIKE ?)"
                like_term = f"%{search}%"
                params.extend([like_term, like_term, like_term])
            query += " ORDER BY c.grade_level, s.last_name, s.first_name"

            rows = conn.execute(query, params).fetchall()
            return [
                Student(
                    student_id=r["student_id"],
                    first_name=r["first_name"],
                    last_name=r["last_name"],
                    class_id=r["class_id"],
                    parent_name=r["parent_name"],
                    parent_email=r["parent_email"],
                    parent_phone=r["parent_phone"],
                    is_transport_enrolled=bool(r["is_transport_enrolled"]),
                    is_hostel_enrolled=bool(r["is_hostel_enrolled"]),
                    status=StudentStatus(r["status"]),
                    class_name=r["class_name"],
                )
                for r in rows
            ]
        finally:
            conn.close()

    def add_student(self, student: Student) -> Student:
        conn = self._get_connection()
        try:
            with conn:
                conn.execute(
                    """INSERT INTO students 
                    (student_id, first_name, last_name, class_id, parent_name, parent_email, parent_phone, is_transport_enrolled, is_hostel_enrolled, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        student.student_id,
                        student.first_name,
                        student.last_name,
                        student.class_id,
                        student.parent_name,
                        student.parent_email,
                        student.parent_phone,
                        1 if student.is_transport_enrolled else 0,
                        1 if student.is_hostel_enrolled else 0,
                        student.status.value,
                    ),
                )
                self._log_audit(conn, "STUDENT", student.student_id, "CREATE", "Admin", {"name": student.full_name})
            return student
        finally:
            conn.close()

    # -------------------------------------------------------------------------
    # Fee Structures & Discounts
    # -------------------------------------------------------------------------
    def get_fee_heads(self) -> List[FeeHead]:
        conn = self._get_connection()
        try:
            rows = conn.execute("SELECT * FROM fee_heads ORDER BY is_optional, id").fetchall()
            return [
                FeeHead(
                    id=r["id"],
                    name=r["name"],
                    code=r["code"],
                    description=r["description"] or "",
                    is_recurring=bool(r["is_recurring"]),
                    is_optional=bool(r["is_optional"]),
                )
                for r in rows
            ]
        finally:
            conn.close()

    def get_fee_structure(self, class_id: int, academic_year: str, term: FeeTerm) -> Optional[FeeStructure]:
        conn = self._get_connection()
        try:
            row = conn.execute(
                """SELECT fs.*, c.name as class_name 
                   FROM fee_structures fs 
                   JOIN classes c ON fs.class_id = c.id 
                   WHERE fs.class_id = ? AND fs.academic_year = ? AND fs.term = ?""",
                (class_id, academic_year, term.value),
            ).fetchone()
            if not row:
                return None

            items_rows = conn.execute(
                """SELECT fsi.*, fh.name as head_name, fh.code as head_code 
                   FROM fee_structure_items fsi 
                   JOIN fee_heads fh ON fsi.fee_head_id = fh.id 
                   WHERE fsi.fee_structure_id = ?""",
                (row["id"],),
            ).fetchall()

            items = [
                FeeStructureItem(
                    fee_head_id=ir["fee_head_id"],
                    head_name=ir["head_name"],
                    head_code=ir["head_code"],
                    amount=Decimal(ir["amount"]),
                )
                for ir in items_rows
            ]

            return FeeStructure(
                id=row["id"],
                name=row["name"],
                class_id=row["class_id"],
                academic_year=row["academic_year"],
                term=FeeTerm(row["term"]),
                items=items,
                class_name=row["class_name"],
            )
        finally:
            conn.close()

    def list_fee_structures(self) -> List[FeeStructure]:
        conn = self._get_connection()
        try:
            rows = conn.execute(
                """SELECT fs.*, c.name as class_name 
                   FROM fee_structures fs 
                   JOIN classes c ON fs.class_id = c.id 
                   ORDER BY fs.academic_year DESC, c.grade_level"""
            ).fetchall()

            structures: List[FeeStructure] = []
            for r in rows:
                items_rows = conn.execute(
                    """SELECT fsi.*, fh.name as head_name, fh.code as head_code 
                       FROM fee_structure_items fsi 
                       JOIN fee_heads fh ON fsi.fee_head_id = fh.id 
                       WHERE fsi.fee_structure_id = ?""",
                    (r["id"],),
                ).fetchall()
                items = [
                    FeeStructureItem(
                        fee_head_id=ir["fee_head_id"],
                        head_name=ir["head_name"],
                        head_code=ir["head_code"],
                        amount=Decimal(ir["amount"]),
                    )
                    for ir in items_rows
                ]
                structures.append(
                    FeeStructure(
                        id=r["id"],
                        name=r["name"],
                        class_id=r["class_id"],
                        academic_year=r["academic_year"],
                        term=FeeTerm(r["term"]),
                        items=items,
                        class_name=r["class_name"],
                    )
                )
            return structures
        finally:
            conn.close()

    def get_discount_policies(self) -> List[DiscountPolicy]:
        conn = self._get_connection()
        try:
            rows = conn.execute("SELECT * FROM discount_policies ORDER BY name").fetchall()
            return [
                DiscountPolicy(
                    id=r["id"],
                    name=r["name"],
                    code=r["code"],
                    discount_type=DiscountType(r["discount_type"]),
                    value=Decimal(r["value"]),
                    applies_to_head_code=r["applies_to_head_code"],
                    description=r["description"] or "",
                )
                for r in rows
            ]
        finally:
            conn.close()

    def get_student_discounts(self, student_id: str, academic_year: str) -> List[DiscountPolicy]:
        conn = self._get_connection()
        try:
            rows = conn.execute(
                """SELECT dp.* 
                   FROM student_discounts sd 
                   JOIN discount_policies dp ON sd.discount_policy_id = dp.id 
                   WHERE sd.student_id = ? AND sd.academic_year = ?""",
                (student_id, academic_year),
            ).fetchall()
            return [
                DiscountPolicy(
                    id=r["id"],
                    name=r["name"],
                    code=r["code"],
                    discount_type=DiscountType(r["discount_type"]),
                    value=Decimal(r["value"]),
                    applies_to_head_code=r["applies_to_head_code"],
                    description=r["description"] or "",
                )
                for r in rows
            ]
        finally:
            conn.close()

    # -------------------------------------------------------------------------
    # Invoicing & Calculation
    # -------------------------------------------------------------------------
    def generate_student_invoice(
        self,
        student_id: str,
        academic_year: str,
        term: FeeTerm,
        issue_date: Optional[date] = None,
        due_date: Optional[date] = None,
    ) -> Invoice:
        student = self.get_student(student_id)
        if not student:
            raise ValueError(f"Student '{student_id}' does not exist.")

        structure = self.get_fee_structure(student.class_id, academic_year, term)
        if not structure:
            raise ValueError(
                f"No fee structure defined for class '{student.class_name}', academic year '{academic_year}', term '{term.value}'."
            )

        discounts = self.get_student_discounts(student_id, academic_year)
        issue_d = issue_date or date.today()
        # Default due date: 21 days from issue date
        due_d = due_date or (issue_d.replace(day=min(28, issue_d.day + 21)) if issue_d.day + 21 <= 28 else issue_d)

        calc = FeeCalculator.compute_student_fees(
            student=student,
            structure=structure,
            discounts=discounts,
            as_of_date=date.today(),
            due_date=due_d,
            include_late_fee=False,  # Newly generated invoices start without late fee
        )

        conn = self._get_connection()
        try:
            with conn:
                cur = conn.cursor()
                # Check for existing invoice
                existing = cur.execute(
                    "SELECT id, invoice_number FROM invoices WHERE student_id = ? AND academic_year = ? AND term = ?",
                    (student_id, academic_year, term.value),
                ).fetchone()
                if existing:
                    raise ValueError(f"Invoice already exists for {student_id} ({term.value}): {existing['invoice_number']}")

                # Generate invoice number: INV-YEAR-0001
                count_res = cur.execute("SELECT COUNT(*) FROM invoices").fetchone()[0]
                inv_number = f"INV-{date.today().year}-{(count_res + 1):04d}"

                cur.execute(
                    """INSERT INTO invoices 
                    (invoice_number, student_id, academic_year, term, issue_date, due_date, subtotal, discount_total, late_fee, total_payable, paid_amount, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '0.00', 'UNPAID')""",
                    (
                        inv_number,
                        student_id,
                        academic_year,
                        term.value,
                        issue_d.isoformat(),
                        due_d.isoformat(),
                        str(calc.subtotal),
                        str(calc.discount_total),
                        str(calc.late_fee),
                        str(calc.total_payable),
                    ),
                )
                inv_id = cur.lastrowid

                # Insert items
                for it in calc.items:
                    cur.execute(
                        """INSERT INTO invoice_items 
                        (invoice_id, fee_head_id, head_name, head_code, amount, discount_amount, net_amount)
                        VALUES (?, ?, ?, ?, ?, ?, ?)""",
                        (
                            inv_id,
                            it.fee_head_id,
                            it.head_name,
                            it.head_code,
                            str(it.amount),
                            str(it.discount_amount),
                            str(it.net_amount),
                        ),
                    )

                self._log_audit(
                    conn,
                    "INVOICE",
                    inv_number,
                    "CREATE",
                    "System",
                    {"student_id": student_id, "amount": str(calc.total_payable)},
                )
        finally:
            conn.close()

        inv = self.get_invoice(inv_id)
        if not inv:
            raise RuntimeError(f"Failed to retrieve generated invoice #{inv_id}")
        return inv

    def generate_batch_invoices_for_class(
        self,
        class_id: int,
        academic_year: str,
        term: FeeTerm,
        issue_date: Optional[date] = None,
        due_date: Optional[date] = None,
    ) -> List[Invoice]:
        """Generates invoices in batch for all active students in a given class."""
        students = self.list_students(class_id=class_id)
        invoices: List[Invoice] = []
        for s in students:
            if s.status != StudentStatus.ACTIVE:
                continue
            try:
                inv = self.generate_student_invoice(
                    student_id=s.student_id,
                    academic_year=academic_year,
                    term=term,
                    issue_date=issue_date,
                    due_date=due_date,
                )
                invoices.append(inv)
            except ValueError:
                # Skip already generated or non-matching records
                continue
        return invoices

    def get_invoice(self, invoice_id_or_num: Any) -> Optional[Invoice]:
        conn = self._get_connection()
        try:
            if isinstance(invoice_id_or_num, int) or (isinstance(invoice_id_or_num, str) and invoice_id_or_num.isdigit()):
                query = "SELECT i.*, s.first_name, s.last_name, s.parent_email, s.parent_phone, c.name as class_name FROM invoices i JOIN students s ON i.student_id = s.student_id JOIN classes c ON s.class_id = c.id WHERE i.id = ?"
                param = int(invoice_id_or_num)
            else:
                query = "SELECT i.*, s.first_name, s.last_name, s.parent_email, s.parent_phone, c.name as class_name FROM invoices i JOIN students s ON i.student_id = s.student_id JOIN classes c ON s.class_id = c.id WHERE i.invoice_number = ?"
                param = str(invoice_id_or_num)

            row = conn.execute(query, (param,)).fetchone()
            if not row:
                return None

            items_rows = conn.execute(
                "SELECT * FROM invoice_items WHERE invoice_id = ?",
                (row["id"],),
            ).fetchall()

            items = [
                InvoiceItem(
                    id=ir["id"],
                    fee_head_id=ir["fee_head_id"],
                    head_name=ir["head_name"],
                    head_code=ir["head_code"],
                    amount=Decimal(ir["amount"]),
                    discount_amount=Decimal(ir["discount_amount"]),
                    net_amount=Decimal(ir["net_amount"]),
                )
                for ir in items_rows
            ]

            return Invoice(
                id=row["id"],
                invoice_number=row["invoice_number"],
                student_id=row["student_id"],
                academic_year=row["academic_year"],
                term=FeeTerm(row["term"]),
                issue_date=date.fromisoformat(row["issue_date"]),
                due_date=date.fromisoformat(row["due_date"]),
                subtotal=Decimal(row["subtotal"]),
                discount_total=Decimal(row["discount_total"]),
                late_fee=Decimal(row["late_fee"]),
                total_payable=Decimal(row["total_payable"]),
                paid_amount=Decimal(row["paid_amount"]),
                status=InvoiceStatus(row["status"]),
                items=items,
                student_name=f"{row['first_name']} {row['last_name']}",
                class_name=row["class_name"],
                parent_email=row["parent_email"],
                parent_phone=row["parent_phone"],
            )
        finally:
            conn.close()

    def list_invoices(
        self,
        student_id: Optional[str] = None,
        status: Optional[InvoiceStatus] = None,
        class_id: Optional[int] = None,
    ) -> List[Invoice]:
        conn = self._get_connection()
        try:
            query = """SELECT i.*, s.first_name, s.last_name, s.parent_email, s.parent_phone, c.name as class_name 
                       FROM invoices i 
                       JOIN students s ON i.student_id = s.student_id 
                       JOIN classes c ON s.class_id = c.id 
                       WHERE 1=1"""
            params: List[Any] = []
            if student_id:
                query += " AND i.student_id = ?"
                params.append(student_id)
            if status:
                query += " AND i.status = ?"
                params.append(status.value)
            if class_id:
                query += " AND s.class_id = ?"
                params.append(class_id)
            query += " ORDER BY i.due_date ASC, i.id DESC"

            rows = conn.execute(query, params).fetchall()
            results = []
            for r in rows:
                results.append(
                    Invoice(
                        id=r["id"],
                        invoice_number=r["invoice_number"],
                        student_id=r["student_id"],
                        academic_year=r["academic_year"],
                        term=FeeTerm(r["term"]),
                        issue_date=date.fromisoformat(r["issue_date"]),
                        due_date=date.fromisoformat(r["due_date"]),
                        subtotal=Decimal(r["subtotal"]),
                        discount_total=Decimal(r["discount_total"]),
                        late_fee=Decimal(r["late_fee"]),
                        total_payable=Decimal(r["total_payable"]),
                        paid_amount=Decimal(r["paid_amount"]),
                        status=InvoiceStatus(r["status"]),
                        student_name=f"{r['first_name']} {r['last_name']}",
                        class_name=r["class_name"],
                        parent_email=r["parent_email"],
                        parent_phone=r["parent_phone"],
                    )
                )
            return results
        finally:
            conn.close()

    def assess_and_apply_late_fees(self, as_of_date: Optional[date] = None) -> int:
        """
        Scans unpaid and partially paid invoices past their grace period,
        computes applicable late fee, and updates total payable and status to OVERDUE.
        """
        curr_d = as_of_date or date.today()
        conn = self._get_connection()
        updated_count = 0
        try:
            with conn:
                cur = conn.cursor()
                unpaid_rows = cur.execute(
                    "SELECT * FROM invoices WHERE status IN ('UNPAID', 'PARTIALLY_PAID', 'OVERDUE')"
                ).fetchall()

                for row in unpaid_rows:
                    due_d = date.fromisoformat(row["due_date"])
                    new_late_fee = FeeCalculator.calculate_late_fee(due_date=due_d, as_of_date=curr_d)
                    existing_late_fee = Decimal(row["late_fee"])
                    subtotal = Decimal(row["subtotal"])
                    disc = Decimal(row["discount_total"])
                    paid = Decimal(row["paid_amount"])

                    if new_late_fee != existing_late_fee:
                        new_total = round_currency((subtotal - disc) + new_late_fee)
                        new_status = "OVERDUE" if curr_d > due_d and paid < new_total else row["status"]
                        cur.execute(
                            "UPDATE invoices SET late_fee = ?, total_payable = ?, status = ? WHERE id = ?",
                            (str(new_late_fee), str(new_total), new_status, row["id"]),
                        )
                        updated_count += 1
                    elif curr_d > due_d and row["status"] in ("UNPAID", "PARTIALLY_PAID"):
                        cur.execute(
                            "UPDATE invoices SET status = 'OVERDUE' WHERE id = ?",
                            (row["id"],),
                        )
                        updated_count += 1
            return updated_count
        finally:
            conn.close()

    # -------------------------------------------------------------------------
    # Payments & Receipts
    # -------------------------------------------------------------------------
    def record_payment(
        self,
        invoice_id: int,
        amount: Decimal,
        payment_method: PaymentMethod,
        transaction_id: str,
        cashier_name: str = "Admin",
        notes: str = "",
    ) -> Tuple[Payment, Receipt]:
        amount = round_currency(amount)
        if amount <= Decimal("0.00"):
            raise ValueError("Payment amount must be greater than zero.")

        conn = self._get_connection()
        try:
            with conn:
                cur = conn.cursor()
                inv_row = cur.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,)).fetchone()
                if not inv_row:
                    raise ValueError(f"Invoice #{invoice_id} not found.")

                total_payable = Decimal(inv_row["total_payable"])
                current_paid = Decimal(inv_row["paid_amount"])
                balance = total_payable - current_paid

                if amount > balance:
                    raise ValueError(f"Payment amount (${amount:.2f}) exceeds outstanding balance (${balance:.2f}).")

                new_paid = round_currency(current_paid + amount)
                new_status = InvoiceStatus.PAID.value if new_paid >= total_payable else InvoiceStatus.PARTIALLY_PAID.value

                # 1. Update invoice
                cur.execute(
                    "UPDATE invoices SET paid_amount = ?, status = ? WHERE id = ?",
                    (str(new_paid), new_status, invoice_id),
                )

                # 2. Record payment
                pay_count = cur.execute("SELECT COUNT(*) FROM payments").fetchone()[0]
                pay_ref = f"PAY-{date.today().year}-{(pay_count + 1):04d}"
                now = datetime.now()

                cur.execute(
                    """INSERT INTO payments 
                    (payment_ref, invoice_id, amount, payment_method, transaction_id, payment_date, cashier_name, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        pay_ref,
                        invoice_id,
                        str(amount),
                        payment_method.value,
                        transaction_id,
                        now.isoformat(),
                        cashier_name,
                        notes,
                    ),
                )
                payment_id = cur.lastrowid

                # 3. Generate Receipt & Audit Hash
                rec_count = cur.execute("SELECT COUNT(*) FROM receipts").fetchone()[0]
                rec_number = f"REC-{date.today().year}-{(rec_count + 1):04d}"
                date_str = now.isoformat()
                rec_hash = compute_receipt_hash(
                    receipt_number=rec_number,
                    payment_ref=pay_ref,
                    amount=amount,
                    student_id=inv_row["student_id"],
                    date_str=date_str,
                )

                cur.execute(
                    "INSERT INTO receipts (receipt_number, payment_id, receipt_hash, created_at) VALUES (?, ?, ?, ?)",
                    (rec_number, payment_id, rec_hash, date_str),
                )
                rec_id = cur.lastrowid

                self._log_audit(
                    conn,
                    "PAYMENT",
                    pay_ref,
                    "COLLECT",
                    cashier_name,
                    {"amount": str(amount), "invoice": inv_row["invoice_number"], "receipt": rec_number},
                )

                payment = Payment(
                    id=payment_id,
                    payment_ref=pay_ref,
                    invoice_id=invoice_id,
                    amount=amount,
                    payment_method=payment_method,
                    transaction_id=transaction_id,
                    payment_date=now,
                    cashier_name=cashier_name,
                    notes=notes,
                    invoice_number=inv_row["invoice_number"],
                    student_id=inv_row["student_id"],
                )
        finally:
            conn.close()

        receipt = self.get_receipt(rec_id)
        if not receipt:
            raise RuntimeError("Failed to retrieve generated receipt.")

        return payment, receipt

    def get_receipt(self, receipt_id_or_number: Any) -> Optional[Receipt]:
        conn = self._get_connection()
        try:
            if isinstance(receipt_id_or_number, int) or (isinstance(receipt_id_or_number, str) and receipt_id_or_number.isdigit()):
                query = "SELECT * FROM receipts WHERE id = ?"
                param = int(receipt_id_or_number)
            else:
                query = "SELECT * FROM receipts WHERE receipt_number = ?"
                param = str(receipt_id_or_number)

            row = conn.execute(query, (param,)).fetchone()
            if not row:
                return None

            pay_row = conn.execute("SELECT * FROM payments WHERE id = ?", (row["payment_id"],)).fetchone()
            if not pay_row:
                return None

            inv = self.get_invoice(pay_row["invoice_id"])
            stu = self.get_student(inv.student_id) if inv else None

            payment = Payment(
                id=pay_row["id"],
                payment_ref=pay_row["payment_ref"],
                invoice_id=pay_row["invoice_id"],
                amount=Decimal(pay_row["amount"]),
                payment_method=PaymentMethod(pay_row["payment_method"]),
                transaction_id=pay_row["transaction_id"],
                payment_date=datetime.fromisoformat(pay_row["payment_date"]),
                cashier_name=pay_row["cashier_name"],
                notes=pay_row["notes"] or "",
            )

            return Receipt(
                id=row["id"],
                receipt_number=row["receipt_number"],
                payment_id=row["payment_id"],
                receipt_hash=row["receipt_hash"],
                created_at=datetime.fromisoformat(row["created_at"]),
                payment=payment,
                invoice=inv,
                student=stu,
            )
        finally:
            conn.close()

    def verify_receipt(self, receipt_number: str) -> Tuple[bool, str]:
        """Validates receipt authenticity against the cryptographic hash."""
        receipt = self.get_receipt(receipt_number)
        if not receipt:
            return False, "Receipt not found in database."

        p = receipt.payment
        if not p or not receipt.student:
            return False, "Corrupt or incomplete payment reference linked to receipt."

        is_valid = verify_receipt_hash(
            receipt_number=receipt.receipt_number,
            payment_ref=p.payment_ref,
            amount=p.amount,
            student_id=receipt.student.student_id,
            date_str=receipt.created_at.isoformat(),
            expected_hash=receipt.receipt_hash,
        )

        if is_valid:
            return True, f"VERIFIED AUTHENTIC: Receipt {receipt_number} matches cryptographic signature."
        else:
            return False, "ALERT: Receipt hash mismatch! Record may have been modified outside the system."

    # -------------------------------------------------------------------------
    # Reports & Analytics
    # -------------------------------------------------------------------------
    def get_kpis(self) -> Dict[str, Any]:
        """Calculates dashboard executive KPIs."""
        conn = self._get_connection()
        try:
            total_students = conn.execute("SELECT COUNT(*) FROM students WHERE status = 'ACTIVE'").fetchone()[0]
            collected_res = conn.execute("SELECT COALESCE(SUM(CAST(amount AS REAL)), 0.0) FROM payments").fetchone()[0]
            outstanding_res = conn.execute(
                """SELECT COALESCE(SUM(CAST(total_payable AS REAL) - CAST(paid_amount AS REAL)), 0.0) 
                   FROM invoices WHERE status IN ('UNPAID', 'PARTIALLY_PAID', 'OVERDUE')"""
            ).fetchone()[0]
            defaulters_count = conn.execute(
                "SELECT COUNT(DISTINCT student_id) FROM invoices WHERE status = 'OVERDUE' OR (status IN ('UNPAID', 'PARTIALLY_PAID') AND due_date < date('now'))"
            ).fetchone()[0]

            return {
                "active_students": total_students,
                "total_collected": Decimal(f"{collected_res:.2f}"),
                "total_outstanding": Decimal(f"{outstanding_res:.2f}"),
                "defaulters_count": defaulters_count,
            }
        finally:
            conn.close()

    def get_defaulters_report(self, min_days_overdue: int = 0, class_id: Optional[int] = None) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            today = date.today().isoformat()
            query = """SELECT i.invoice_number, i.due_date, i.total_payable, i.paid_amount,
                              s.student_id, s.first_name, s.last_name, s.parent_name, s.parent_phone, s.parent_email,
                              c.name as class_name,
                              (julianday(?) - julianday(i.due_date)) as days_overdue
                       FROM invoices i
                       JOIN students s ON i.student_id = s.student_id
                       JOIN classes c ON s.class_id = c.id
                       WHERE (i.status = 'OVERDUE' OR (i.status IN ('UNPAID', 'PARTIALLY_PAID') AND i.due_date < ?))"""
            params: List[Any] = [today, today]
            if class_id:
                query += " AND s.class_id = ?"
                params.append(class_id)
            query += " ORDER BY days_overdue DESC, i.due_date ASC"

            rows = conn.execute(query, params).fetchall()
            results = []
            for r in rows:
                days_overdue = int(r["days_overdue"])
                if days_overdue >= min_days_overdue:
                    bal = Decimal(r["total_payable"]) - Decimal(r["paid_amount"])
                    results.append(
                        {
                            "invoice_number": r["invoice_number"],
                            "student_id": r["student_id"],
                            "student_name": f"{r['first_name']} {r['last_name']}",
                            "class_name": r["class_name"],
                            "parent_name": r["parent_name"],
                            "parent_phone": r["parent_phone"],
                            "parent_email": r["parent_email"],
                            "due_date": r["due_date"],
                            "days_overdue": days_overdue,
                            "balance_due": round_currency(bal),
                        }
                    )
            return results
        finally:
            conn.close()

    def get_collection_summary(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        conn = self._get_connection()
        try:
            query = "SELECT * FROM payments WHERE 1=1"
            params: List[Any] = []
            if start_date:
                query += " AND payment_date >= ?"
                params.append(start_date)
            if end_date:
                query += " AND payment_date <= ?"
                params.append(end_date)
            query += " ORDER BY payment_date DESC"

            rows = conn.execute(query, params).fetchall()
            total = Decimal("0.00")
            by_method: Dict[str, Decimal] = {}

            records = []
            for r in rows:
                amt = Decimal(r["amount"])
                total += amt
                m = r["payment_method"]
                by_method[m] = by_method.get(m, Decimal("0.00")) + amt
                records.append(
                    {
                        "payment_ref": r["payment_ref"],
                        "invoice_id": r["invoice_id"],
                        "amount": amt,
                        "payment_method": r["payment_method"],
                        "transaction_id": r["transaction_id"],
                        "payment_date": r["payment_date"][:19],
                        "cashier_name": r["cashier_name"],
                    }
                )

            return {
                "total_collected": total,
                "by_method": by_method,
                "payments_count": len(records),
                "records": records,
            }
        finally:
            conn.close()

    def get_student_statement(self, student_id: str) -> Dict[str, Any]:
        """Returns full financial ledger for a student (invoices + payments)."""
        student = self.get_student(student_id)
        if not student:
            raise ValueError(f"Student {student_id} not found.")

        invoices = self.list_invoices(student_id=student_id)
        inv_ids = [inv.id for inv in invoices if inv.id]

        conn = self._get_connection()
        payments = []
        try:
            if inv_ids:
                placeholders = ",".join("?" for _ in inv_ids)
                p_rows = conn.execute(
                    f"SELECT * FROM payments WHERE invoice_id IN ({placeholders}) ORDER BY payment_date ASC",
                    inv_ids,
                ).fetchall()
                for pr in p_rows:
                    payments.append(
                        {
                            "payment_ref": pr["payment_ref"],
                            "invoice_id": pr["invoice_id"],
                            "amount": Decimal(pr["amount"]),
                            "payment_method": pr["payment_method"],
                            "date": pr["payment_date"],
                        }
                    )
        finally:
            conn.close()

        total_invoiced = sum((i.total_payable for i in invoices), Decimal("0.00"))
        total_paid = sum((i.paid_amount for i in invoices), Decimal("0.00"))
        balance = total_invoiced - total_paid

        return {
            "student": student,
            "total_invoiced": total_invoiced,
            "total_paid": total_paid,
            "balance": balance,
            "invoices": invoices,
            "payments": payments,
        }

    def export_defaulters_csv(self) -> str:
        report = self.get_defaulters_report()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            ["Invoice #", "Student ID", "Student Name", "Class", "Parent Name", "Parent Phone", "Due Date", "Days Overdue", "Balance Due ($)"]
        )
        for r in report:
            writer.writerow(
                [
                    r["invoice_number"],
                    r["student_id"],
                    r["student_name"],
                    r["class_name"],
                    r["parent_name"],
                    r["parent_phone"],
                    r["due_date"],
                    r["days_overdue"],
                    f"{r['balance_due']:.2f}",
                ]
            )
        return output.getvalue()

    def export_collection_csv(self) -> str:
        summary = self.get_collection_summary()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Payment Ref", "Invoice ID", "Amount ($)", "Method", "Tx ID / Cheque #", "Date & Time", "Cashier"])
        for r in summary["records"]:
            writer.writerow([
                r["payment_ref"],
                r["invoice_id"],
                f"{r['amount']:.2f}",
                r["payment_method"],
                r.get("transaction_id", ""),
                r["payment_date"],
                r["cashier_name"],
            ])
        return output.getvalue()

    def _log_audit(self, conn: sqlite3.Connection, entity_type: str, entity_id: str, action: str, actor: str, details: Dict[str, Any]) -> None:
        conn.execute(
            "INSERT INTO audit_logs (entity_type, entity_id, action, actor, details_json) VALUES (?, ?, ?, ?, ?)",
            (entity_type, str(entity_id), action, actor, json.dumps(details)),
        )
