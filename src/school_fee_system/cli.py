"""
Command Line Interface (CLI) for School Student Fee Management System.
Built with standard library argparse with formatted tabular output.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from decimal import Decimal
from typing import List, Optional

from school_fee_system.database import connect_db, initialize_schema, seed_sample_data, get_db_path
from school_fee_system.models import Student, StudentStatus, FeeTerm, InvoiceStatus, PaymentMethod
from school_fee_system.receipt_generator import ReceiptFormatter
from school_fee_system.services import SchoolFeeService


def print_table(headers: List[str], rows: List[List[str]]) -> None:
    """Utility to render cleanly padded ASCII tables in the terminal."""
    if not rows:
        print("(No records found)")
        return

    col_widths = [len(h) for h in headers]
    for row in rows:
        for idx, cell in enumerate(row):
            col_widths[idx] = max(col_widths[idx], len(str(cell)))

    # Header
    sep = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"
    header_line = "| " + " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers)) + " |"
    print(sep)
    print(header_line)
    print(sep)

    # Rows
    for row in rows:
        line = "| " + " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)) + " |"
        print(line)
    print(sep)


def handle_init_db(args: argparse.Namespace) -> None:
    db_path = get_db_path(args.db)
    conn = connect_db(db_path)
    try:
        initialize_schema(conn)
        if args.seed:
            seed_sample_data(conn)
            print(f"✓ Database initialized and seeded with sample data at: {db_path}")
        else:
            print(f"✓ Database initialized with clean schema at: {db_path}")
    finally:
        conn.close()


def handle_students(args: argparse.Namespace, service: SchoolFeeService) -> None:
    sub = args.student_cmd
    if sub == "list":
        students = service.list_students(class_id=args.class_id, search=args.search)
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
        headers = ["ID", "Name", "Class", "Parent", "Phone", "Transport", "Hostel", "Status"]
        print_table(headers, rows)

    elif sub == "add":
        new_stu = Student(
            student_id=args.id,
            first_name=args.first,
            last_name=args.last,
            class_id=args.class_id,
            parent_name=args.parent_name,
            parent_email=args.email,
            parent_phone=args.phone,
            is_transport_enrolled=args.transport,
            is_hostel_enrolled=args.hostel,
            status=StudentStatus.ACTIVE,
        )
        service.add_student(new_stu)
        print(f"✓ Enrolled student {new_stu.full_name} ({new_stu.student_id}) successfully.")

    elif sub == "statement":
        stmt = service.get_student_statement(args.id)
        s: Student = stmt["student"]
        print("\n" + "=" * 60)
        print(f"  ACCOUNT STATEMENT: {s.full_name} ({s.student_id})")
        print(f"  Class: {s.class_name} | Contact: {s.parent_phone}")
        print("=" * 60)
        print(f"  Total Invoiced : ₹{stmt['total_invoiced']:.2f}")
        print(f"  Total Paid     : ₹{stmt['total_paid']:.2f}")
        print(f"  Balance Due    : ₹{stmt['balance']:.2f}")
        print("-" * 60)
        print("  INVOICES:")
        inv_rows = [
            [i.invoice_number, i.term.value, str(i.due_date), f"₹{i.total_payable:.2f}", f"₹{i.paid_amount:.2f}", i.status.value]
            for i in stmt["invoices"]
        ]
        print_table(["Invoice #", "Term", "Due Date", "Payable (₹)", "Paid (₹)", "Status"], inv_rows)

        print("\n  PAYMENTS:")
        pay_rows = [
            [p["payment_ref"], p["date"][:10], f"₹{p['amount']:.2f}", p["payment_method"]]
            for p in stmt["payments"]
        ]
        print_table(["Payment Ref", "Date", "Amount (₹)", "Method"], pay_rows)


def handle_fees(args: argparse.Namespace, service: SchoolFeeService) -> None:
    sub = args.fee_cmd
    if sub == "list-heads":
        heads = service.get_fee_heads()
        rows = [[h.code, h.name, "Yes" if h.is_recurring else "No", "Yes" if h.is_optional else "No", h.description] for h in heads]
        print_table(["Code", "Name", "Recurring", "Optional", "Description"], rows)

    elif sub == "list-structures":
        structures = service.list_fee_structures()
        rows = [
            [
                str(st.id),
                st.name,
                st.class_name or str(st.class_id),
                st.academic_year,
                st.term.value,
                f"₹{st.total_base_amount:.2f}",
                ", ".join(f"{it.head_code}: ₹{it.amount:.0f}" for it in st.items),
            ]
            for st in structures
        ]
        print_table(["ID", "Name", "Class", "Year", "Term", "Total Base (₹)", "Components"], rows)

    elif sub == "list-discounts":
        discounts = service.get_discount_policies()
        rows = [
            [
                d.code,
                d.name,
                d.discount_type.value,
                f"{d.value}%" if d.discount_type == DiscountType.PERCENTAGE else f"₹{d.value:.2f}",
                d.applies_to_head_code or "ALL (General)",
                d.description,
            ]
            for d in discounts
        ]
        print_table(["Code", "Policy Name", "Type", "Value", "Target", "Description"], rows)


def handle_invoices(args: argparse.Namespace, service: SchoolFeeService) -> None:
    sub = args.invoice_cmd
    if sub == "generate":
        due_d = date.fromisoformat(args.due_date) if args.due_date else None
        inv = service.generate_student_invoice(
            student_id=args.student_id,
            academic_year=args.year,
            term=FeeTerm(args.term),
            due_date=due_d,
        )
        print(f"✓ Generated Invoice: {inv.invoice_number}")
        print(f"  Student : {inv.student_name} ({inv.student_id})")
        print(f"  Subtotal: ₹{inv.subtotal:.2f} - Discount: ₹{inv.discount_total:.2f} = Total: ₹{inv.total_payable:.2f}")

    elif sub == "batch-generate":
        due_d = date.fromisoformat(args.due_date) if args.due_date else None
        invoices = service.generate_batch_invoices_for_class(
            class_id=args.class_id,
            academic_year=args.year,
            term=FeeTerm(args.term),
            due_date=due_d,
        )
        print(f"✓ Batch generation complete. Successfully issued {len(invoices)} invoices.")

    elif sub == "list":
        st = InvoiceStatus(args.status) if args.status else None
        invoices = service.list_invoices(student_id=args.student_id, status=st, class_id=args.class_id)
        rows = [
            [
                i.invoice_number,
                i.student_name or i.student_id,
                i.class_name or "-",
                i.term.value,
                str(i.due_date),
                f"₹{i.total_payable:.2f}",
                f"₹{i.paid_amount:.2f}",
                f"₹{i.balance_amount:.2f}",
                i.status.value,
            ]
            for i in invoices
        ]
        print_table(["Invoice #", "Student", "Class", "Term", "Due Date", "Total (₹)", "Paid (₹)", "Balance (₹)", "Status"], rows)

    elif sub == "view":
        inv = service.get_invoice(args.id)
        if not inv:
            print(f"Invoice '{args.id}' not found.")
            return

        print("\n" + "=" * 55)
        print(f"  INVOICE: {inv.invoice_number}")
        print("=" * 55)
        print(f"  Student       : {inv.student_name} ({inv.student_id})")
        print(f"  Class         : {inv.class_name}")
        print(f"  Academic Term : {inv.academic_year} [{inv.term.value}]")
        print(f"  Issue Date    : {inv.issue_date} | Due Date: {inv.due_date}")
        print(f"  Status        : {inv.status.value}")
        print("-" * 55)
        print("  FEE BREAKDOWN:")
        item_rows = [
            [it.head_name, f"₹{it.amount:.2f}", f"₹{it.discount_amount:.2f}", f"₹{it.net_amount:.2f}"]
            for it in inv.items
        ]
        print_table(["Head", "Amount (₹)", "Discount (₹)", "Net Amount (₹)"], item_rows)
        print(f"  Subtotal      : ₹{inv.subtotal:.2f}")
        print(f"  Discounts     : -₹{inv.discount_total:.2f}")
        print(f"  Late Penalty  : +₹{inv.late_fee:.2f}")
        print(f"  TOTAL PAYABLE : ₹{inv.total_payable:.2f}")
        print(f"  Amount Settled: ₹{inv.paid_amount:.2f}")
        print(f"  BALANCE DUE   : ₹{inv.balance_amount:.2f}")
        print("=" * 55)


def handle_payments(args: argparse.Namespace, service: SchoolFeeService) -> None:
    sub = args.payment_cmd
    if sub == "record":
        pay, rec = service.record_payment(
            invoice_id=args.invoice_id,
            amount=Decimal(str(args.amount)),
            payment_method=PaymentMethod(args.method),
            transaction_id=args.tx_id or "COUNTER-CASH",
            cashier_name=args.cashier or "Admin",
            notes=args.notes or "",
        )
        print("✓ Payment registered successfully!")
        print(f"  Payment Ref : {pay.payment_ref}")
        print(f"  Receipt No  : {rec.receipt_number}")
        print(f"  Audit Hash  : {rec.receipt_hash[:32]}...")
        print("\n" + ReceiptFormatter.format_text(rec))


def handle_receipts(args: argparse.Namespace, service: SchoolFeeService) -> None:
    sub = args.receipt_cmd
    if sub == "view":
        rec = service.get_receipt(args.number)
        if not rec:
            print(f"Receipt '{args.number}' not found.")
            return

        if args.html:
            with open(args.html, "w", encoding="utf-8") as f:
                f.write(ReceiptFormatter.format_html(rec))
            print(f"✓ Saved printable HTML receipt to: {args.html}")
        else:
            print(ReceiptFormatter.format_text(rec))

    elif sub == "verify":
        is_valid, msg = service.verify_receipt(args.number)
        if is_valid:
            print(f"✓ {msg}")
        else:
            print(f"✗ {msg}", file=sys.stderr)


def handle_defaulters(args: argparse.Namespace, service: SchoolFeeService) -> None:
    reports = service.get_defaulters_report(min_days_overdue=args.min_days, class_id=args.class_id)
    if args.export:
        csv_content = service.export_defaulters_csv()
        with open(args.export, "w", encoding="utf-8") as f:
            f.write(csv_content)
        print(f"✓ Exported {len(reports)} defaulters to: {args.export}")
        return

    rows = [
        [
            r["invoice_number"],
            r["student_name"],
            r["class_name"],
            r["parent_phone"],
            r["due_date"],
            f"{r['days_overdue']} days",
            f"₹{r['balance_due']:.2f}",
        ]
        for r in reports
    ]
    print(f"\nDEFALUTERS LIST (Overdue Invoices: {len(reports)})")
    print_table(["Invoice #", "Student", "Class", "Parent Phone", "Due Date", "Overdue By", "Balance Due (₹)"], rows)


def handle_reports(args: argparse.Namespace, service: SchoolFeeService) -> None:
    sub = args.report_cmd
    if sub == "collection":
        if args.export:
            csv_content = service.export_collection_csv()
            with open(args.export, "w", encoding="utf-8") as f:
                f.write(csv_content)
            print(f"✓ Exported collections to: {args.export}")
            return

        summary = service.get_collection_summary(start_date=args.start, end_date=args.end)
        print("\n" + "=" * 55)
        print("          FINANCIAL COLLECTION SUMMARY")
        print("=" * 55)
        print(f"  Total Collected: ₹{summary['total_collected']:.2f}")
        print(f"  Total Receipts : {summary['payments_count']}")
        print("-" * 55)
        print("  COLLECTION BY PAYMENT METHOD:")
        for method, amt in summary["by_method"].items():
            print(f"    • {method:<15}: ₹{amt:.2f}")
        print("-" * 55)


def handle_serve(args: argparse.Namespace, service: SchoolFeeService) -> None:
    from school_fee_system.server import run_server
    run_server(host=args.host, port=args.port, db_path=service.db_path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="school-fee-system",
        description="School Student Fee Management System — Complete Billing & Accounting Suite",
    )
    parser.add_argument("--db", default=None, help="Custom SQLite database file path")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. init-db
    p_init = subparsers.add_parser("init-db", help="Initialize schema and optional demo seed data")
    p_init.add_argument("--seed", action="store_true", help="Pre-load demo classes, fee heads, and students")

    # 2. students
    p_stu = subparsers.add_parser("students", help="Student profile management")
    stu_sub = p_stu.add_subparsers(dest="student_cmd", required=True)
    
    p_stu_list = stu_sub.add_parser("list", help="List enrolled students")
    p_stu_list.add_argument("--class-id", type=int, help="Filter by class ID")
    p_stu_list.add_argument("--search", help="Search name or ID")

    p_stu_add = stu_sub.add_parser("add", help="Enroll a new student")
    p_stu_add.add_argument("--id", required=True, help="Student admission ID (e.g. STU-2026-010)")
    p_stu_add.add_argument("--first", required=True, help="First name")
    p_stu_add.add_argument("--last", required=True, help="Last name")
    p_stu_add.add_argument("--class-id", type=int, required=True, help="Class ID")
    p_stu_add.add_argument("--parent-name", required=True, help="Parent/Guardian name")
    p_stu_add.add_argument("--email", required=True, help="Parent email")
    p_stu_add.add_argument("--phone", required=True, help="Parent phone")
    p_stu_add.add_argument("--transport", action="store_true", help="Opt in for school bus transport")
    p_stu_add.add_argument("--hostel", action="store_true", help="Opt in for school boarding/hostel")

    p_stu_stmt = stu_sub.add_parser("statement", help="Print student account statement & ledger")
    p_stu_stmt.add_argument("--id", required=True, help="Student ID")

    # 3. fees
    p_fee = subparsers.add_parser("fees", help="Fee heads, structures, and discounts")
    fee_sub = p_fee.add_subparsers(dest="fee_cmd", required=True)
    fee_sub.add_parser("list-heads", help="List available fee components/heads")
    fee_sub.add_parser("list-structures", help="List fee structures configured for classes")
    fee_sub.add_parser("list-discounts", help="List discount policies (merit, sibling, etc.)")

    # 4. invoices
    p_inv = subparsers.add_parser("invoices", help="Invoice generation and lookup")
    inv_sub = p_inv.add_subparsers(dest="invoice_cmd", required=True)
    
    p_inv_gen = inv_sub.add_parser("generate", help="Generate an invoice for a single student")
    p_inv_gen.add_argument("--student-id", required=True)
    p_inv_gen.add_argument("--year", default="2026-2027", help="Academic year (default: 2026-2027)")
    p_inv_gen.add_argument("--term", choices=[t.value for t in FeeTerm], default="TERM_1")
    p_inv_gen.add_argument("--due-date", help="Due date (YYYY-MM-DD)")

    p_inv_batch = inv_sub.add_parser("batch-generate", help="Batch generate invoices for a class")
    p_inv_batch.add_argument("--class-id", type=int, required=True)
    p_inv_batch.add_argument("--year", default="2026-2027")
    p_inv_batch.add_argument("--term", choices=[t.value for t in FeeTerm], default="TERM_1")
    p_inv_batch.add_argument("--due-date", help="Due date (YYYY-MM-DD)")

    p_inv_list = inv_sub.add_parser("list", help="List invoices")
    p_inv_list.add_argument("--student-id")
    p_inv_list.add_argument("--status", choices=[s.value for s in InvoiceStatus])
    p_inv_list.add_argument("--class-id", type=int)

    p_inv_view = inv_sub.add_parser("view", help="View full invoice details")
    p_inv_view.add_argument("--id", required=True, help="Invoice ID or Number")

    # 5. payments
    p_pay = subparsers.add_parser("payments", help="Record and inspect fee collections")
    pay_sub = p_pay.add_subparsers(dest="payment_cmd", required=True)
    p_pay_rec = pay_sub.add_parser("record", help="Record fee payment against an invoice")
    p_pay_rec.add_argument("--invoice-id", type=int, required=True)
    p_pay_rec.add_argument("--amount", type=float, required=True)
    p_pay_rec.add_argument("--method", choices=[m.value for m in PaymentMethod], default="CASH")
    p_pay_rec.add_argument("--tx-id", default="COUNTER-CASH")
    p_pay_rec.add_argument("--cashier", default="Admin")
    p_pay_rec.add_argument("--notes", default="")

    # 6. receipts
    p_rec = subparsers.add_parser("receipts", help="Receipt lookup and cryptographic verification")
    rec_sub = p_rec.add_subparsers(dest="receipt_cmd", required=True)
    p_rec_view = rec_sub.add_parser("view", help="View receipt")
    p_rec_view.add_argument("--number", required=True, help="Receipt number (e.g. REC-2026-0001)")
    p_rec_view.add_argument("--html", help="Save to HTML file path for printing")

    p_rec_ver = rec_sub.add_parser("verify", help="Cryptographically verify a receipt")
    p_rec_ver.add_argument("--number", required=True)

    # 7. defaulters
    p_def = subparsers.add_parser("defaulters", help="List students with overdue balances")
    p_def.add_argument("--min-days", type=int, default=0, help="Minimum days overdue")
    p_def.add_argument("--class-id", type=int, help="Filter by class")
    p_def.add_argument("--export", help="Export to CSV file path")

    # 8. reports
    p_rep = subparsers.add_parser("reports", help="Financial accounting reports")
    rep_sub = p_rep.add_subparsers(dest="report_cmd", required=True)
    p_rep_col = rep_sub.add_parser("collection", help="Collection report summary")
    p_rep_col.add_argument("--start", help="Start date (YYYY-MM-DD)")
    p_rep_col.add_argument("--end", help="End date (YYYY-MM-DD)")
    p_rep_col.add_argument("--export", help="Export to CSV file path")

    # 9. serve
    p_srv = subparsers.add_parser("serve", help="Launch integrated Web Dashboard & REST API server")
    p_srv.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", 8000)),
        help="Port to listen on (default: 8000 or $PORT env)",
    )
    p_srv.add_argument(
        "--host",
        default=os.environ.get("HOST", "127.0.0.1"),
        help="Host address (default: 127.0.0.1 or $HOST env)",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    service = SchoolFeeService(db_path=args.db)

    try:
        if args.command == "init-db":
            handle_init_db(args)
        elif args.command == "students":
            handle_students(args, service)
        elif args.command == "fees":
            handle_fees(args, service)
        elif args.command == "invoices":
            handle_invoices(args, service)
        elif args.command == "payments":
            handle_payments(args, service)
        elif args.command == "receipts":
            handle_receipts(args, service)
        elif args.command == "defaulters":
            handle_defaulters(args, service)
        elif args.command == "reports":
            handle_reports(args, service)
        elif args.command == "serve":
            handle_serve(args, service)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
