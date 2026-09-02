import json
from database import query_db, execute_db

class FinancialService:
    # -------------------------------------------------------------
    # INCOME MANAGEMENT
    # -------------------------------------------------------------
    @staticmethod
    def get_user_incomes(user_id):
        return query_db("SELECT * FROM incomes WHERE user_id = %s ORDER BY date DESC, id DESC", (user_id,))

    @staticmethod
    def add_income(user_id, source, amount, category, date, description=""):
        return execute_db("""
            INSERT INTO incomes (user_id, source, amount, category, date, description)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, source.strip(), float(amount), category.strip(), date, description.strip()))

    @staticmethod
    def delete_income(income_id, user_id):
        return execute_db("DELETE FROM incomes WHERE id = %s AND user_id = %s", (income_id, user_id))

    # -------------------------------------------------------------
    # EXPENSE MANAGEMENT
    # -------------------------------------------------------------
    @staticmethod
    def get_user_expenses(user_id):
        return query_db("SELECT * FROM expenses WHERE user_id = %s ORDER BY date DESC, id DESC", (user_id,))

    @staticmethod
    def add_expense(user_id, title, amount, category, date, description=""):
        return execute_db("""
            INSERT INTO expenses (user_id, title, amount, category, date, description)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, title.strip(), float(amount), category.strip(), date, description.strip()))

    @staticmethod
    def delete_expense(expense_id, user_id):
        return execute_db("DELETE FROM expenses WHERE id = %s AND user_id = %s", (expense_id, user_id))

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

        # Expenses in this month (date format: YYYY-MM-DD)
        expenses = query_db("""
            SELECT SUM(amount) as total FROM expenses 
            WHERE user_id = %s AND date LIKE %s
        """, (user_id, f"{month_year}%"), one=True)
        spent = float(expenses['total']) if expenses and expenses['total'] else 0.0

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
            curr = float(g['current_amount'])
            progress_pct = min(100.0, round((curr / target * 100), 1)) if target > 0 else 0.0
            remaining = max(0.0, round(target - curr, 2))
            is_completed = curr >= target
            formatted.append({
                **g,
                "target_amount": target,
                "current_amount": curr,
                "progress_pct": progress_pct,
                "remaining": remaining,
                "is_completed": is_completed
            })
        return formatted

    @staticmethod
    def add_goal(user_id, name, target_amount, initial_amount, target_date, priority="Medium", description=""):
        return execute_db("""
            INSERT INTO financial_goals (user_id, name, target_amount, current_amount, target_date, priority, description, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'In Progress')
        """, (user_id, name.strip(), float(target_amount), float(initial_amount or 0.0), target_date, priority, description.strip()))

    @staticmethod
    def add_funds_to_goal(goal_id, user_id, added_amount):
        """
        CUMULATIVE GOAL UPDATE:
        If current = 5000 and added = 2000, new current = 7000.
        Never replaces old amount.
        """
        goal = query_db("SELECT * FROM financial_goals WHERE id = %s AND user_id = %s", (goal_id, user_id), one=True)
        if not goal:
            return False
        
        current = float(goal['current_amount'])
        target = float(goal['target_amount'])
        new_total = current + float(added_amount)
        status = "Completed" if new_total >= target else "In Progress"

        return execute_db("""
            UPDATE financial_goals 
            SET current_amount = %s, status = %s
            WHERE id = %s AND user_id = %s
        """, (new_total, status, goal_id, user_id))

    @staticmethod
    def delete_goal(goal_id, user_id):
        return execute_db("DELETE FROM financial_goals WHERE id = %s AND user_id = %s", (goal_id, user_id))
