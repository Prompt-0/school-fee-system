"""
Comprehensive Indian School Dummy Data Generator for Delhi Public Academy.
Populates realistic students, classes, CBSE fee structures, discounts,
quarterly invoices, UPI/NEFT/Cheque/Cash payment transactions, and audit receipts.
"""

from __future__ import annotations

import json
import os
import shutil
import sqlite3
from datetime import date, timedelta
from decimal import Decimal

from school_fee_system.database import initialize_schema
from school_fee_system.models import FeeTerm, PaymentMethod
from school_fee_system.services import SchoolFeeService


CLASSES_DATA = [
    ("Class 1-A", 1),
    ("Class 1-B", 1),
    ("Class 5-A", 5),
    ("Class 5-B", 5),
    ("Class 8-A", 8),
    ("Class 9-A", 9),
    ("Class 9-B", 9),
    ("Class 10-A", 10),
    ("Class 10-B", 10),
    ("Class 11-Science", 11),
    ("Class 11-Commerce", 11),
    ("Class 12-Science", 12),
]

FEE_HEADS_DATA = [
    ("Tuition Fee", "TUITION", "Core academic instruction & curriculum fee", 1, 0),
    ("Computer & Smart Class Fee", "LAB", "Computer, AI lab and interactive smartboard fee", 1, 0),
    ("Annual Development Fund", "ANNUAL_DEV", "School infrastructure and development fund", 1, 0),
    ("Science Composite Lab Fee", "SCIENCE_LAB", "Physics, Chemistry and Biology laboratory charges", 1, 0),
    ("Library & Digital Content", "LIBRARY", "Library access and digital learning subscription", 1, 0),
    ("Sports & Co-Curricular", "SPORTS", "Athletic coaching, sports equipment & yoga", 1, 0),
    ("School Bus Transport Fee", "TRANSPORT", "Route-wise GPS tracked bus transportation", 1, 1),
    ("Hostel & Mess Boarding", "HOSTEL", "Boarding accommodation, meals and laundry", 1, 1),
    ("Examination & Assessment", "EXAM", "Term assessment, printing and CBSE board papers", 1, 0),
    ("Admission Registration", "ADMISSION", "One-time registration fee for new admissions", 0, 0),
]

DISCOUNTS_DATA = [
    ("Merit Scholarship 25%", "MERIT_25", "PERCENTAGE", "25.00", "TUITION", "Top 5% percentile in academic assessments"),
    ("Merit Scholarship 50%", "MERIT_50", "PERCENTAGE", "50.00", "TUITION", "Board examination and Olympiad rank holders"),
    ("Sibling Concession (₹1,500)", "SIBLING_FLAT", "FIXED", "1500.00", None, "Concession for younger siblings in school"),
    ("Staff Ward Concession 50%", "STAFF_50", "PERCENTAGE", "50.00", "TUITION", "Tuition waiver for faculty and school staff children"),
    ("RTE / EWS Fee Waiver 100%", "RTE_100", "PERCENTAGE", "100.00", "TUITION", "Right to Education Act 25% reserved quota waiver"),
    ("Sports Quota Concession 30%", "SPORTS_30", "PERCENTAGE", "30.00", "TUITION", "State/National level athlete scholarship"),
]

