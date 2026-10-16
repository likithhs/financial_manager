class FinancialCalculator:
    """
    Performs transparent, mathematically sound financial calculations
    used by the AI Financial Adviser.
    """

    @staticmethod
    def monthly_surplus(total_income, total_expenses):
        """
        Money left after expenses in the current month.
        """
        income = float(total_income or 0)
        expenses = float(total_expenses or 0)

        return round(income - expenses, 2)

    @staticmethod
    def savings_rate(total_income, total_expenses):
        """
        Calculates the percentage of income remaining after expenses.
        Returns 0.0 when income is zero or negative.
        """
        income = float(total_income or 0)
        expenses = float(total_expenses or 0)

        if income <= 0:
            return 0.0

        surplus = income - expenses
        return round((surplus / income) * 100, 2)

    @staticmethod
    def expense_ratio(total_income, total_expenses):
        """
        Calculates what percentage of income is being spent.
        Returns 100.0 if expenses > 0 and income <= 0, or 0.0 if both zero.
        """
        income = float(total_income or 0)
        expenses = float(total_expenses or 0)

        if income <= 0:
            return 100.0 if expenses > 0 else 0.0

        return round((expenses / income) * 100, 2)

    @staticmethod
    def required_monthly_saving(target_amount, current_amount, months_remaining):
        """
        Calculates the monthly amount required to reach a goal.
        """
        target = float(target_amount or 0)
        current = float(current_amount or 0)
        months = int(months_remaining or 0)

        remaining = max(0.0, target - current)

        if months <= 0:
            return round(remaining, 2)

        return round(remaining / months, 2)

    @staticmethod
    def goal_progress(target_amount, current_amount):
        """
        Calculates goal completion percentage.
        """
        target = float(target_amount or 0)
        current = float(current_amount or 0)

        if target <= 0:
            return 0.0

        return round(min((current / target) * 100, 100.0), 2)

    @staticmethod
    def budget_utilization(spent, budget):
        """
        Calculates percentage of budget already used.
        """
        spent = float(spent or 0)
        budget = float(budget or 0)

        if budget <= 0:
            return 0.0

        return round((spent / budget) * 100, 2)

    @staticmethod
    def future_investment_value(monthly_investment,
                                months,
                                annual_return_rate=10):
        """
        Estimates future value of regular monthly investments.
        Educational estimate, not a guaranteed return.
        """
        monthly = float(monthly_investment or 0)
        months = int(months or 0)
        annual_rate = float(annual_return_rate or 0)

        if monthly <= 0 or months <= 0:
            return 0.0

        monthly_rate = annual_rate / 100 / 12

        if monthly_rate == 0:
            return round(monthly * months, 2)

        future_value = monthly * (
            ((1 + monthly_rate) ** months - 1)
            / monthly_rate
        )

        return round(future_value, 2)

    @staticmethod
    def emergency_fund_months(emergency_fund, monthly_expenses):
        """
        Estimates how many months of expenses dedicated emergency funds can cover.
        Returns 0.0 if monthly_expenses <= 0 or emergency_fund <= 0, avoiding false precision.
        """
        funds = float(emergency_fund or 0)
        expenses = float(monthly_expenses or 0)

        if expenses <= 0 or funds <= 0:
            return 0.0

        return round(funds / expenses, 2)