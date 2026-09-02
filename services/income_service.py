"""
FinAI Backend Foundation - Income Service
Handles transaction-based income logging and user-isolated retrieval.
"""

from decimal import Decimal
from database import query_db, execute_db
from services.validators import validate_monetary_amount, validate_date, validate_required_fields


class IncomeService:
    @staticmethod
    def get_user_incomes(user_id):
        """
        Retrieves all income transactions belonging strictly to the authenticated user.
        Preserves complete transaction history (ordered latest first).
        """
        return query_db(
            "SELECT id, user_id, source, amount, category, date, description, created_at "
            "FROM incomes WHERE user_id = %s ORDER BY date DESC, id DESC",
            (user_id,)
        )

    @staticmethod
    def get_total_income(user_id):
        """Calculates total accumulated income for the authenticated user."""
        row = query_db(
            "SELECT COALESCE(SUM(amount), 0) as total FROM incomes WHERE user_id = %s",
            (user_id,),
            one=True
        )
        return Decimal(str(row['total'])) if row else Decimal("0.00")

    @staticmethod
    def add_income(user_id, source, amount, category="Salary / Wages", date_str=None, description=""):
        """
        Records an individual income transaction.
        Strictly preserves previous transactions without overwriting.
        """
        validate_required_fields({"source": source}, ["source"])
        clean_amount = validate_monetary_amount(amount, field_name="income amount")
        clean_date = validate_date(str(date_str)) if date_str else None

        # Insert into incomes (and sync with income table)
        inc_id = execute_db("""
            INSERT INTO incomes (user_id, source, amount, category, date, description)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, source.strip(), clean_amount, category, clean_date, description))

        try:
            execute_db("""
                INSERT INTO income (user_id, amount, source, date, description)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, clean_amount, source.strip(), clean_date, description))
        except Exception:
            pass

        return inc_id

    @staticmethod
    def delete_income(income_id, user_id):
        """Deletes an income entry strictly verifying user ownership."""
        return execute_db("DELETE FROM incomes WHERE id = %s AND user_id = %s", (income_id, user_id))