# 45 Realistic Indian Students across grades
STUDENTS_DATA = [
    # Class 10-A
    ("ADM-2026-001", "Aarav", "Sharma", "Class 10-A", "Rajesh Sharma", "rajesh.sharma@example.com", "+91 98110 12345", True, False, "ACTIVE", "MERIT_25"),
    ("ADM-2026-002", "Priya", "Patel", "Class 10-A", "Sunita Patel", "sunita.patel@example.com", "+91 98220 23456", False, False, "ACTIVE", None),
    ("ADM-2026-003", "Rohan", "Verma", "Class 10-A", "Anil Verma", "anil.verma@example.com", "+91 98330 34567", True, True, "ACTIVE", None),
    ("ADM-2026-004", "Ananya", "Iyer", "Class 10-A", "S. K. Iyer", "sk.iyer@example.com", "+91 98440 45678", False, False, "ACTIVE", "SIBLING_FLAT"),
    ("ADM-2026-005", "Kabir", "Singh", "Class 10-A", "Gurpreet Singh", "gurpreet.s@example.com", "+91 98550 56789", True, False, "ACTIVE", None),
    ("ADM-2026-006", "Diya", "Banerjee", "Class 10-A", "Somnath Banerjee", "somnath.b@example.com", "+91 98660 67890", True, False, "ACTIVE", "MERIT_50"),
    ("ADM-2026-007", "Aditya", "Kulkarni", "Class 10-A", "Prakash Kulkarni", "prakash.k@example.com", "+91 98770 78901", False, False, "ACTIVE", None),

    # Class 10-B
    ("ADM-2026-008", "Sneha", "Reddy", "Class 10-B", "K. V. Reddy", "kv.reddy@example.com", "+91 98112 34567", True, False, "ACTIVE", None),
    ("ADM-2026-009", "Vivaan", "Joshi", "Class 10-B", "Makarand Joshi", "m.joshi@example.com", "+91 98223 45678", False, False, "ACTIVE", "STAFF_50"),
    ("ADM-2026-010", "Ishita", "Deshmukh", "Class 10-B", "Sachin Deshmukh", "sachin.d@example.com", "+91 98334 56789", True, False, "ACTIVE", None),
    ("ADM-2026-011", "Reyansh", "Gupta", "Class 10-B", "Alok Gupta", "alok.gupta@example.com", "+91 98445 67890", False, True, "ACTIVE", None),
    ("ADM-2026-012", "Tanvi", "Nair", "Class 10-B", "Gopikrishnan Nair", "gk.nair@example.com", "+91 98556 78901", True, False, "ACTIVE", "MERIT_25"),

    # Class 9-A
    ("ADM-2026-013", "Aryan", "Choudhury", "Class 9-A", "Pradip Choudhury", "pradip.c@example.com", "+91 98667 89012", True, False, "ACTIVE", None),
    ("ADM-2026-014", "Meera", "Nambiar", "Class 9-A", "Ramesh Nambiar", "ramesh.n@example.com", "+91 98778 90123", False, False, "ACTIVE", "SIBLING_FLAT"),
    ("ADM-2026-015", "Sai", "Pranav", "Class 9-A", "Srinivas Rao", "srinivas.r@example.com", "+91 98889 01234", True, False, "ACTIVE", None),
    ("ADM-2026-016", "Avni", "Malhotra", "Class 9-A", "Deepak Malhotra", "deepak.m@example.com", "+91 98990 12345", False, False, "ACTIVE", None),
    ("ADM-2026-017", "Harshvardhan", "Rathore", "Class 9-A", "Vikram Singh Rathore", "vikram.r@example.com", "+91 98101 23456", True, True, "ACTIVE", "SPORTS_30"),

    # Class 9-B
    ("ADM-2026-018", "Riya", "Sen", "Class 9-B", "Debashis Sen", "debashis.s@example.com", "+91 98212 34567", False, False, "ACTIVE", "RTE_100"),
    ("ADM-2026-019", "Devansh", "Tripathi", "Class 9-B", "Manoj Tripathi", "manoj.t@example.com", "+91 98323 45678", True, False, "ACTIVE", None),
    ("ADM-2026-020", "Khushi", "Agarwal", "Class 9-B", "Pankaj Agarwal", "pankaj.a@example.com", "+91 98434 56789", False, False, "ACTIVE", None),
    ("ADM-2026-021", "Manav", "Khatri", "Class 9-B", "Sanjay Khatri", "sanjay.k@example.com", "+91 98545 67890", True, False, "ACTIVE", None),

    # Class 11-Science
    ("ADM-2026-022", "Kavya", "Menon", "Class 11-Science", "K. R. Menon", "kr.menon@example.com", "+91 98656 78901", True, False, "ACTIVE", "MERIT_50"),
    ("ADM-2026-023", "Arnav", "Ghosh", "Class 11-Science", "Subir Ghosh", "subir.g@example.com", "+91 98767 89012", False, False, "ACTIVE", None),
    ("ADM-2026-024", "Samaira", "Kapoor", "Class 11-Science", "Rohit Kapoor", "rohit.k@example.com", "+91 98878 90123", True, True, "ACTIVE", None),
    ("ADM-2026-025", "Siddharth", "Pillai", "Class 11-Science", "Murugan Pillai", "murugan.p@example.com", "+91 98989 01234", True, False, "ACTIVE", None),
    ("ADM-2026-026", "Tara", "Bhatia", "Class 11-Science", "Virender Bhatia", "v.bhatia@example.com", "+91 98190 12345", False, False, "ACTIVE", "STAFF_50"),

    # Class 11-Commerce
    ("ADM-2026-027", "Yash", "Chhabra", "Class 11-Commerce", "Rajinder Chhabra", "r.chhabra@example.com", "+91 98201 23456", True, False, "ACTIVE", None),
    ("ADM-2026-028", "Nandini", "Saxena", "Class 11-Commerce", "Arun Saxena", "arun.s@example.com", "+91 98312 34567", False, False, "ACTIVE", None),
    ("ADM-2026-029", "Dhruv", "Singhania", "Class 11-Commerce", "Vijay Singhania", "vijay.s@example.com", "+91 98423 45678", True, False, "ACTIVE", None),

    # Class 12-Science
    ("ADM-2026-030", "Aniket", "Bhardwaj", "Class 12-Science", "Kuldeep Bhardwaj", "k.bhardwaj@example.com", "+91 98534 56789", False, False, "ACTIVE", "MERIT_25"),
    ("ADM-2026-031", "Sanya", "Mirza", "Class 12-Science", "Farhan Mirza", "farhan.m@example.com", "+91 98645 67890", True, False, "ACTIVE", None),
    ("ADM-2026-032", "Pranav", "Hegde", "Class 12-Science", "Venkatesh Hegde", "v.hegde@example.com", "+91 98756 78901", True, True, "ACTIVE", None),

    # Class 8-A
    ("ADM-2026-033", "Aanya", "Pandey", "Class 8-A", "Sudhir Pandey", "sudhir.p@example.com", "+91 98867 89012", True, False, "ACTIVE", "SIBLING_FLAT"),
    ("ADM-2026-034", "Atharva", "Kadam", "Class 8-A", "Nitin Kadam", "nitin.k@example.com", "+91 98978 90123", False, False, "ACTIVE", None),
    ("ADM-2026-035", "Bhavya", "Mishra", "Class 8-A", "Akhilesh Mishra", "akhilesh.m@example.com", "+91 98189 01234", True, False, "ACTIVE", None),

    # Class 5-A & 5-B (Primary)
    ("ADM-2026-036", "Chirag", "Dhar", "Class 5-A", "Anirban Dhar", "anirban.d@example.com", "+91 98290 12345", True, False, "ACTIVE", None),
    ("ADM-2026-037", "Disha", "Goyal", "Class 5-A", "Naresh Goyal", "naresh.g@example.com", "+91 98301 23456", False, False, "ACTIVE", None),
    ("ADM-2026-038", "Eklavya", "Rawat", "Class 5-B", "Surender Rawat", "surender.r@example.com", "+91 98412 34567", True, False, "ACTIVE", None),
    ("ADM-2026-039", "Gauri", "Shukla", "Class 5-B", "Pramod Shukla", "pramod.s@example.com", "+91 98523 45678", False, False, "ACTIVE", "RTE_100"),

    # Class 1-A & 1-B (Foundational)
    ("ADM-2026-040", "Hridyansh", "Bose", "Class 1-A", "Debashree Bose", "debashree.b@example.com", "+91 98634 56789", True, False, "ACTIVE", None),
    ("ADM-2026-041", "Ishani", "Roy", "Class 1-A", "Sourav Roy", "sourav.r@example.com", "+91 98745 67890", False, False, "ACTIVE", None),
    ("ADM-2026-042", "Jayant", "Chauhan", "Class 1-B", "Harpal Chauhan", "harpal.c@example.com", "+91 98856 78901", True, False, "ACTIVE", None),
    ("ADM-2026-043", "Kashvi", "Sethi", "Class 1-B", "Varun Sethi", "varun.s@example.com", "+91 98967 89012", False, False, "ACTIVE", "SIBLING_FLAT"),
]


