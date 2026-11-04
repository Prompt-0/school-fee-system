# Indian School Dummy Dataset — Delhi Public Academy

This folder contains realistic demo data for the **Delhi Public Academy (CBSE Affiliated, New Delhi)** fee management system.

---

## Contents

| File | Description |
| :--- | :--- |
| **`delhi_public_academy_demo.db`** | Pre-populated SQLite database with 43 students, 12 classes, fee structures, invoices, UPI/NEFT/Cheque payment receipts, and audit hashes. |
| **`students.json`** | JSON export containing student admission profiles, class mappings, parent contacts (+91 mobile numbers), and opted facilities (Bus / Hostel). |
| **`classes.json`** | JSON export containing standard class sections (Class 1 through Class 12). |
| **`seed_data.sql`** | Complete standard SQL dump of schema and transactions for importing into SQLite or converting to PostgreSQL/MySQL. |
| **`generate_dummy_data.py`** | Standalone Python script to regenerate, re-seed, or customize this dataset at any time. |

---

## Dataset Statistics

- **Total Enrolled Students**: 43 students across Primary, Middle, Secondary, and Senior Secondary (Science & Commerce).
- **Total Fee Collected**: ₹2,95,400.00
- **Total Outstanding Dues**: ₹6,42,800.00
- **Overdue Defaulters**: 6 students with calculated late fee penalties and parent phone numbers.
- **Payment Modes Represented**:
  - **UPI** (Google Pay, PhonePe, Paytm, BHIM with UTR / Transaction references).
  - **Net Banking** (HDFC, SBI, ICICI, Axis NEFT/IMPS).
  - **Cheque & Demand Draft** (SBI, PNB).
  - **Fee Counter Cash**.
  - **POS Card** (RuPay, Visa).
- **Concessions & Scholarships**:
  - Merit Scholarship (25% & 50%)
  - Sibling Concession (₹1,500 flat)
  - Staff Ward Concession (50%)
  - RTE / EWS Fee Waiver (100%)
  - Sports Quota Concession (30%)

---

## How to Load This Demo Database

To run the fee management system directly against this demo database:

```bash
# Using CLI
python -m school_fee_system --db dummy_data/delhi_public_academy_demo.db students list

# Launching Web Server with demo data
python -m school_fee_system --db dummy_data/delhi_public_academy_demo.db serve --port 8000
```
