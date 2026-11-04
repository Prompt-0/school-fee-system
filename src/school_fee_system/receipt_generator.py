"""
Receipt generation and cryptographic tamper-detection for fee payments.
Provides:
- Cryptographic SHA-256 hash generation for fraud prevention.
- Clean formatted ASCII/text receipts for thermal or terminal printers.
- Semantic, printable HTML receipt templates with school insignia and verification stamps.
"""

from __future__ import annotations

import hashlib
from decimal import Decimal
from typing import Optional

from school_fee_system.models import Receipt, Payment, Invoice, Student


SECRET_SALT = "SCHOOL-FEE-SECURE-AUDIT-SALT-2026"


def compute_receipt_hash(receipt_number: str, payment_ref: str, amount: Decimal, student_id: str, date_str: str) -> str:
    """Computes SHA-256 checksum incorporating payment details and secret salt."""
    raw_payload = f"{receipt_number}|{payment_ref}|{amount:.2f}|{student_id}|{date_str}|{SECRET_SALT}"
    return hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()


def verify_receipt_hash(receipt_number: str, payment_ref: str, amount: Decimal, student_id: str, date_str: str, expected_hash: str) -> bool:
    """Verifies whether a given receipt has been modified or tampered with."""
    computed = compute_receipt_hash(receipt_number, payment_ref, amount, student_id, date_str)
    return computed == expected_hash