def generate_database(target_db_path: str) -> None:
    """Creates schema and generates full Indian school dataset."""
    if os.path.exists(target_db_path):
        os.remove(target_db_path)
    os.makedirs(os.path.dirname(os.path.abspath(target_db_path)), exist_ok=True)

    conn = sqlite3.connect(target_db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")

    initialize_schema(conn)

    cur = conn.cursor()
    with conn:
        # 1. Insert Classes
        cur.executemany("INSERT INTO classes (name, grade_level) VALUES (?, ?)", CLASSES_DATA)
        class_map = {row["name"]: row["id"] for row in cur.execute("SELECT id, name FROM classes").fetchall()}

        # 2. Insert Fee Heads
        cur.executemany(
            "INSERT INTO fee_heads (name, code, description, is_recurring, is_optional) VALUES (?, ?, ?, ?, ?)",
            FEE_HEADS_DATA,
        )
        head_map = {row["code"]: row["id"] for row in cur.execute("SELECT id, code FROM fee_heads").fetchall()}

        # 3. Insert Discounts
        cur.executemany(
            "INSERT INTO discount_policies (name, code, discount_type, value, applies_to_head_code, description) VALUES (?, ?, ?, ?, ?, ?)",
            DISCOUNTS_DATA,
        )
        disc_map = {row["code"]: row["id"] for row in cur.execute("SELECT id, code FROM discount_policies").fetchall()}

        # 4. Standard Fee Structures for Classes
        # Grade 9 & 10
        for grade_name in ["Class 10-A", "Class 10-B", "Class 9-A", "Class 9-B"]:
            cid = class_map[grade_name]
            cur.execute(
                "INSERT INTO fee_structures (name, class_id, academic_year, term) VALUES (?, ?, ?, ?)",
                (f"{grade_name} Term-1 (Apr-Sep 2026)", cid, "2026-2027", "TERM_1"),
            )
            fs_id = cur.lastrowid
            items = [
                (fs_id, head_map["TUITION"], "12000.00"),
                (fs_id, head_map["LAB"], "2500.00"),
                (fs_id, head_map["ANNUAL_DEV"], "4000.00"),
                (fs_id, head_map["SCIENCE_LAB"], "1500.00"),
                (fs_id, head_map["LIBRARY"], "1000.00"),
                (fs_id, head_map["SPORTS"], "800.00"),
                (fs_id, head_map["EXAM"], "600.00"),
                (fs_id, head_map["TRANSPORT"], "3500.00"),
                (fs_id, head_map["HOSTEL"], "18000.00"),
            ]
            cur.executemany("INSERT INTO fee_structure_items (fee_structure_id, fee_head_id, amount) VALUES (?, ?, ?)", items)

        # Senior Secondary (Grade 11 & 12)
        for grade_name in ["Class 11-Science", "Class 11-Commerce", "Class 12-Science"]:
            cid = class_map[grade_name]
            cur.execute(
                "INSERT INTO fee_structures (name, class_id, academic_year, term) VALUES (?, ?, ?, ?)",
                (f"{grade_name} Term-1 (Apr-Sep 2026)", cid, "2026-2027", "TERM_1"),
            )
            fs_id = cur.lastrowid
            items = [
                (fs_id, head_map["TUITION"], "15000.00"),
                (fs_id, head_map["LAB"], "3000.00"),
                (fs_id, head_map["ANNUAL_DEV"], "5000.00"),
                (fs_id, head_map["SCIENCE_LAB"], "2000.00"),
                (fs_id, head_map["LIBRARY"], "1200.00"),
                (fs_id, head_map["SPORTS"], "1000.00"),
                (fs_id, head_map["EXAM"], "800.00"),
                (fs_id, head_map["TRANSPORT"], "4000.00"),
                (fs_id, head_map["HOSTEL"], "20000.00"),
            ]
            cur.executemany("INSERT INTO fee_structure_items (fee_structure_id, fee_head_id, amount) VALUES (?, ?, ?)", items)

        # Middle & Primary (Grade 8, 5, 1)
        for grade_name in ["Class 8-A", "Class 5-A", "Class 5-B", "Class 1-A", "Class 1-B"]:
            cid = class_map[grade_name]
            cur.execute(
                "INSERT INTO fee_structures (name, class_id, academic_year, term) VALUES (?, ?, ?, ?)",
                (f"{grade_name} Term-1 (Apr-Sep 2026)", cid, "2026-2027", "TERM_1"),
            )
            fs_id = cur.lastrowid
            items = [
                (fs_id, head_map["TUITION"], "9000.00"),
                (fs_id, head_map["LAB"], "1500.00"),
                (fs_id, head_map["ANNUAL_DEV"], "3000.00"),
                (fs_id, head_map["LIBRARY"], "800.00"),
                (fs_id, head_map["SPORTS"], "600.00"),
                (fs_id, head_map["EXAM"], "500.00"),
                (fs_id, head_map["TRANSPORT"], "3000.00"),
                (fs_id, head_map["HOSTEL"], "16000.00"),
            ]
            cur.executemany("INSERT INTO fee_structure_items (fee_structure_id, fee_head_id, amount) VALUES (?, ?, ?)", items)

        # 5. Insert Students
        for s in STUDENTS_DATA:
            stu_id, first, last, cls_name, parent, email, phone, trans, host, status, disc_code = s
            cid = class_map[cls_name]
            cur.execute(
                """INSERT INTO students 
                (student_id, first_name, last_name, class_id, parent_name, parent_email, parent_phone, is_transport_enrolled, is_hostel_enrolled, status) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (stu_id, first, last, cid, parent, email, phone, 1 if trans else 0, 1 if host else 0, status),
            )
            if disc_code and disc_code in disc_map:
                cur.execute(
                    "INSERT INTO student_discounts (student_id, discount_policy_id, academic_year) VALUES (?, ?, ?)",
                    (stu_id, disc_map[disc_code], "2026-2027"),
                )

    conn.close()

    # Now use SchoolFeeService to issue realistic invoices and payments
    svc = SchoolFeeService(db_path=target_db_path)

    # Invoices & Collections Generation
    payment_samples = [
        # Student ID, Payment amount, Method, UTR / Tx ID, Cashier, Notes
        ("ADM-2026-001", Decimal("15000.00"), PaymentMethod.UPI, "UPI/GPay/202604019921234", "Sunita Verma", "Term-1 advance via Google Pay"),
        ("ADM-2026-002", None, PaymentMethod.NET_BANKING, "HDFC/NEFT/202604058811", "Accounts Office", "Full payment via HDFC NetBanking"),
        ("ADM-2026-003", Decimal("20000.00"), PaymentMethod.CHEQUE_DD, "CHQ-442109-SBI-DELHI", "Rajesh Sharma", "Cheque drawn on SBI Main Branch"),
        ("ADM-2026-005", None, PaymentMethod.UPI, "UPI/PhonePe/2026041044321", "Sunita Verma", "Full Term-1 settlement via PhonePe"),
        ("ADM-2026-006", None, PaymentMethod.CASH, "CASH-COUNTER-044", "Counter Cashier", "Counter cash receipt issued"),
        ("ADM-2026-008", Decimal("12000.00"), PaymentMethod.CARD, "POS/HDFC/998822", "Counter Cashier", "RuPay Debit Card payment at counter"),
        ("ADM-2026-010", None, PaymentMethod.UPI, "UPI/Paytm/202604147761", "Sunita Verma", "Paytm UPI settlement"),
        ("ADM-2026-012", Decimal("10000.00"), PaymentMethod.NET_BANKING, "ICICI/IMPS/20260415332", "Accounts Office", "ICICI IMPS Transfer"),
        ("ADM-2026-013", None, PaymentMethod.CASH, "CASH-COUNTER-098", "Counter Cashier", "Cash deposit at fee window"),
        ("ADM-2026-015", Decimal("8000.00"), PaymentMethod.UPI, "UPI/BHIM/20260416991", "Sunita Verma", "BHIM UPI payment (1st installment)"),
        ("ADM-2026-022", None, PaymentMethod.NET_BANKING, "AXIS/NEFT/20260418554", "Accounts Office", "Axis Bank NEFT wire"),
        ("ADM-2026-024", Decimal("25000.00"), PaymentMethod.CHEQUE_DD, "CHQ-778811-PNB-NOIDA", "Rajesh Sharma", "Boarding & Tuition fees paid by Cheque"),
        ("ADM-2026-027", None, PaymentMethod.CARD, "POS/SBI/334411", "Counter Cashier", "Visa card transaction at POS terminal"),
        ("ADM-2026-030", Decimal("12000.00"), PaymentMethod.UPI, "UPI/GPay/20260420112", "Sunita Verma", "Google Pay transaction"),
        ("ADM-2026-033", None, PaymentMethod.CASH, "CASH-COUNTER-142", "Counter Cashier", "Fee counter collection"),
        ("ADM-2026-036", Decimal("7000.00"), PaymentMethod.UPI, "UPI/PhonePe/20260422998", "Sunita Verma", "PhonePe UPI payment"),
        ("ADM-2026-040", None, PaymentMethod.UPI, "UPI/GPay/20260425667", "Sunita Verma", "Class 1 admission Term 1 paid"),
    ]

    for s in STUDENTS_DATA[:35]:
        stu_id = s[0]
        # Some overdue invoices for defaulters list demo
        is_overdue = stu_id in ["ADM-2026-004", "ADM-2026-007", "ADM-2026-011", "ADM-2026-016", "ADM-2026-023", "ADM-2026-028"]
        if is_overdue:
            due_d = date.today() - timedelta(days=15)
        else:
            due_d = date.today() + timedelta(days=20)

        inv = svc.generate_student_invoice(
            student_id=stu_id,
            academic_year="2026-2027",
            term=FeeTerm.TERM_1,
            due_date=due_d,
        )

    # Process sample payments
    for p_info in payment_samples:
        stu_id, amt, method, tx_id, cashier, notes = p_info
        invoices = svc.list_invoices(student_id=stu_id)
        if invoices:
            target_inv = invoices[0]
            pay_amount = amt if amt is not None else target_inv.balance_amount
            if pay_amount > Decimal("0.00") and pay_amount <= target_inv.balance_amount:
                svc.record_payment(
                    invoice_id=target_inv.id,
                    amount=pay_amount,
                    payment_method=method,
                    transaction_id=tx_id,
                    cashier_name=cashier,
                    notes=notes,
                )

    # Apply late fee assessment on overdue invoices
    svc.assess_and_apply_late_fees()


def export_json_and_sql(db_path: str, output_dir: str) -> None:
    """Exports structured JSON datasets and an SQL dump for documentation."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # 1. Export Students JSON
    students = conn.execute("SELECT s.*, c.name as class_name FROM students s JOIN classes c ON s.class_id = c.id").fetchall()
    students_list = [dict(s) for s in students]
    with open(os.path.join(output_dir, "students.json"), "w", encoding="utf-8") as f:
        json.dump(students_list, f, indent=2)

    # 2. Export Classes JSON
    classes = conn.execute("SELECT * FROM classes").fetchall()
    with open(os.path.join(output_dir, "classes.json"), "w", encoding="utf-8") as f:
        json.dump([dict(c) for c in classes], f, indent=2)

    # 3. Export SQL dump
    with open(os.path.join(output_dir, "seed_data.sql"), "w", encoding="utf-8") as f:
        for line in conn.iterdump():
            f.write(f"{line}\n")

    conn.close()


def main() -> None:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)

    demo_db_path = os.path.join(base_dir, "delhi_public_academy_demo.db")
    live_db_path = os.path.join(project_root, "data", "fees.db")

    print(f"Generating comprehensive Indian School dummy dataset at: {demo_db_path}...")
    generate_database(demo_db_path)

    print("Exporting students.json, classes.json, and seed_data.sql...")
    export_json_and_sql(demo_db_path, base_dir)

    # Copy to live database so running server picks it up immediately
    print(f"Updating active local database at: {live_db_path}...")
    shutil.copyfile(demo_db_path, live_db_path)

    svc = SchoolFeeService(db_path=live_db_path)
    kpis = svc.get_kpis()
    print("\n✓ Dummy Data Population Complete!")
    print(f"  • Total Enrolled Students : {kpis['active_students']}")
    print(f"  • Total Collections (₹)   : ₹{kpis['total_collected']:,.2f}")
    print(f"  • Total Outstanding (₹)   : ₹{kpis['total_outstanding']:,.2f}")
    print(f"  • Overdue Defaulters      : {kpis['defaulters_count']}")


if __name__ == "__main__":
    main()
