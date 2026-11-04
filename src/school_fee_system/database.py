"""
Database initialization, schema management, and connection utilities for SQLite.
Supports ACID transactions, WAL mode, foreign keys, and pre-populated seed data.
"""

from __future__ import annotations

import os
import shutil
import sqlite3
from contextlib import contextmanager
from decimal import Decimal
from typing import Generator, Optional


DEFAULT_DB_PATH = os.path.expanduser("~/.local/share/school_fee_system/fees.db")


def get_db_path(custom_path: Optional[str] = None) -> str:
    path = custom_path or os.environ.get("SCHOOL_FEE_DB_PATH")
    if not path:
        # If project-level data/fees.db exists or demo db is available, prioritize it
        project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        project_db = os.path.join(project_dir, "data", "fees.db")
        demo_db = os.path.join(project_dir, "dummy_data", "delhi_public_academy_demo.db")

        if not os.path.exists(project_db) and os.path.exists(demo_db):
            try:
                os.makedirs(os.path.dirname(project_db), exist_ok=True)
                shutil.copyfile(demo_db, project_db)
            except (OSError, PermissionError):
                return demo_db

        if os.path.exists(project_db):
            return project_db

        candidate = DEFAULT_DB_PATH
        try:
            os.makedirs(os.path.dirname(os.path.abspath(candidate)), exist_ok=True)
            # Test write ability
            test_file = os.path.join(os.path.dirname(os.path.abspath(candidate)), ".write_test")
            with open(test_file, "w") as f:
                f.write("ok")
            os.remove(test_file)
            path = candidate
        except (OSError, PermissionError):
            # Fallback to project-level data directory
            path = project_db
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    else:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    return path


