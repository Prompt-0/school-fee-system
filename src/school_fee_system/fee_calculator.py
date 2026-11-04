"""
Calculation engine for School Student Fees.
Performs exact Decimal arithmetic for:
- Base fee aggregation according to student optional service enrollments (transport, hostel).
- Concession and scholarship deductions (percentage, fixed amount, head-targeted).
- Late fee and overdue penalty assessments with grace periods.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional

from school_fee_system.models import (
    Student,
    FeeStructure,
    FeeStructureItem,
    DiscountPolicy,
    DiscountType,
    InvoiceItem,
)


CENT = Decimal("0.01")


def round_currency(val: Decimal) -> Decimal:
    """Rounds a Decimal value to two decimal places using standard financial rounding."""
    return val.quantize(CENT, rounding=ROUND_HALF_UP)


@dataclass
class CalculatedFeeItem:
    fee_head_id: int
    head_name: str
    head_code: str
    amount: Decimal
    discount_amount: Decimal
    net_amount: Decimal


@dataclass
class CalculationResult:
    items: List[CalculatedFeeItem]
    subtotal: Decimal
    discount_total: Decimal
    late_fee: Decimal
    total_payable: Decimal


class FeeCalculator:
    @staticmethod
    def calculate_late_fee(
        due_date: date,
        as_of_date: date,
        grace_period_days: int = 7,
        rate_per_day: Decimal = Decimal("5.00"),
        flat_fee: Decimal = Decimal("25.00"),
        use_daily_rate: bool = True,
        max_cap: Decimal = Decimal("150.00"),
    ) -> Decimal:
        """
        Calculates overdue fine based on due date and assessment date.
        If evaluated within the grace period, penalty is 0.
        """
        if as_of_date <= due_date:
            return Decimal("0.00")

        grace_deadline = due_date + timedelta(days=grace_period_days)
        if as_of_date <= grace_deadline:
            return Decimal("0.00")

        overdue_days = (as_of_date - due_date).days
        if use_daily_rate:
            raw_penalty = Decimal(overdue_days) * rate_per_day
        else:
            raw_penalty = flat_fee

        final_penalty = min(raw_penalty, max_cap)
        return round_currency(max(Decimal("0.00"), final_penalty))

    @classmethod
    def compute_student_fees(
        cls,
        student: Student,
        structure: FeeStructure,
        discounts: List[DiscountPolicy],
        as_of_date: Optional[date] = None,
        due_date: Optional[date] = None,
        include_late_fee: bool = True,
    ) -> CalculationResult:
        """
        Computes the complete fee breakdown for a student given their class fee structure
        and awarded scholarships/discounts.
        """
        calculated_items: List[CalculatedFeeItem] = []
        subtotal = Decimal("0.00")
        discount_total = Decimal("0.00")

        for item in structure.items:
            # Check for optional services opt-in
            if item.head_code == "TRANSPORT" and not student.is_transport_enrolled:
                continue
            if item.head_code == "HOSTEL" and not student.is_hostel_enrolled:
                continue

            base_amount = round_currency(item.amount)
            item_discount = Decimal("0.00")

            # Check if any discount policy applies to this item
            for policy in discounts:
                if policy.applies_to_head_code:
                    if policy.applies_to_head_code == item.head_code:
                        if policy.discount_type == DiscountType.PERCENTAGE:
                            disc_calc = (base_amount * policy.value) / Decimal("100.00")
                            item_discount += disc_calc
                        elif policy.discount_type == DiscountType.FIXED:
                            item_discount += policy.value
                else:
                    # General discount (applies_to_head_code is None)
                    # Percentage applies across all items
                    if policy.discount_type == DiscountType.PERCENTAGE:
                        disc_calc = (base_amount * policy.value) / Decimal("100.00")
                        item_discount += disc_calc
                    # Fixed general discounts are deducted in the aggregate pass below

            # Discount cannot exceed the item's cost
            item_discount = min(base_amount, item_discount)
            item_discount = round_currency(item_discount)
            net_item = base_amount - item_discount

            subtotal += base_amount
            discount_total += item_discount

            calculated_items.append(
                CalculatedFeeItem(
                    fee_head_id=item.fee_head_id,
                    head_name=item.head_name,
                    head_code=item.head_code,
                    amount=base_amount,
                    discount_amount=item_discount,
                    net_amount=net_item,
                )
            )

        # Check for unallocated fixed discounts that apply generally (head_code is None)
        general_discounts = [d for d in discounts if d.applies_to_head_code is None and d.discount_type == DiscountType.FIXED]
        for g_disc in general_discounts:
            remaining_to_deduct = round_currency(g_disc.value)
            for calc_item in calculated_items:
                if remaining_to_deduct <= Decimal("0.00"):
                    break
                available_for_discount = calc_item.net_amount
                if available_for_discount > Decimal("0.00"):
                    deduct = min(available_for_discount, remaining_to_deduct)
                    calc_item.discount_amount = round_currency(calc_item.discount_amount + deduct)
                    calc_item.net_amount = round_currency(calc_item.amount - calc_item.discount_amount)
                    discount_total += deduct
                    remaining_to_deduct -= deduct

        subtotal = round_currency(subtotal)
        discount_total = round_currency(discount_total)

        # Late fee computation
        late_fee = Decimal("0.00")
        if include_late_fee and due_date and as_of_date:
            late_fee = cls.calculate_late_fee(due_date=due_date, as_of_date=as_of_date)

        total_payable = round_currency((subtotal - discount_total) + late_fee)

        return CalculationResult(
            items=calculated_items,
            subtotal=subtotal,
            discount_total=discount_total,
            late_fee=late_fee,
            total_payable=total_payable,
        )
