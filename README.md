# Delhi Public Academy — School Student Fee Management System (CBSE / Indian Curriculum)

A Python software suite tailored for Indian schools (CBSE / ICSE / State Boards) to configure fee structures, issue quarterly invoices, track partial/full fee collections via UPI, NEFT, Net Banking, and Cash, compute concessions (Merit, Sibling, Staff Ward, RTE/EWS), and produce tamper-evident digital receipts with official CBSE school letterhead and verification stamps.

---

## Indian School Customizations & Features

- **School Identity & Affiliation**: Tailored for Indian schools with CBSE Affiliation details (Affiliation No: 1930245, School Code: 45123).
- **Indian Currency & Numbering**: All fees, balances, receipts, and collection registers formatted in Indian Rupees (**₹**) with Indian number grouping (`₹12,000.00`).
- **Standard Indian Fee Heads**:
  - `Tuition Fee` (ट्यूशन फीस)
  - `Computer & Smart Class Fee` (AI / Multimedia lab)
  - `Library & Learning Resources`
  - `Sports & Co-Curricular Activities`
  - `School Bus Transport (Route-based)`
  - `Hostel & Mess Boarding`
  - `Admission & Registration Fee`
- **Indian Concession & Scholarship Engine**:
  - `Merit Scholarships (25% & 50%)`
  - `Sibling Concession (₹1,500 flat concession for younger siblings)`
  - `Staff Ward Benefit (50% Tuition fee waiver for teachers & staff wards)`
  - `RTE / EWS Fee Waiver (100% Tuition waiver for Right to Education quota)`
- **Academic Calendar & Billing Cycles**:
  - Quarterly fee schedules:
    - **Quarter 1**: April – June
    - **Quarter 2**: July – September
    - **Quarter 3**: October – December
    - **Quarter 4**: January – March
  - Half-Yearly (Term-1 / Term-2) & Annual options.
- **Indian Payment Modes**:
  - **UPI** (Google Pay, PhonePe, Paytm, BHIM with UTR Number logging).
  - **Net Banking (IMPS / NEFT / RTGS)**.
  - **Fee Counter Cash**.
  - **Cheque / Demand Draft (DD)** with Cheque No. & Bank Name.
  - **POS Debit / Credit Card (RuPay, Visa, MasterCard)**.
- **Tamper-Evident Receipts**:
  - Sequential receipt numbering (`REC-2026-0001`).
  - SHA-256 cryptographic verification seal.
  - Printable HTML receipt with CBSE school header and digital verification stamp.

---

## Directory Structure

```
school-fee-system/
├── pyproject.toml              # uv / pip package configuration
├── src/
│   └── school_fee_system/
│       ├── __init__.py         # Package exports
│       ├── __main__.py         # python -m executable entrypoint
│       ├── models.py           # Domain dataclasses & Enums (Decimal-based)
│       ├── database.py         # SQLite schema, WAL mode, foreign keys, demo seeds
│       ├── fee_calculator.py   # Calculation engine (discounts, late fees, proration)
│       ├── receipt_generator.py# Cryptographic SHA-256 hash & receipt formats
│       ├── services.py         # Business logic, audit logging & reporting
│       ├── cli.py              # CLI argument parser & table renderers
│       └── server.py           # Single-Page Web Dashboard & REST API server
└── tests/
    └── test_fee_system.py      # Automated unit & integration tests
```

---

## Quickstart & Setup

### 1. Initialize Virtual Environment
Using `uv`:
```bash
uv venv
source .venv/bin/activate
```

Or using standard Python:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Run Automated Test Suite
```bash
PYTHONPATH=src python -m unittest discover -v -s tests
```

### 3. Initialize Database with Demo Data
```bash
PYTHONPATH=src python -m school_fee_system init-db --seed
```

---

## CLI Usage Guide

All commands support the `--db <path>` flag to specify a custom database location (defaults to `~/.local/share/school_fee_system/fees.db`).

### 1. Enrolled Students
```bash
# List all enrolled students
python -m school_fee_system students list

# Filter students by class or search query
python -m school_fee_system students list --search "Sharma"

# View individual student account statement & payment ledger
python -m school_fee_system students statement --id STU-2026-001

# Enroll a new student
python -m school_fee_system students add \
  --id STU-2026-006 \
  --first "Lucas" \
  --last "Miller" \
  --class-id 1 \
  --parent-name "Sarah Miller" \
  --email "sarah@example.com" \
  --phone "+1-555-0199" \
  --transport
```

### 2. Fee Structures & Discount Policies
```bash
# View all fee heads (Tuition, Lab, Transport, etc.)
python -m school_fee_system fees list-heads

# View class fee structures
python -m school_fee_system fees list-structures

# View scholarship and concession policies
python -m school_fee_system fees list-discounts
```

### 3. Generating Invoices
```bash
# Generate an invoice for an individual student (auto-applies discounts & services)
python -m school_fee_system invoices generate \
  --student-id STU-2026-001 \
  --year 2026-2027 \
  --term TERM_1

# Batch generate invoices for an entire class
python -m school_fee_system invoices batch-generate \
  --class-id 1 \
  --year 2026-2027 \
  --term TERM_1

# List invoices
python -m school_fee_system invoices list

# Inspect fee item breakdown on an invoice
python -m school_fee_system invoices view --id INV-2026-0001
```

### 4. Collecting Payments & Printing Receipts
```bash
# Record a payment (Cash, UPI, ONLINE_CARD, CHEQUE, BANK_TRANSFER)
python -m school_fee_system payments record \
  --invoice-id 1 \
  --amount 630.00 \
  --method UPI \
  --tx-id "UPI-992211" \
  --cashier "Sarah Connor"

# View terminal ASCII receipt
python -m school_fee_system receipts view --number REC-2026-0001

# Export printable HTML receipt for browser/PDF printing
python -m school_fee_system receipts view --number REC-2026-0001 --html receipt.html

# Cryptographically verify receipt authenticity
python -m school_fee_system receipts verify --number REC-2026-0001
```

### 5. Defaulters & Financial Accounting
```bash
# Display students with overdue fee invoices
python -m school_fee_system defaulters

# Export defaulters list to CSV
python -m school_fee_system defaulters --export overdue_students.csv

# View fee collection summary by payment method
python -m school_fee_system reports collection

# Export all collections to CSV for audit
python -m school_fee_system reports collection --export fee_collections.csv
```

---

## Interactive Web Dashboard & REST API

Launch the built-in Web UI server:
```bash
python -m school_fee_system serve --port 8000
```
Open **`http://127.0.0.1:8000/`** in your browser.

### Web Dashboard Features:
- **Executive KPIs**: Real-time revenue, outstanding dues, defaulters count, active student metrics.
- **Live Student Directory**: Add students, search records, view account ledgers.
- **Fee Collection Terminal**: Select open invoices, enter partial or full amounts, record transactions, and instantly popup a printable receipt.
- **Overdue Defaulters Tracker**: Filter by overdue duration and export to CSV.
- **REST APIs**: JSON endpoints under `/api/` for integrating with external portals and parent apps.
