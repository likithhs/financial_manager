import json
from decimal import Decimal
from database import query_db, execute_db, transaction_scope
from ai.date_utils import get_calendar_month_range, get_app_current_date
from services.goal_service import is_goal_active, ALL_SUPPORTED_STATUSES, EXCLUDED_GOAL_STATUSES, ACTIVE_GOAL_STATUSES

class FinancialService:
    # -------------------------------------------------------------
    # INCOME MANAGEMENT
    # -------------------------------------------------------------
    @staticmethod
    def get_user_incomes(user_id):
        """Retrieves all lifetime income records for the user ordered by date descending."""
        return query_db("SELECT * FROM incomes WHERE user_id = %s ORDER BY date DESC, id DESC", (user_id,))

    @staticmethod
    def get_user_monthly_incomes(user_id, target_date=None):
        """Retrieves income transactions for the specified calendar month (default: current month)."""
        first_day, last_day = get_calendar_month_range(target_date)
        return query_db("""
            SELECT * FROM incomes 
            WHERE user_id = %s AND date >= %s AND date <= %s 
            ORDER BY date DESC, id DESC
        """, (user_id, first_day.strftime('%Y-%m-%d'), last_day.strftime('%Y-%m-%d')))

    @staticmethod
    def add_income(user_id, source, amount, category="Salary / Wages", date=None, description=""):
        if date is None:
            date = get_app_current_date().strftime('%Y-%m-%d')
        return execute_db("""
            INSERT INTO incomes (user_id, source, amount, category, date, description)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, source.strip(), float(amount), category.strip(), str(date), description.strip()))

    @staticmethod
    def delete_income(income_id, user_id):
        return execute_db("DELETE FROM incomes WHERE id = %s AND user_id = %s", (income_id, user_id))

    # -------------------------------------------------------------
    # EXPENSE MANAGEMENT
    # -------------------------------------------------------------
    @staticmethod
    def get_user_expenses(user_id):
        """Retrieves all lifetime expense records for the user ordered by date descending."""
        return query_db("SELECT * FROM expenses WHERE user_id = %s ORDER BY date DESC, id DESC", (user_id,))

    @staticmethod
    def get_user_monthly_expenses(user_id, target_date=None):
        """Retrieves expense transactions for the specified calendar month (default: current month)."""
        first_day, last_day = get_calendar_month_range(target_date)
        return query_db("""
            SELECT * FROM expenses 
            WHERE user_id = %s AND date >= %s AND date <= %s 
            ORDER BY date DESC, id DESC
        """, (user_id, first_day.strftime('%Y-%m-%d'), last_day.strftime('%Y-%m-%d')))

    @staticmethod
    def add_expense(user_id, title, amount, category="Other", date=None, description=""):
        if date is None:
            date = get_app_current_date().strftime('%Y-%m-%d')
        return execute_db("""
            INSERT INTO expenses (user_id, title, amount, category, date, description)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, title.strip(), float(amount), category.strip(), str(date), description.strip()))

    @staticmethod
    def delete_expense(expense_id, user_id):
        return execute_db("DELETE FROM expenses WHERE id = %s AND user_id = %s", (expense_id, user_id))

    # -------------------------------------------------------------
    # CASHFLOW SUMMARIES (CURRENT MONTH VS LIFETIME)
    # -------------------------------------------------------------
    @staticmethod
    def get_monthly_cashflow_summary(user_id, target_date=None):
        """
        Calculates income, expenses, savings buffer, savings rate, and expense ratio
        strictly filtered to the specified calendar month (default: current month).
        """
        first_day, last_day = get_calendar_month_range(target_date)
        first_str = first_day.strftime('%Y-%m-%d')
        last_str = last_day.strftime('%Y-%m-%d')

        inc_row = query_db("""
            SELECT COALESCE(SUM(amount), 0) AS total 
            FROM incomes 
            WHERE user_id = %s AND date >= %s AND date <= %s
        """, (user_id, first_str, last_str), one=True)
        monthly_income = float(inc_row['total']) if inc_row and inc_row['total'] is not None else 0.0

        exp_row = query_db("""
            SELECT COALESCE(SUM(amount), 0) AS total 
            FROM expenses 
            WHERE user_id = %s AND date >= %s AND date <= %s
        """, (user_id, first_str, last_str), one=True)
        monthly_expenses = float(exp_row['total']) if exp_row and exp_row['total'] is not None else 0.0

        savings = round(monthly_income - monthly_expenses, 2)
        if monthly_income > 0:
            savings_rate = round((savings / monthly_income) * 100, 2)
            expense_ratio = round((monthly_expenses / monthly_income) * 100, 2)
        else:
            savings_rate = 0.0
            expense_ratio = 100.0 if monthly_expenses > 0 else 0.0

        return {
            "month_str": first_day.strftime('%Y-%m'),
            "start_date": first_str,
            "end_date": last_str,
            "income": monthly_income,
            "expenses": monthly_expenses,
            "savings": savings,
            "savings_rate": savings_rate,
            "expense_ratio": expense_ratio
        }

    @staticmethod
    def get_lifetime_cashflow_summary(user_id):
        """Calculates all-time lifetime income, lifetime expenses, and lifetime cash balance."""
        inc_row = query_db("SELECT COALESCE(SUM(amount), 0) AS total FROM incomes WHERE user_id = %s", (user_id,), one=True)
        exp_row = query_db("SELECT COALESCE(SUM(amount), 0) AS total FROM expenses WHERE user_id = %s", (user_id,), one=True)

        lifetime_income = float(inc_row['total']) if inc_row and inc_row['total'] is not None else 0.0
        lifetime_expenses = float(exp_row['total']) if exp_row and exp_row['total'] is not None else 0.0
        lifetime_savings = round(lifetime_income - lifetime_expenses, 2)

        return {
            "total_income": lifetime_income,
            "total_expenses": lifetime_expenses,
            "savings": lifetime_savings
        }

    # -------------------------------------------------------------
    # BUDGET MANAGEMENT
    # -------------------------------------------------------------
    @staticmethod
    def get_user_budget(user_id, month_year):
        return query_db("SELECT * FROM budgets WHERE user_id = %s AND month_year = %s", (user_id, month_year), one=True)

    @staticmethod
    def set_budget(user_id, month_year, total_budget, category_budgets_dict=None):
        cat_json = json.dumps(category_budgets_dict or {})
        existing = FinancialService.get_user_budget(user_id, month_year)
        if existing:
            return execute_db("""
                UPDATE budgets SET total_budget = %s, category_budgets = %s WHERE id = %s
            """, (float(total_budget), cat_json, existing['id']))
        else:
            return execute_db("""
                INSERT INTO budgets (user_id, month_year, total_budget, category_budgets)
                VALUES (%s, %s, %s, %s)
            """, (user_id, month_year, float(total_budget), cat_json))

    @staticmethod
    def get_budget_summary(user_id, month_year):
        budget_row = FinancialService.get_user_budget(user_id, month_year)
        total_budget = float(budget_row['total_budget']) if budget_row else 0.0

        # Expenses strictly in this month using parameterized date boundary
        first_day, last_day = get_calendar_month_range(month_year)
        expenses = query_db("""
            SELECT COALESCE(SUM(amount), 0) as total FROM expenses 
            WHERE user_id = %s AND date >= %s AND date <= %s
        """, (user_id, first_day.strftime('%Y-%m-%d'), last_day.strftime('%Y-%m-%d')), one=True)
        spent = float(expenses['total']) if expenses and expenses['total'] is not None else 0.0

        utilization = round((spent / total_budget * 100), 1) if total_budget > 0 else 0.0
        is_overbudget = spent > total_budget if total_budget > 0 else False
        remaining = max(0.0, total_budget - spent)

        return {
            "month_year": month_year,
            "total_budget": total_budget,
            "spent": spent,
            "remaining": remaining,
            "utilization": utilization,
            "is_overbudget": is_overbudget
        }

    # -------------------------------------------------------------
    # FINANCIAL GOALS MANAGEMENT
    # -------------------------------------------------------------
    @staticmethod
    def get_user_goals(user_id):
        goals = query_db("SELECT * FROM financial_goals WHERE user_id = %s ORDER BY target_date ASC", (user_id,))
        formatted = []
        for g in goals:
            target = float(g['target_amount'])
            curr = float(g.get('current_amount') if g.get('current_amount') is not None else (g.get('current_savings') or 0.0))
            progress_pct = min(100.0, round((curr / target * 100), 1)) if target > 0 else 0.0
            remaining = max(0.0, round(target - curr, 2))
            status_str = str(g.get('status') or 'In Progress').strip()
            is_completed = (curr >= target and target > 0) or status_str.lower() == 'completed'
            is_active = is_goal_active(status_str, curr, target)

            formatted.append({
                **g,
                "name": g.get('name') or g.get('goal_name'),
                "target_amount": target,
                "current_amount": curr,
                "progress_pct": progress_pct,
                "remaining": remaining,
                "is_completed": is_completed,
                "is_active": is_active,
                "status": status_str
            })
        return formatted

    @staticmethod
    def add_goal(user_id, name, target_amount, initial_amount=0.0, target_date=None, priority="Medium", description="", status="In Progress"):
        if target_date is None:
            target_date = get_app_current_date().strftime('%Y-%m-%d')
        target_val = float(target_amount)
        init_val = float(initial_amount or 0.0)
        clean_status = status.strip() if status and status.strip() in ALL_SUPPORTED_STATUSES else "In Progress"
        if target_val > 0 and init_val >= target_val:
            clean_status = "Completed"

        with transaction_scope() as tx:
            goal_id = tx.execute("""
                INSERT INTO financial_goals (user_id, name, goal_name, target_amount, current_amount, current_savings, target_date, priority, description, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, name.strip(), name.strip(), target_val, init_val, init_val, str(target_date), priority, description.strip(), clean_status))

            if init_val > 0.0:
                tx.execute("""
                    INSERT INTO goal_contributions (goal_id, user_id, amount, contribution_date, description)
                    VALUES (%s, %s, %s, %s, %s)
                """, (goal_id, user_id, init_val, str(target_date), "Initial deposit"))

            return goal_id

    @staticmethod
    def update_goal_status(goal_id, user_id, new_status):
        """Updates goal status preserving supported lifecycle states."""
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
    def add_funds_to_goal(goal_id, user_id, added_amount, description="Accumulated contribution"):
        """
        CUMULATIVE GOAL UPDATE:
        Atomically updates goal balance and records contribution history.
        If current = 5000 and added = 2000, new current = 7000.
        Never replaces old amount.
        Transitions to Completed if target reached; otherwise preserves existing active/paused status.
        """
        added_val = float(added_amount)
        if added_val <= 0:
            return False

        with transaction_scope() as tx:
            goal = tx.query("SELECT * FROM financial_goals WHERE id = %s AND user_id = %s", (goal_id, user_id), one=True)
            if not goal:
                return False
            
            current = float(goal.get('current_amount') if goal.get('current_amount') is not None else (goal.get('current_savings') or 0.0))
            target = float(goal['target_amount'])
            new_total = current + added_val
            
            current_status = str(goal.get('status') or 'In Progress').strip()
            if new_total >= target and target > 0:
                status = "Completed"
            else:
                if current_status.lower() in EXCLUDED_GOAL_STATUSES and current_status.lower() != 'completed':
                    status = current_status
                else:
                    status = current_status if current_status.lower() in ACTIVE_GOAL_STATUSES else "In Progress"

            tx.execute("""
                INSERT INTO goal_contributions (goal_id, user_id, amount, contribution_date, description)
                VALUES (%s, %s, %s, %s, %s)
            """, (goal_id, user_id, added_val, get_app_current_date().strftime('%Y-%m-%d'), description))

            tx.execute("""
                UPDATE financial_goals 
                SET current_amount = %s, current_savings = %s, status = %s
                WHERE id = %s AND user_id = %s
            """, (new_total, new_total, status, goal_id, user_id))

            return True

    @staticmethod
    def delete_goal(goal_id, user_id):
        return execute_db("DELETE FROM financial_goals WHERE id = %s AND user_id = %s", (goal_id, user_id))
