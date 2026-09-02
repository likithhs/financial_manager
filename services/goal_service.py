"""
FinAI Backend Foundation - Financial Goal Service
Handles goal milestones, accumulated contributions, and progress tracking.
"""

from decimal import Decimal
from datetime import date
from database import query_db, execute_db
from services.validators import validate_monetary_amount, validate_date, validate_required_fields


class GoalService:
    @staticmethod
    def get_user_goals(user_id):
        """Retrieves all goals belonging to user with computed progress metrics."""
        goals = query_db(
            "SELECT id, user_id, COALESCE(name, goal_name) as name, target_amount, "
            "COALESCE(current_amount, current_savings, 0.00) as current_amount, "
            "target_date, priority, status, description, created_at "
            "FROM financial_goals WHERE user_id = %s ORDER BY id DESC",
            (user_id,)
        )
        for g in goals:
            target = Decimal(str(g['target_amount']))
            curr = Decimal(str(g['current_amount']))
            g['target_amount'] = float(target)
            g['current_amount'] = float(curr)
            g['progress_pct'] = min(round((curr / target * 100), 1), 100.0) if target > 0 else 0.0
            g['remaining'] = float(max(target - curr, Decimal("0.00")))
            g['is_completed'] = curr >= target
        return goals

    @staticmethod
    def create_goal(user_id, name, target_amount, initial_savings=0.00, target_date_str=None, priority="Medium", description=""):
        """Initializes a new financial goal."""
        validate_required_fields({"name": name}, ["name"])
        clean_target = validate_monetary_amount(target_amount, min_val=100.00, field_name="target amount")
        clean_initial = validate_monetary_amount(initial_savings, min_val=0.00, field_name="initial savings") if initial_savings else Decimal("0.00")
        clean_date = validate_date(str(target_date_str)) if target_date_str else date.today()

        goal_id = execute_db("""
            INSERT INTO financial_goals (user_id, name, goal_name, target_amount, current_amount, current_savings, target_date, priority, status, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'In Progress', %s)
        """, (user_id, name.strip(), name.strip(), clean_target, clean_initial, clean_initial, clean_date, priority, description))

        if clean_initial > Decimal("0.00"):
            execute_db("""
                INSERT INTO goal_contributions (goal_id, user_id, amount, contribution_date, description)
                VALUES (%s, %s, %s, %s, %s)
            """, (goal_id, user_id, clean_initial, clean_date, "Initial deposit"))

        return goal_id

    @staticmethod
    def add_contribution(goal_id, user_id, amount, description="Accumulated contribution"):
        """
        Adds a cumulative deposit towards a goal.
        Preserves deposit audit record in goal_contributions and updates accumulated goal balance.
        """
        clean_amount = validate_monetary_amount(amount, min_val=1.00, field_name="contribution amount")

        # Verify user ownership
        goal = query_db("SELECT id, target_amount, current_amount FROM financial_goals WHERE id = %s AND user_id = %s", (goal_id, user_id), one=True)
        if not goal:
            return False

        # Record contribution history
        execute_db("""
            INSERT INTO goal_contributions (goal_id, user_id, amount, contribution_date, description)
            VALUES (%s, %s, %s, %s, %s)
        """, (goal_id, user_id, clean_amount, date.today(), description))

        # Update accumulated balance
        new_amount = Decimal(str(goal['current_amount'])) + clean_amount
        target = Decimal(str(goal['target_amount']))
        new_status = 'Completed' if new_amount >= target else 'In Progress'

        execute_db("""
            UPDATE financial_goals
            SET current_amount = %s, current_savings = %s, status = %s
            WHERE id = %s AND user_id = %s
        """, (new_amount, new_amount, new_status, goal_id, user_id))

        return True

    @staticmethod
    def delete_goal(goal_id, user_id):
        """Deletes a goal verifying user ownership."""
        return execute_db("DELETE FROM financial_goals WHERE id = %s AND user_id = %s", (goal_id, user_id))