def connect_db(db_path: Optional[str] = None) -> sqlite3.Connection:
    target_path = get_db_path(db_path)
    conn = sqlite3.connect(target_path, timeout=15.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn


@contextmanager
def get_db_cursor(db_path: Optional[str] = None) -> Generator[sqlite3.Cursor, None, None]:
    conn = connect_db(db_path)
    try:
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def initialize_schema(conn: sqlite3.Connection) -> None:
    """Creates tables, foreign keys, and indexes if they do not already exist."""
    schema_sql = """
    CREATE TABLE IF NOT EXISTS classes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        grade_level INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS students (
        student_id TEXT PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        class_id INTEGER NOT NULL REFERENCES classes(id) ON DELETE RESTRICT,
        parent_name TEXT NOT NULL,
        parent_email TEXT NOT NULL,
        parent_phone TEXT NOT NULL,
        is_transport_enrolled INTEGER NOT NULL DEFAULT 0,
        is_hostel_enrolled INTEGER NOT NULL DEFAULT 0,
        status TEXT NOT NULL DEFAULT 'ACTIVE',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS fee_heads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        code TEXT NOT NULL UNIQUE,
        description TEXT DEFAULT '',
        is_recurring INTEGER NOT NULL DEFAULT 1,
        is_optional INTEGER NOT NULL DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS fee_structures (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        class_id INTEGER NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
        academic_year TEXT NOT NULL,
        term TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(class_id, academic_year, term)
    );

    CREATE TABLE IF NOT EXISTS fee_structure_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fee_structure_id INTEGER NOT NULL REFERENCES fee_structures(id) ON DELETE CASCADE,
        fee_head_id INTEGER NOT NULL REFERENCES fee_heads(id) ON DELETE RESTRICT,
        amount TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS discount_policies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        code TEXT NOT NULL UNIQUE,
        discount_type TEXT NOT NULL,
        value TEXT NOT NULL,
        applies_to_head_code TEXT,
        description TEXT DEFAULT ''
    );

    CREATE TABLE IF NOT EXISTS student_discounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
        discount_policy_id INTEGER NOT NULL REFERENCES discount_policies(id) ON DELETE CASCADE,
        academic_year TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(student_id, discount_policy_id, academic_year)
    );

    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_number TEXT NOT NULL UNIQUE,
        student_id TEXT NOT NULL REFERENCES students(student_id) ON DELETE RESTRICT,
        academic_year TEXT NOT NULL,
        term TEXT NOT NULL,
        issue_date TEXT NOT NULL,
        due_date TEXT NOT NULL,
        subtotal TEXT NOT NULL,
        discount_total TEXT NOT NULL DEFAULT '0.00',
        late_fee TEXT NOT NULL DEFAULT '0.00',
        total_payable TEXT NOT NULL,
        paid_amount TEXT NOT NULL DEFAULT '0.00',
        status TEXT NOT NULL DEFAULT 'UNPAID',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS invoice_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id INTEGER NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
        fee_head_id INTEGER NOT NULL REFERENCES fee_heads(id),
        head_name TEXT NOT NULL,
        head_code TEXT NOT NULL,
        amount TEXT NOT NULL,
        discount_amount TEXT NOT NULL DEFAULT '0.00',
        net_amount TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        payment_ref TEXT NOT NULL UNIQUE,
        invoice_id INTEGER NOT NULL REFERENCES invoices(id) ON DELETE RESTRICT,
        amount TEXT NOT NULL,
        payment_method TEXT NOT NULL,
        transaction_id TEXT NOT NULL,
        payment_date TIMESTAMP NOT NULL,
        cashier_name TEXT NOT NULL,
        notes TEXT DEFAULT ''
    );

    CREATE TABLE IF NOT EXISTS receipts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        receipt_number TEXT NOT NULL UNIQUE,
        payment_id INTEGER NOT NULL REFERENCES payments(id) ON DELETE RESTRICT,
        receipt_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_type TEXT NOT NULL,
        entity_id TEXT NOT NULL,
        action TEXT NOT NULL,
        actor TEXT NOT NULL,
        details_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_students_class ON students(class_id);
    CREATE INDEX IF NOT EXISTS idx_invoices_student ON invoices(student_id);
    CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);
    CREATE INDEX IF NOT EXISTS idx_payments_invoice ON payments(invoice_id);
    CREATE INDEX IF NOT EXISTS idx_receipts_payment ON receipts(payment_id);
    """
    with conn:
        conn.executescript(schema_sql)


def seed_sample_data(conn: sqlite3.Connection) -> None:
    """Populates realistic seed data for immediate demonstration and testing."""
    initialize_schema(conn)

    cur = conn.cursor()
    # Check if data already exists
    cur.execute("SELECT COUNT(*) FROM classes")
    if cur.fetchone()[0] > 0:
        return

    with conn:
        # 1. Classes
        classes = [
            ("Class 9-A", 9),
            ("Class 9-B", 9),
            ("Class 10-A", 10),
            ("Class 10-B", 10),
            ("Class 11-Science", 11),
            ("Class 12-Commerce", 12),
        ]
        cur.executemany("INSERT INTO classes (name, grade_level) VALUES (?, ?)", classes)

        # 2. Fee Heads (CBSE/Indian School Curriculum)
        fee_heads = [
            ("Tuition Fee", "TUITION", "Core academic instruction fee", 1, 0),
            ("Computer & Smart Class Fee", "LAB", "Computer laboratory, AI lab & smart board fee", 1, 0),
            ("Library & Learning Resources", "LIBRARY", "Library access and digital learning materials", 1, 0),
            ("Sports & Co-Curricular", "SPORTS", "Athletic training, PT and sports equipment", 1, 0),
            ("School Bus Transport", "TRANSPORT", "Optional route-based school bus service", 1, 1),
            ("Hostel & Mess Boarding", "HOSTEL", "Optional boarding, lodging and meal plan", 1, 1),
            ("Admission & Registration", "ADMISSION", "One-time new student registration charges", 0, 0),
        ]
        cur.executemany(
            "INSERT INTO fee_heads (name, code, description, is_recurring, is_optional) VALUES (?, ?, ?, ?, ?)",
            fee_heads
        )

        # 3. Discount Policies
        discounts = [
            ("Merit Scholarship 25%", "MERIT_25", "PERCENTAGE", "25.00", "TUITION", "Top academic percentile discount on Tuition"),
            ("Merit Scholarship 50%", "MERIT_50", "PERCENTAGE", "50.00", "TUITION", "Board examination topper scholarship"),
            ("Sibling Concession (₹1,500)", "SIBLING_FLAT", "FIXED", "1500.00", None, "Concession for younger siblings studying in the school"),
            ("Staff Ward Benefit 50%", "STAFF_50", "PERCENTAGE", "50.00", "TUITION", "Fee concession for children of school teachers & staff"),
            ("RTE / EWS Fee Waiver", "RTE_WAIVER", "PERCENTAGE", "100.00", "TUITION", "Right to Education Act 25% reserved quota fee waiver"),
        ]
        cur.executemany(
            "INSERT INTO discount_policies (name, code, discount_type, value, applies_to_head_code, description) VALUES (?, ?, ?, ?, ?, ?)",
            discounts
        )

        # Fetch IDs for fee heads
        head_map = {row["code"]: row["id"] for row in cur.execute("SELECT id, code FROM fee_heads").fetchall()}
        class_map = {row["name"]: row["id"] for row in cur.execute("SELECT id, name FROM classes").fetchall()}

        # 4. Standard Fee Structures (Class 10-A & Class 9-A)
        # Session 2026-2027 Quarter-1 (Apr - Jun) / Term 1
        cur.execute(
            "INSERT INTO fee_structures (name, class_id, academic_year, term) VALUES (?, ?, ?, ?)",
            ("Class 10-A Term-1 (Apr-Sep 2026)", class_map["Class 10-A"], "2026-2027", "TERM_1")
        )
        struct_id_10 = cur.lastrowid
        structure_items_10 = [
            (struct_id_10, head_map["TUITION"], "12000.00"),
            (struct_id_10, head_map["LAB"], "2500.00"),
            (struct_id_10, head_map["LIBRARY"], "1000.00"),
            (struct_id_10, head_map["SPORTS"], "800.00"),
            (struct_id_10, head_map["TRANSPORT"], "3500.00"),
            (struct_id_10, head_map["HOSTEL"], "18000.00"),
        ]
        cur.executemany(
            "INSERT INTO fee_structure_items (fee_structure_id, fee_head_id, amount) VALUES (?, ?, ?)",
            structure_items_10
        )

        cur.execute(
            "INSERT INTO fee_structures (name, class_id, academic_year, term) VALUES (?, ?, ?, ?)",
            ("Class 9-A Term-1 (Apr-Sep 2026)", class_map["Class 9-A"], "2026-2027", "TERM_1")
        )
        struct_id_9 = cur.lastrowid
        structure_items_9 = [
            (struct_id_9, head_map["TUITION"], "10000.00"),
            (struct_id_9, head_map["LAB"], "2000.00"),
            (struct_id_9, head_map["LIBRARY"], "1000.00"),
            (struct_id_9, head_map["SPORTS"], "800.00"),
            (struct_id_9, head_map["TRANSPORT"], "3500.00"),
            (struct_id_9, head_map["HOSTEL"], "18000.00"),
        ]
        cur.executemany(
            "INSERT INTO fee_structure_items (fee_structure_id, fee_head_id, amount) VALUES (?, ?, ?)",
            structure_items_9
        )

        # 5. Sample Students (Indian Names and Contact)
        students = [
            ("STU-2026-001", "Aarav", "Sharma", class_map["Class 10-A"], "Rajesh Sharma", "rajesh.sharma@example.com", "+91 98110 12345", 1, 0, "ACTIVE"),
            ("STU-2026-002", "Priya", "Patel", class_map["Class 10-A"], "Sunita Patel", "sunita.patel@example.com", "+91 98220 23456", 0, 0, "ACTIVE"),
            ("STU-2026-003", "Rohan", "Verma", class_map["Class 10-A"], "Anil Verma", "anil.verma@example.com", "+91 98330 34567", 1, 1, "ACTIVE"),
            ("STU-2026-004", "Ananya", "Iyer", class_map["Class 9-A"], "S. K. Iyer", "sk.iyer@example.com", "+91 98440 45678", 0, 0, "ACTIVE"),
            ("STU-2026-005", "Kabir", "Singh", class_map["Class 9-A"], "Gurpreet Singh", "gurpreet.singh@example.com", "+91 98550 56789", 1, 0, "ACTIVE"),
        ]
        cur.executemany(
            """INSERT INTO students 
            (student_id, first_name, last_name, class_id, parent_name, parent_email, parent_phone, is_transport_enrolled, is_hostel_enrolled, status) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            students
        )

        # 6. Assign Discounts
        disc_map = {row["code"]: row["id"] for row in cur.execute("SELECT id, code FROM discount_policies").fetchall()}
        # Aarav gets 25% merit scholarship on Tuition
        cur.execute(
            "INSERT INTO student_discounts (student_id, discount_policy_id, academic_year) VALUES (?, ?, ?)",
            ("STU-2026-001", disc_map["MERIT_25"], "2026-2027")
        )
        # Ananya gets Sibling concession (₹1,500)
        cur.execute(
            "INSERT INTO student_discounts (student_id, discount_policy_id, academic_year) VALUES (?, ?, ?)",
            ("STU-2026-004", disc_map["SIBLING_FLAT"], "2026-2027")
        )
