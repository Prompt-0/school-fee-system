#!/usr/bin/env python3
"""
Delhi Public Academy — School Fee Management System
Interactive Terminal Application for Students & Administrators.

Usage:
  python main.py                 # Launches interactive menu console
  python main.py [COMMAND]       # Runs specific CLI command
"""

import os
import sys

# Ensure src/ is in python path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from decimal import Decimal
from school_fee_system.database import get_db_path, connect_db, initialize_schema, seed_sample_data
from school_fee_system.models import Student, StudentStatus, PaymentMethod
from school_fee_system.receipt_generator import ReceiptFormatter
from school_fee_system.services import SchoolFeeService
from school_fee_system.cli import print_table


MENU_BANNER = """
\033[38;2;45;212;191m\033[1m================================================================================
🎓 DELHI PUBLIC ACADEMY — SCHOOL FEE MANAGEMENT CONSOLE
================================================================================\033[0m
  \033[1m[1]\033[0m  List All Enrolled Students (43 Pupils)
  \033[1m[2]\033[0m  View Fee Invoices & Balances
  \033[1m[3]\033[0m  Record a Fee Payment (UPI / Cash / NetBanking / Cheque)
  \033[1m[4]\033[0m  View Overdue Defaulters Register
  \033[1m[5]\033[0m  Financial Collection & Revenue Summary
  \033[1m[6]\033[0m  View & Verify Digital Receipt (HMAC-SHA256)
  \033[1m[7]\033[0m  Enroll New Student
  \033[1m[8]\033[0m  Run Automated Test Suite (20 Tests)
  \033[1m[9]\033[0m  Reset Database to Fresh CBSE Demo State
  \033[1m[0]\033[0m  Exit Console
\033[38;2;45;212;191m\033[1m================================================================================\033[0m
"""


def get_service() -> SchoolFeeService:
    default_db = os.path.join(ROOT_DIR, "dummy_data", "delhi_public_academy_demo.db")
    active_db = os.path.join(ROOT_DIR, "data", "fees.db")
    if not os.path.exists(active_db) and os.path.exists(default_db):
        import shutil
        os.makedirs(os.path.dirname(active_db), exist_ok=True)
        shutil.copyfile(default_db, active_db)

    db_path = active_db if os.path.exists(active_db) else default_db
    conn = connect_db(db_path)
    initialize_schema(conn)
    conn.close()
    return SchoolFeeService(db_path)


