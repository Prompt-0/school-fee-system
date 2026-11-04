"""
School Student Fee Management System.
"""

from school_fee_system.cli import main
from school_fee_system.services import SchoolFeeService
from school_fee_system.fee_calculator import FeeCalculator
from school_fee_system.database import connect_db, initialize_schema, seed_sample_data

__all__ = [
    "main",
    "SchoolFeeService",
    "FeeCalculator",
    "connect_db",
    "initialize_schema",
    "seed_sample_data",
]
