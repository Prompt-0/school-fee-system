# 💻 School Fee Management System — In-Browser Web Terminal

A self-contained, interactive **Web Terminal Console** for Delhi Public Academy's fee management and accounting system. 

It provides a retro-modern CLI interface directly inside your web browser with real-time ANSI colors, tab completion, command history, mobile touch controls, and cryptographic receipt verification.

---

## ✨ Features

- **In-Browser Terminal**: Full keyboard navigation (`↑`/`↓` history, `Tab` completion, `Ctrl+L` clear, `Ctrl+C` cancel).
- **Zero External Dependencies**: Powered by Python's built-in `http.server` and vanilla JavaScript with a fast custom ANSI escape sequence renderer.
- **CBSE Accounting Suite**: Complete access to student records, quarterly fee invoices, payment processing, defaulter lists, and revenue analytics.
- **Multiple Color Themes**:
  - `teal` — Modern Fedora Dark Slate with Teal accent (Default)
  - `matrix` — Phosphor Green on Onyx Black
  - `amber` — Vintage Amber CRT
  - `nord` — Arctic Frost & Slate Blue
  - `cyberpunk` — Neon Cyan & Hot Magenta
- **Retro CRT Mode**: Optional toggle for scanline and phosphor glow effect.
- **Mobile Optimized**: Bottom touch bar with virtual keys (`TAB`, `↑`, `↓`, `kpis`, `students`, `invoices`, `pay`, `defaulters`) and 16px inputs to prevent auto-zooming.

---

## 🚀 Running the Web Terminal

### Mode 1: Standalone Subproject Server (Port 8080)
From the repository root:
```bash
python -m web_terminal --port 8080
```
Open your browser at:
👉 **`http://127.0.0.1:8080/`**

### Mode 2: Integrated with the Main Application (Port 8000 or Cloud)
The Web Terminal is automatically mounted into the primary application server at the `/terminal` route:
```bash
python -m school_fee_system serve --port 8000
```
Open your browser at:
👉 **`http://127.0.0.1:8000/terminal`**  
*(or on Render: `https://con-academy.onrender.com/terminal`)*

---

## 📖 Command Reference & Cheatsheet

| Command | Arguments | Description |
| :--- | :--- | :--- |
| `help` | `[cmd]` | Displays the full manual or command-specific help |
| `kpis` | — | Shows real-time financial metrics in an ASCII box (Active students, revenue, dues) |
| `students list` | `[--class <id>] [--search <str>]` | Tabulates enrolled pupils with guardian contact and transport/hostel flags |
| `students view` | `<student_id>` | Displays full student profile, billing ledger, and transaction history |
| `invoices list` | `[--status <PAID/UNPAID/OVERDUE>]` | Lists invoices with due dates, gross amounts, and remaining balances |
| `invoices view` | `<invoice_id_or_num>` | Displays itemized fee heads (Tuition, Lab, Transport) and concessions |
| `invoices generate` | `<student_id> [term] [year]` | Generates a quarterly fee invoice for a student |
| `pay` | `<inv_id> <amount> [method] [tx_id] [cashier]` | Records payment, updates balance, and prints official receipt |
| `receipts view` | `<receipt_number>` | Displays ASCII receipt with SHA-256 digital security seal |
| `receipts verify` | `<receipt_number>` | Cryptographically audits receipt authenticity against tampering |
| `defaulters` | `[min_days]` | Lists all overdue accounts with days overdue and parent phone numbers |
| `reports collection` | — | Revenue summary grouped by payment method (UPI, Cash, Cheque, etc.) |
| `classes` | — | Lists all classes and section grade levels |
| `theme` | `<teal \| matrix \| amber \| nord \| cyberpunk>` | Switches the terminal color palette live |
| `banner` | — | Displays the official school crest ASCII banner |
| `clear` | — | Clears the terminal output screen (`Ctrl+L`) |

---

## 💡 Example Sessions

### 1. View School KPIs
```text
admin@dpa-terminal:~$ kpis
┌────────────────────────────────────────────────────────────────────────┐
│         DELHI PUBLIC ACADEMY — REAL-TIME FINANCIAL SUMMARY             │
├──────────────────┬──────────────────┬──────────────────┬───────────────┤
│ ACTIVE PUPILS    │ TOTAL COLLECTED  │ OUTSTANDING DUES │ DEFAULTERS      │
│        43        │   ₹2,95,400.00   │   ₹642,800.00    │       6       │
└──────────────────┴──────────────────┴──────────────────┴───────────────┘
```

### 2. Check Overdue Defaulters
```text
admin@dpa-terminal:~$ defaulters
FEE DEFAULTERS LIST (6 overdue accounts):
┌───────────────┬─────────────────┬───────────────────┬─────────────────┬────────────┬─────────┬─────────────┐
│ Invoice #     │ Student Name    │ Class             │ Guardian Phone  │ Due Date   │ Overdue │ Balance Due │
├───────────────┼─────────────────┼───────────────────┼─────────────────┼────────────┼─────────┼─────────────┤
│ INV-2026-0004 │ Ananya Iyer     │ Class 10-A        │ +91 98440 45678 │ 2026-10-20 │ 16 days │  ₹20,975.00 │
│ INV-2026-0011 │ Reyansh Gupta   │ Class 10-B        │ +91 98445 67890 │ 2026-10-20 │ 16 days │  ₹40,475.00 │
...
```

### 3. Record UPI Fee Payment
```text
admin@dpa-terminal:~$ pay 4 20975.00 UPI UTR-882341901 Cashier-1
✓ PAYMENT RECORDED SUCCESSFULLY!
  Payment Ref   : PAY-2026-0008
  Amount Credited: ₹20,975.00
  Payment Mode  : UPI (Tx: UTR-882341901)
  Receipt Issued: REC-2026-0008
  Digital Seal  : 6f8e79b9a241e...
```
