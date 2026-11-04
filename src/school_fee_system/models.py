"""
Domain models and Enums for the School Student Fee Management System.
Uses standard library dataclasses and Decimal for exact financial arithmetic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any


class StudentStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    GRADUATED = "GRADUATED"
    TRANSFERRED = "TRANSFERRED"


class FeeTerm(str, Enum):
    ANNUAL = "ANNUAL"
    QUARTER_1 = "QUARTER_1"  # Apr - Jun
    QUARTER_2 = "QUARTER_2"  # Jul - Sep
    QUARTER_3 = "QUARTER_3"  # Oct - Dec
    QUARTER_4 = "QUARTER_4"  # Jan - Mar
    TERM_1 = "TERM_1"        # Half-Yearly (Apr - Sep)
    TERM_2 = "TERM_2"        # Annual (Oct - Mar)
    TERM_3 = "TERM_3"
    MONTHLY = "MONTHLY"


class DiscountType(str, Enum):
    PERCENTAGE = "PERCENTAGE"
    FIXED = "FIXED"


class InvoiceStatus(str, Enum):
    DRAFT = "DRAFT"
    UNPAID = "UNPAID"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    PAID = "PAID"
    OVERDUE = "OVERDUE"
    CANCELLED = "CANCELLED"


class PaymentMethod(str, Enum):
    UPI = "UPI"                      # Google Pay, PhonePe, Paytm, BHIM
    NET_BANKING = "NET_BANKING"      # NEFT / RTGS / IMPS
    CASH = "CASH"                    # Fee Counter Cash
    CHEQUE_DD = "CHEQUE_DD"          # Cheque or Demand Draft
    CARD = "CARD"                    # POS RuPay / Visa / MasterCard
    # Backward compatibility aliases
    CHEQUE = "CHEQUE"
    BANK_TRANSFER = "BANK_TRANSFER"
    ONLINE_CARD = "ONLINE_CARD"


@dataclass
class ClassSection:
    id: Optional[int]
    name: str  # e.g. "Grade 10-A"
    grade_level: int  # e.g. 10
    created_at: Optional[datetime] = None


@dataclass
class Student:
    student_id: str  # Unique Admission No, e.g. "STU-2026-001"
    first_name: str
    last_name: str
    class_id: int
    parent_name: str
    parent_email: str
    parent_phone: str
    is_transport_enrolled: bool = False
    is_hostel_enrolled: bool = False
    status: StudentStatus = StudentStatus.ACTIVE
    class_name: Optional[str] = None
    created_at: Optional[datetime] = None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


@dataclass
class FeeHead:
    id: Optional[int]
    name: str  # e.g. "Tuition Fee"
    code: str  # e.g. "TUITION"
    description: str = ""
    is_recurring: bool = True
    is_optional: bool = False


@dataclass
class FeeStructureItem:
    fee_head_id: int
    head_name: str
    head_code: str
    amount: Decimal


@dataclass
class FeeStructure:
    id: Optional[int]
    name: str  # e.g. "Grade 10 Term-1 Fee 2026"
    class_id: int
    academic_year: str  # e.g. "2026-2027"
    term: FeeTerm
    items: List[FeeStructureItem] = field(default_factory=list)
    class_name: Optional[str] = None

    @property
    def total_base_amount(self) -> Decimal:
        return sum((item.amount for item in self.items), Decimal("0.00"))


@dataclass
class DiscountPolicy:
    id: Optional[int]
    name: str  # e.g. "Merit Concession"
    code: str  # e.g. "MERIT_25"
    discount_type: DiscountType
    value: Decimal  # e.g. 25.00 for 25% or 500.00 for $500
    applies_to_head_code: Optional[str] = None  # None = entire bill or specific like "TUITION"
    description: str = ""


@dataclass
class InvoiceItem:
    id: Optional[int]
    fee_head_id: int
    head_name: str
    head_code: str
    amount: Decimal
    discount_amount: Decimal
    net_amount: Decimal


@dataclass
class Invoice:
    id: Optional[int]
    invoice_number: str  # e.g. "INV-2026-0001"
    student_id: str
    academic_year: str
    term: FeeTerm
    issue_date: date
    due_date: date
    subtotal: Decimal
    discount_total: Decimal
    late_fee: Decimal
    total_payable: Decimal
    paid_amount: Decimal
    status: InvoiceStatus
    items: List[InvoiceItem] = field(default_factory=list)
    student_name: Optional[str] = None
    class_name: Optional[str] = None
    parent_email: Optional[str] = None
    parent_phone: Optional[str] = None
    created_at: Optional[datetime] = None

    @property
    def balance_amount(self) -> Decimal:
        return max(Decimal("0.00"), self.total_payable - self.paid_amount)


@dataclass
class Payment:
    id: Optional[int]
    payment_ref: str  # e.g. "PAY-2026-0001"
    invoice_id: int
    amount: Decimal
    payment_method: PaymentMethod
    transaction_id: str  # Bank ref, Cheque no, or "CASH-COUNTER"
    payment_date: datetime
    cashier_name: str
    notes: str = ""
    invoice_number: Optional[str] = None
    student_id: Optional[str] = None
    student_name: Optional[str] = None


@dataclass
class Receipt:
    id: Optional[int]
    receipt_number: str  # e.g. "REC-2026-0001"
    payment_id: int
    receipt_hash: str  # SHA-256 verification hash
    created_at: datetime
    payment: Optional[Payment] = None
    invoice: Optional[Invoice] = None
    student: Optional[Student] = None
