"""
FinAI Backend Foundation - Financial Goal Service
Handles goal milestones, accumulated contributions, status management, and progress tracking.
"""

from decimal import Decimal
from datetime import date
from database import query_db, execute_db, transaction_scope
from services.validators import validate_monetary_amount, validate_date, validate_required_fields

ACTIVE_GOAL_STATUSES = {'active', 'in progress', 'in_progress'}
EXCLUDED_GOAL_STATUSES = {'completed', 'cancelled', 'canceled', 'archived', 'paused'}
ALL_SUPPORTED_STATUSES = ['In Progress', 'Active', 'Completed', 'Paused', 'Cancelled', 'Archived']


def is_goal_active(status, current_amount=0.0, target_amount=0.0):
    """
    Determines whether a financial goal is an active qualifying goal.
    - True for unfinished goals with supported active statuses: 'Active', 'In Progress'.
    - False for 'Completed', or if current_amount >= target_amount (when target > 0).
    - False for non-qualifying statuses: 'Cancelled', 'Archived', 'Paused'.
    """
    norm_status = str(status or '').strip().lower()
    if norm_status in EXCLUDED_GOAL_STATUSES:
        return False
    if norm_status not in ACTIVE_GOAL_STATUSES:
        return False
    target = float(target_amount or 0.0)
    curr = float(current_amount or 0.0)
    if target > 0 and curr >= target:
        return False
    return True


def count_active_goals(goals):
    """
    Counts unfinished active qualifying goals from a list of goal dictionaries.
    """
    count = 0
    for g in goals:
        status = g.get('status')
        curr = g.get('current_amount', 0.0)
        target = g.get('target_amount', 0.0)
        if is_goal_active(status, curr, target):
            count += 1
    return count


class GoalService:
    @staticmethod
    def get_user_goals(user_id):
        """Retrieves all goals belonging to user with computed progress metrics and status."""
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
            status_str = str(g.get('status') or 'In Progress').strip()
            status_norm = status_str.lower()

            g['target_amount'] = float(target)
            g['current_amount'] = float(curr)
            g['progress_pct'] = min(round((curr / target * 100), 1), 100.0) if target > 0 else 0.0
            g['remaining'] = float(max(target - curr, Decimal("0.00")))
            g['is_completed'] = (curr >= target and target > Decimal("0.00")) or status_norm == 'completed'
            g['is_active'] = is_goal_active(status_str, curr, target)
        return goals

    @staticmethod
    def create_goal(user_id, name, target_amount, initial_savings=0.00, target_date_str=None, priority="Medium", description="", status="In Progress"):
        """Initializes a new financial goal with supported status within an atomic transaction."""
        validate_required_fields({"name": name}, ["name"])
        clean_target = validate_monetary_amount(target_amount, min_val=100.00, field_name="target amount")
        clean_initial = validate_monetary_amount(initial_savings, min_val=0.00, field_name="initial savings") if initial_savings else Decimal("0.00")
        clean_date = validate_date(str(target_date_str)) if target_date_str else date.today()

        # Validate initial status
        clean_status = status.strip() if status and status.strip() in ALL_SUPPORTED_STATUSES else "In Progress"
        if clean_initial >= clean_target:
            clean_status = "Completed"

        with transaction_scope() as tx:
            goal_id = tx.execute("""
                INSERT INTO financial_goals (user_id, name, goal_name, target_amount, current_amount, current_savings, target_date, priority, status, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, name.strip(), name.strip(), clean_target, clean_initial, clean_initial, clean_date, priority, clean_status, description))

            if clean_initial > Decimal("0.00"):
                tx.execute("""
                    INSERT INTO goal_contributions (goal_id, user_id, amount, contribution_date, description)
                    VALUES (%s, %s, %s, %s, %s)
                """, (goal_id, user_id, clean_initial, clean_date, "Initial deposit"))

            return goal_id

    @staticmethod
    def update_goal_status(goal_id, user_id, new_status):
        """
        Updates a goal status ensuring valid supported lifecycle state:
        'In Progress', 'Active', 'Completed', 'Paused', 'Cancelled', 'Archived'.
        """
        normalized = new_status.strip().title() if new_status else "In Progress"
        status_map = {s.lower(): s for s in ALL_SUPPORTED_STATUSES}
        matched_status = status_map.get(normalized.lower())
        if not matched_status:
            return False

        return execute_db("""
            UPDATE financial_goals
            SET status = %s
            WHERE id = %s AND user_id = %s
        """, (matched_status, goal_id, user_id))

    @staticmethod
    def add_contribution(goal_id, user_id, amount, description="Accumulated contribution"):
        """
        Adds a cumulative deposit towards a goal atomically.
        Preserves deposit audit record in goal_contributions and updates accumulated goal balance.
        Transitions to 'Completed' when target reached; otherwise preserves existing active/paused status.
        """
        clean_amount = validate_monetary_amount(amount, min_val=1.00, field_name="contribution amount")

        with transaction_scope() as tx:
            # Verify user ownership within the transaction
            goal = tx.query("SELECT id, target_amount, current_amount, status FROM financial_goals WHERE id = %s AND user_id = %s", (goal_id, user_id), one=True)
            if not goal:
                return False

            # Record contribution history
            tx.execute("""
                INSERT INTO goal_contributions (goal_id, user_id, amount, contribution_date, description)
                VALUES (%s, %s, %s, %s, %s)
            """, (goal_id, user_id, clean_amount, date.today(), description))

            # Update accumulated balance
            new_amount = Decimal(str(goal['current_amount'])) + clean_amount
            target = Decimal(str(goal['target_amount']))
            
            current_status = str(goal.get('status') or 'In Progress').strip()
            if new_amount >= target:
                new_status = 'Completed'
            else:
                # If goal was paused, cancelled, or archived, preserve that status
                if current_status.lower() in EXCLUDED_GOAL_STATUSES and current_status.lower() != 'completed':
                    new_status = current_status
                else:
                    new_status = current_status if current_status.lower() in ACTIVE_GOAL_STATUSES else 'In Progress'

            tx.execute("""
                UPDATE financial_goals
                SET current_amount = %s, current_savings = %s, status = %s
                WHERE id = %s AND user_id = %s
            """, (new_amount, new_amount, new_status, goal_id, user_id))

            return True

    @staticmethod
    def delete_goal(goal_id, user_id):
        """Deletes a goal verifying user ownership."""
        return execute_db("DELETE FROM financial_goals WHERE id = %s AND user_id = %s", (goal_id, user_id))