class ReceiptFormatter:
    @staticmethod
    def format_text(receipt: Receipt) -> str:
        """Renders an ASCII text receipt suitable for CLI or thermal receipt printers."""
        p: Payment = receipt.payment or Payment(
            id=0, payment_ref="N/A", invoice_id=0, amount=Decimal("0.00"),
            payment_method="CASH", transaction_id="", payment_date=receipt.created_at, cashier_name="Admin"
        )
        inv: Optional[Invoice] = receipt.invoice
        stu: Optional[Student] = receipt.student

        inv_num = inv.invoice_number if inv else "N/A"
        stu_id = stu.student_id if stu else (inv.student_id if inv else "N/A")
        stu_name = stu.full_name if stu else (inv.student_name if inv else "N/A")
        cls_name = stu.class_name if stu else (inv.class_name if inv else "N/A")
        balance = inv.balance_amount if inv else Decimal("0.00")

        method_str = p.payment_method.value if hasattr(p.payment_method, "value") else str(p.payment_method)
        lines = [
            "=" * 55,
            "            DELHI PUBLIC ACADEMY",
            "   (Affiliated to CBSE, New Delhi | Affil No: 1930245)",
            "         OFFICIAL FEE PAYMENT RECEIPT",
            "=" * 55,
            f"Receipt No    : {receipt.receipt_number}",
            f"Date & Time   : {receipt.created_at.strftime('%d-%b-%Y %I:%M %p')}",
            f"Payment Ref   : {p.payment_ref}",
            f"Payment Mode  : {method_str}",
            f"UTR / Txn Ref : {p.transaction_id or 'CASH-COUNTER'}",
            f"Cashier / Auth: {p.cashier_name}",
            "-" * 55,
            f"Admission No  : {stu_id}",
            f"Student Name  : {stu_name}",
            f"Class/Section : {cls_name}",
            f"Parent Name   : {stu.parent_name if stu else 'N/A'}",
            f"Bill / Inv No : {inv_num}",
            "-" * 55,
            f"Amount Paid   : ₹{p.amount:.2f}",
            f"Remaining Due : ₹{balance:.2f}",
            "-" * 55,
            "Digital Verification Seal (SHA-256):",
            f"  {receipt.receipt_hash[:36]}...",
            "=" * 55,
            "  Computer-generated fee receipt. No physical signature required.",
            "=" * 55,
        ]
        return "\n".join(lines)

    @staticmethod
    def format_html(receipt: Receipt) -> str:
        """Renders an elegant, printable Indian school HTML receipt."""
        p = receipt.payment
        inv = receipt.invoice
        stu = receipt.student

        amount_val = f"₹{p.amount:.2f}" if p else "₹0.00"
        balance_val = f"₹{inv.balance_amount:.2f}" if inv else "₹0.00"

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Fee Receipt - {receipt.receipt_number}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #f8fafc; color: #1e293b; padding: 2rem; }}
  .receipt-card {{ max-width: 680px; margin: 0 auto; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); padding: 2.5rem; }}
  .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #0f766e; padding-bottom: 1.25rem; margin-bottom: 1.5rem; }}
  .school-title {{ font-size: 1.45rem; font-weight: 800; color: #0f766e; text-transform: uppercase; letter-spacing: 0.5px; }}
  .badge {{ background: #ccfbf1; color: #0f766e; padding: 0.35rem 0.75rem; border-radius: 9999px; font-size: 0.825rem; font-weight: 700; text-transform: uppercase; border: 1px solid #99f6e4; }}
  .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem; }}
  .info-label {{ font-size: 0.72rem; text-transform: uppercase; color: #64748b; font-weight: 700; letter-spacing: 0.5px; }}
  .info-val {{ font-size: 0.95rem; font-weight: 600; color: #0f172a; margin-top: 2px; }}
  .amount-box {{ background: #f0fdfa; border: 1px solid #99f6e4; border-radius: 8px; padding: 1.25rem; display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }}
  .amount-val {{ font-size: 1.85rem; font-weight: 800; color: #0f766e; }}
  .footer {{ border-top: 1px solid #e2e8f0; padding-top: 1rem; font-size: 0.75rem; color: #94a3b8; display: flex; justify-content: space-between; align-items: center; }}
  .hash {{ font-family: monospace; word-break: break-all; max-width: 340px; color: #64748b; }}
  .stamp-box {{ border: 2px dashed #0f766e; color: #0f766e; padding: 0.4rem 0.8rem; border-radius: 6px; font-weight: 700; font-size: 0.75rem; text-align: center; text-transform: uppercase; }}
  @media print {{
    body {{ background: #ffffff; padding: 0; }}
    .receipt-card {{ border: none; box-shadow: none; padding: 0; }}
  }}
</style>
</head>
<body>
<div class="receipt-card">
  <div class="header">
    <div>
      <div class="school-title">DELHI PUBLIC ACADEMY</div>
      <div style="font-size: 0.825rem; color: #64748b; margin-top: 2px;">Affiliated to CBSE, New Delhi | Affiliation No. 1930245</div>
      <div style="font-size: 0.775rem; color: #94a3b8;">Institutional Area, Sector 12, New Delhi — 110075</div>
    </div>
    <div class="badge">Official Fee Receipt</div>
  </div>

  <div class="info-grid">
    <div>
      <div class="info-label">Receipt Number</div>
      <div class="info-val" style="color: #0f766e;">{receipt.receipt_number}</div>
    </div>
    <div>
      <div class="info-label">Date & Time of Payment</div>
      <div class="info-val">{receipt.created_at.strftime('%d %B %Y - %I:%M %p')}</div>
    </div>
    <div>
      <div class="info-label">Admission / S.R. No.</div>
      <div class="info-val">{stu.student_id if stu else 'N/A'}</div>
    </div>
    <div>
      <div class="info-label">Student Name</div>
      <div class="info-val">{stu.full_name if stu else (inv.student_name if inv else 'N/A')}</div>
    </div>
    <div>
      <div class="info-label">Class & Section</div>
      <div class="info-val">{stu.class_name if stu else (inv.class_name if inv else 'N/A')}</div>
    </div>
    <div>
      <div class="info-label">Father / Guardian Name</div>
      <div class="info-val">{stu.parent_name if stu else 'N/A'}</div>
    </div>
    <div>
      <div class="info-label">Invoice Reference</div>
      <div class="info-val">{inv.invoice_number if inv else 'N/A'} ({inv.term.value if inv else 'N/A'})</div>
    </div>
    <div>
      <div class="info-label">Payment Mode & UTR / Cheque Ref</div>
      <div class="info-val">{p.payment_method if p else 'N/A'} — {p.transaction_id if (p and p.transaction_id) else 'COUNTER-CASH'}</div>
    </div>
  </div>

  <div class="amount-box">
    <div>
      <div style="font-size: 0.85rem; font-weight: 700; color: #115e59; text-transform: uppercase;">Amount Received</div>
      <div style="font-size: 0.8rem; color: #64748b; margin-top: 2px;">Authorized Cashier: {p.cashier_name if p else 'Counter Cashier'}</div>
    </div>
    <div class="amount-val">{amount_val}</div>
  </div>

  <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem; margin-bottom: 1.5rem; color: #475569; background: #f8fafc; padding: 0.75rem 1rem; border-radius: 6px;">
    <span>Remaining Balance for Term: <strong style="color: #b91c1c;">{balance_val}</strong></span>
    <div class="stamp-box">✓ FEE VERIFIED & CREDITED</div>
  </div>

  <div class="footer">
    <div>
      <div style="font-weight: 700; font-size: 0.75rem; text-transform: uppercase;">Digital Security Hash (SHA-256)</div>
      <div class="hash">{receipt.receipt_hash}</div>
    </div>
    <div style="text-align: right;">
      Accounts & Billing Department
      <div style="font-size: 0.7rem; color: #64748b;">Delhi Public Academy • Accounts Cell</div>
    </div>
  </div>
</div>
</body>
</html>"""
