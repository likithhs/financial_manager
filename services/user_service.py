"""
FinAI Backend Foundation - User Service
Handles user account lookups, profile data, and credential verification foundation.
"""

from database import query_db, execute_db
from werkzeug.security import generate_password_hash, check_password_hash
from services.validators import validate_email, validate_password, validate_required_fields, ValidationError


class UserService:
    @staticmethod
    def get_by_id(user_id):
        """Fetches user record by ID (excluding password hash)."""
        return query_db(
            "SELECT id, name, email, role, age, occupation, financial_exp, investment_exp, created_at, updated_at "
            "FROM users WHERE id = %s",
            (user_id,),
            one=True
        )

    @staticmethod
    def get_by_email(email):
        """Fetches user record by normalized email."""
        clean_email = validate_email(email)
        return query_db("SELECT * FROM users WHERE email = %s", (clean_email,), one=True)

    @staticmethod
    def get_financial_profile(user_id):
        """Fetches user financial profile or returns an empty default structure."""
        profile = query_db("SELECT * FROM financial_profiles WHERE user_id = %s", (user_id,), one=True)
        if not profile:
            return {
                "user_id": user_id,
                "monthly_income": 0.00,
                "fixed_expenses": 0.00,
                "variable_expenses": 0.00,
                "existing_savings": 0.00,
                "loan_emi": 0.00,
                "investment_experience": "Beginner",
                "risk_tolerance": "medium"
            }
        return profile

    @staticmethod
    def update_profile(user_id, name, age=25, occupation="Student / Professional", financial_exp="Beginner", investment_exp="None"):
        """Updates user profile baseline details."""
        return execute_db("""
            UPDATE users
            SET name = %s, age = %s, occupation = %s, financial_exp = %s, investment_exp = %s
            WHERE id = %s
        """, (name, age, occupation, financial_exp, investment_exp, user_id))

    @staticmethod
    def update_password(user_id, new_password):
        """Updates user password using cryptographically secure hashing."""
        validate_password(new_password)
        pwd_hash = generate_password_hash(new_password)
        return execute_db("""
            UPDATE users
            SET password = %s, password_hash = %s
            WHERE id = %s
        """, (pwd_hash, pwd_hash, user_id))