def interactive_menu():
    print(MENU_BANNER)
    service = get_service()

    while True:
        try:
            choice = input("\033[36m\033[1mDPA-Menu [1-9, 0 to exit]>\033[0m ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting. Goodbye!")
            break

        if not choice:
            continue

        if choice in ("0", "exit", "quit", "q"):
            print("Exiting School Fee Management Console. Goodbye!")
            break

        elif choice == "1":
            print("\n\033[1mENROLLED STUDENTS (DELHI PUBLIC ACADEMY):\033[0m")
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
            print_table(["ID", "Name", "Class", "Parent", "Phone", "Transport", "Hostel", "Status"], rows)

        elif choice == "2":
            print("\n\033[1mFEE INVOICES & BALANCES:\033[0m")
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
            print_table(["ID", "Invoice #", "Student", "Class", "Total", "Paid", "Balance", "Status", "Due Date"], rows)

        elif choice == "3":
            print("\n\033[1mRECORD A FEE PAYMENT:\033[0m")
            try:
                inv_id_input = input("Enter Invoice ID (e.g. 1): ").strip()
                if not inv_id_input.isdigit():
                    print("\033[31mError: Invoice ID must be a number.\033[0m\n")
                    continue
                inv_id = int(inv_id_input)
                amount_str = input("Enter Payment Amount (₹): ").strip()
                amount = Decimal(amount_str)
                method_str = input("Payment Mode [UPI / CASH / NETBANKING / CHEQUE] (default UPI): ").strip().upper() or "UPI"
                tx_ref = input("Transaction Ref / Cheque No (optional): ").strip() or "CLI-MANUAL"

                payment, receipt = service.record_payment(
                    invoice_id=inv_id,
                    amount=amount,
                    payment_method=PaymentMethod(method_str),
                    transaction_id=tx_ref,
                )
                print(f"\n\033[32m\033[1m✓ Payment of ₹{payment.amount:.2f} recorded successfully!\033[0m")
                print(f"Receipt Number: \033[1m{receipt.receipt_number}\033[0m")
                print(f"Cryptographic Hash: \033[36m{receipt.receipt_hash[:24]}...\033[0m\n")
            except Exception as e:
                print(f"\033[31mError recording payment: {e}\033[0m\n")

        elif choice == "4":
            print("\n\033[1mOVERDUE FEE DEFAULTERS:\033[0m")
            defaulters = service.get_defaulters_report()
            if not defaulters:
                print("\033[32m✓ Great news! No overdue fee defaulters at this time.\033[0m\n")
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

        elif choice == "5":
            print("\n\033[1mFINANCIAL COLLECTION REPORT:\033[0m")
            summary = service.get_collection_summary()
            print(f"Total Collected: \033[32m\033[1m₹{summary['total_collected']:,.2f}\033[0m")
            print(f"Receipts Issued: {summary['payments_count']}\n")
            rows = [[k, f"₹{v:,.2f}"] for k, v in summary["by_method"].items()]
            print_table(["Payment Mode", "Total Credited (₹)"], rows)

        elif choice == "6":
            rec_num = input("Enter Receipt Number (e.g. REC-2026-0001): ").strip()
            if not rec_num:
                continue
            is_valid, receipt = service.verify_receipt_authenticity(rec_num)
            if not receipt:
                print(f"\033[31mReceipt {rec_num} not found.\033[0m\n")
            elif is_valid:
                amt_str = f"₹{receipt.payment.amount:,.2f}" if receipt.payment else "₹0.00"
                mode_str = receipt.payment.payment_method.value if receipt.payment else "N/A"
                print(f"\n\033[32m\033[1m✓ VALID CRYPTOGRAPHIC RECEIPT\033[0m")
                print(f"Receipt Number : {receipt.receipt_number}")
                print(f"Amount Paid    : {amt_str}")
                print(f"Payment Mode   : {mode_str}")
                print(f"HMAC Signature : {receipt.receipt_hash}\n")
            else:
                print(f"\n\033[31m\033[1m✗ TAMPER WARNING: Receipt signature does not match database record!\033[0m\n")

        elif choice == "7":
            print("\n\033[1mENROLL NEW STUDENT:\033[0m")
            try:
                sid = input("Admission ID (e.g. ADM-2026-050): ").strip()
                fname = input("First Name: ").strip()
                lname = input("Last Name: ").strip()
                cid = int(input("Class ID (1 to 8): ").strip())
                parent = input("Parent/Guardian Name: ").strip()
                phone = input("Parent Phone: ").strip()
                email = input("Parent Email: ").strip()
                trans = input("Enroll Transport? [y/N]: ").strip().lower() == "y"
                hostel = input("Enroll Hostel? [y/N]: ").strip().lower() == "y"

                new_s = Student(
                    student_id=sid,
                    first_name=fname,
                    last_name=lname,
                    class_id=cid,
                    parent_name=parent,
                    parent_phone=phone,
                    parent_email=email,
                    is_transport_enrolled=trans,
                    is_hostel_enrolled=hostel,
                    status=StudentStatus.ACTIVE,
                )
                service.add_student(new_s)
                print(f"\n\033[32m\033[1m✓ Student {new_s.full_name} enrolled successfully!\033[0m\n")
            except Exception as e:
                print(f"\033[31mError adding student: {e}\033[0m\n")

        elif choice == "8":
            print("\n\033[1mRUNNING AUTOMATED UNIT TESTS:\033[0m")
            import unittest
            loader = unittest.TestLoader()
            suite = loader.discover(os.path.join(ROOT_DIR, "tests"))
            runner = unittest.TextTestRunner(verbosity=2)
            runner.run(suite)

        elif choice == "9":
            demo_db = os.path.join(ROOT_DIR, "dummy_data", "delhi_public_academy_demo.db")
            active_db = os.path.join(ROOT_DIR, "data", "fees.db")
            if os.path.exists(demo_db):
                import shutil
                shutil.copyfile(demo_db, active_db)
                service = get_service()
                print("\033[32m\033[1m✓ Database restored to fresh 43-student CBSE demo state!\033[0m\n")
            else:
                print("\033[31mDemo database file not found.\033[0m\n")

        elif choice.lower() in ("menu", "help", "?"):
            print(MENU_BANNER)

        else:
            print(f"\033[33mUnknown option '{choice}'. Type 1-9 to select, 0 to exit, or 'menu' to show options.\033[0m\n")


def main():
    if len(sys.argv) > 1:
        # Command line arguments passed -> delegate to CLI
        from school_fee_system.cli import main as cli_main
        cli_main()
    else:
        # No arguments -> launch interactive menu
        interactive_menu()


if __name__ == "__main__":
    main()
