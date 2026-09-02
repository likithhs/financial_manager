"""
FinAI Backend Foundation - Expense Service
Handles categorized expense tracking, budget burn calculations, and user isolation.
"""

from decimal import Decimal
from database import query_db, execute_db
from services.validators import validate_monetary_amount, validate_date, validate_required_fields


class ExpenseService:
    @staticmethod
    def get_categories():
        """Fetches predefined expense categories."""
        cats = query_db("SELECT id, name, description FROM expense_categories ORDER BY id ASC")
        if not cats:
            return ["Food", "Transport", "Education", "Rent", "Shopping", "Entertainment", "Bills", "Other"]
        return [c['name'] for c in cats]

    @staticmethod
    def get_user_expenses(user_id):
        """Retrieves all expense records strictly belonging to the authenticated user."""
        return query_db(
            "SELECT id, user_id, category_id, title, category, amount, date, description, created_at "
            "FROM expenses WHERE user_id = %s ORDER BY date DESC, id DESC",
            (user_id,)
        )

    @staticmethod
    def get_total_expenses(user_id):
        """Calculates total living expenses for the authenticated user."""
        row = query_db(
            "SELECT COALESCE(SUM(amount), 0) as total FROM expenses WHERE user_id = %s",
            (user_id,),
            one=True
        )
        return Decimal(str(row['total'])) if row else Decimal("0.00")

    @staticmethod
    def add_expense(user_id, title, amount, category="Other", date_str=None, description=""):
        """Records an expense transaction linked to category and authenticated user."""
        validate_required_fields({"title": title}, ["title"])
        clean_amount = validate_monetary_amount(amount, field_name="expense amount")
        clean_date = validate_date(str(date_str)) if date_str else None

        # Resolve category_id if available
        cat_row = query_db("SELECT id FROM expense_categories WHERE name = %s", (category,), one=True)
        cat_id = cat_row['id'] if cat_row else None

        return execute_db("""
            INSERT INTO expenses (user_id, category_id, title, category, amount, date, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, cat_id, title.strip(), category, clean_amount, clean_date, description))

    @staticmethod
    def delete_expense(expense_id, user_id):
        """Deletes an expense record strictly verifying user ownership."""
        return execute_db("DELETE FROM expenses WHERE id = %s AND user_id = %s", (expense_id, user_id))
