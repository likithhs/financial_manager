"""
FinAI Backend Foundation - Input Validation Utility
Provides reusable validators for monetary amounts, emails, passwords, dates, and IDs.
"""

import re
from datetime import datetime
from decimal import Decimal, InvalidOperation

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


class ValidationError(Exception):
    """Custom exception raised when data validation fails."""
    def __init__(self, message, field=None):
        super().__init__(message)
        self.message = message
        self.field = field


def validate_required_fields(data, required_fields):
    """
    Validates that all required fields are present and non-empty in the provided data dict.
    Raises ValidationError if any field is missing.
    """
    for field in required_fields:
        val = data.get(field)
        if val is None or (isinstance(val, str) and not val.strip()):
            raise ValidationError(f"Field '{field}' is required and cannot be blank.", field=field)
    return True


def validate_email(email):
    """
    Validates that the email has a valid format.
    Returns normalized lowercase email or raises ValidationError.
    """
    if not email or not isinstance(email, str):
        raise ValidationError("Valid email address is required.", field="email")
    email = email.strip().lower()
    if not EMAIL_REGEX.match(email):
        raise ValidationError("Invalid email address format.", field="email")
    return email


def validate_password(password, min_length=6):
    """
    Validates password length and structure.
    Raises ValidationError if too short.
    """
    if not password or len(password) < min_length:
        raise ValidationError(f"Password must be at least {min_length} characters long.", field="password")
    return True


def validate_monetary_amount(amount, min_val=0.01, max_val=100000000.00, field_name="amount"):
    """
    Validates that a financial amount is numeric, positive, and within realistic boundaries.
    Returns clean Decimal representation with 2 decimal places.
    """
    if amount is None or amount == "":
        raise ValidationError(f"{field_name.capitalize()} cannot be empty.", field=field_name)
    try:
        dec_amount = Decimal(str(amount)).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        raise ValidationError(f"{field_name.capitalize()} must be a valid number.", field=field_name)

    if dec_amount < Decimal(str(min_val)):
        raise ValidationError(f"{field_name.capitalize()} must be at least {min_val}.", field=field_name)
    if dec_amount > Decimal(str(max_val)):
        raise ValidationError(f"{field_name.capitalize()} exceeds maximum allowable limit.", field=field_name)
    return dec_amount


def validate_date(date_str, field_name="date"):
    """
    Validates that a date string follows YYYY-MM-DD format.
    Returns date object or raises ValidationError.
    """
    if not date_str or not isinstance(date_str, str):
        raise ValidationError(f"{field_name.capitalize()} cannot be empty.", field=field_name)
    try:
        parsed_date = datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
        return parsed_date
    except ValueError:
        raise ValidationError(f"{field_name.capitalize()} must be formatted as YYYY-MM-DD.", field=field_name)


def validate_id(id_val, field_name="id"):
    """
    Validates positive integer ID.
    """
    try:
        int_id = int(id_val)
        if int_id <= 0:
            raise ValueError()
        return int_id
    except (TypeError, ValueError):
        raise ValidationError(f"Invalid {field_name}. Must be a positive integer.", field=field_name)
