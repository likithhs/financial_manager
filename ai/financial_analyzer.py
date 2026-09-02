
from database import query_db, execute_db
from ai.financial_health import calculate_financial_health


def evaluate_user_financial_health(user_id):
    """
    Fetches all financial data for a user,
    evaluates financial health,
    saves the evaluation in the database,
    and returns the result.
    """

    # ---------------------------------------------------------
    # 1. TOTAL INCOME
    # ---------------------------------------------------------
    income_row = query_db(
        """
        SELECT SUM(amount) AS total
        FROM incomes
        WHERE user_id = %s
        """,
        (user_id,),
        one=True
    )

    total_income = (
        float(income_row["total"])
        if income_row and income_row["total"] is not None
        else 0.0
    )

    # ---------------------------------------------------------
    # 2. TOTAL EXPENSES
    # ---------------------------------------------------------
    expense_row = query_db(
        """
        SELECT SUM(amount) AS total
        FROM expenses
        WHERE user_id = %s
        """,
        (user_id,),
        one=True
    )

    total_expenses = (
        float(expense_row["total"])
        if expense_row and expense_row["total"] is not None
        else 0.0
    )

    # ---------------------------------------------------------
    # 3. EMERGENCY FUND
    # ---------------------------------------------------------
    # financial_goals uses goal_name, NOT name
    emergency_goal = query_db(
        """
        SELECT current_amount
        FROM financial_goals
        WHERE user_id = %s
        AND (
            LOWER(goal_name) LIKE %s
            OR LOWER(goal_name) LIKE %s
        )
        ORDER BY current_amount DESC
        LIMIT 1
        """,
        (
            user_id,
            "%emergency%",
            "%safety%"
        ),
        one=True
    )

    emergency_fund = (
        float(emergency_goal["current_amount"])
        if emergency_goal
        and emergency_goal["current_amount"] is not None
        else 0.0
    )

    # ---------------------------------------------------------
    # 4. TOTAL ACTIVE BUDGET
    # ---------------------------------------------------------
    budget_row = query_db(
        """
        SELECT total_budget
        FROM budgets
        WHERE user_id = %s
        ORDER BY id DESC
        LIMIT 1
        """,
        (user_id,),
        one=True
    )

    total_budget = (
        float(budget_row["total_budget"])
        if budget_row
        and budget_row["total_budget"] is not None
        else 0.0
    )

    # ---------------------------------------------------------
    # 5. ACTIVE GOALS COUNT
    # ---------------------------------------------------------
    goals_row = query_db(
        """
        SELECT COUNT(*) AS count
        FROM financial_goals
        WHERE user_id = %s
        AND status = %s
        """,
        (
            user_id,
            "Active"
        ),
        one=True
    )

    active_goals_count = (
        int(goals_row["count"])
        if goals_row
        else 0
    )

    # ---------------------------------------------------------
    # 6. CALCULATE FINANCIAL HEALTH
    # ---------------------------------------------------------
    health_data = calculate_financial_health(
        total_income=total_income,
        total_expenses=total_expenses,
        emergency_fund=emergency_fund,
        total_budget=total_budget,
        active_goals_count=active_goals_count
    )

    # ---------------------------------------------------------
    # 7. CHECK IF FINANCIAL ANALYSIS ALREADY EXISTS
    # ---------------------------------------------------------
    existing = query_db(
        """
        SELECT id
        FROM financial_analysis
        WHERE user_id = %s
        """,
        (user_id,),
        one=True
    )

    # ---------------------------------------------------------
    # 8. UPDATE EXISTING ANALYSIS
    # ---------------------------------------------------------
    if existing:

        execute_db(
            """
            UPDATE financial_analysis
            SET
                total_income = %s,
                total_expenses = %s,
                savings = %s,
                savings_rate = %s,
                expense_ratio = %s,
                emergency_fund_ratio = %s,
                health_score = %s,
                health_status = %s,
                explanation = %s,
                evaluated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (
                health_data["total_income"],
                health_data["total_expenses"],
                health_data["savings"],
                health_data["savings_rate"],
                health_data["expense_ratio"],
                health_data["emergency_fund_ratio"],
                health_data["score"],
                health_data["health_status"],
                health_data["explanation"],
                existing["id"]
            )
        )

    # ---------------------------------------------------------
    # 9. INSERT NEW ANALYSIS
    # ---------------------------------------------------------
    else:

        execute_db(
            """
            INSERT INTO financial_analysis
            (
                user_id,
                total_income,
                total_expenses,
                savings,
                savings_rate,
                expense_ratio,
                emergency_fund_ratio,
                health_score,
                health_status,
                explanation
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                user_id,
                health_data["total_income"],
                health_data["total_expenses"],
                health_data["savings"],
                health_data["savings_rate"],
                health_data["expense_ratio"],
                health_data["emergency_fund_ratio"],
                health_data["score"],
                health_data["health_status"],
                health_data["explanation"]
            )
        )

    # ---------------------------------------------------------
    # 10. RETURN RESULT
    # ---------------------------------------------------------
    return health_data