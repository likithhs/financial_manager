from datetime import date
from database import query_db
from ai.financial_calculator import FinancialCalculator


class GoalAnalyzer:
    """
    Analyzes a user's financial goals using live database data.
    """

    @staticmethod
    def get_user_goals(user_id):
        return query_db("""
            SELECT *
            FROM financial_goals
            WHERE user_id = %s
            ORDER BY target_date ASC
        """, (user_id,))

    @staticmethod
    def analyze_goal(goal):
        """
        Analyze one financial goal.
        """

        target = float(goal.get('target_amount') or 0)
        current = float(goal.get('current_amount') or 0)

        progress = FinancialCalculator.goal_progress(
            target,
            current
        )

        remaining = max(0, target - current)

        target_date = goal.get('target_date')

        months_remaining = 0

        if target_date:
            if hasattr(target_date, "date"):
                target_date = target_date.date()

            today = date.today()

            months_remaining = max(
                0,
                (target_date.year - today.year) * 12
                + (target_date.month - today.month)
            )

        monthly_required = FinancialCalculator.required_monthly_saving(
            target,
            current,
            months_remaining
        )

        completed = current >= target

        if completed:
            status = "Completed"
        elif months_remaining == 0:
            status = "Due Now"
        elif progress >= 75:
            status = "On Track"
        elif progress >= 40:
            status = "Moderate Progress"
        else:
            status = "Needs Attention"

        return {
            "id": goal.get("id"),
            "name": goal.get("goal_name"),
            "target_amount": target,
            "current_amount": current,
            "remaining": round(remaining, 2),
            "progress_pct": progress,
            "target_date": target_date,
            "months_remaining": months_remaining,
            "monthly_required": monthly_required,
            "priority": goal.get("priority", "Medium"),
            "status": status,
            "completed": completed
        }

    @staticmethod
    def analyze_user_goals(user_id):
        """
        Analyze all goals belonging to the user.
        """

        goals = GoalAnalyzer.get_user_goals(user_id)

        return [
            GoalAnalyzer.analyze_goal(goal)
            for goal in goals
        ]

    @staticmethod
    def get_goal_summary(user_id):
        """
        Returns an overall summary of the user's goals.
        """

        goals = GoalAnalyzer.analyze_user_goals(user_id)

        if not goals:
            return {
                "total_goals": 0,
                "completed": 0,
                "active": 0,
                "goals": []
            }

        completed = sum(
            1 for goal in goals
            if goal["completed"]
        )

        return {
            "total_goals": len(goals),
            "completed": completed,
            "active": len(goals) - completed,
            "goals": goals
        }