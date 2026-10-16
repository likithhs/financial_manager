from database import query_db, execute_db
from ai.financial_health import calculate_financial_health
from ai.date_utils import get_calendar_month_range, get_app_current_date
from services.goal_service import count_active_goals


def get_user_monthly_expense_basis(user_id, end_date_str=None):
    """
    Determines the monthly expense basis (burn rate) for runway calculations.
    Uses up to the last 3 distinct historical months of expenses.
    Returns: (monthly_expense_basis: float, has_sufficient_history: bool)
    """
    if end_date_str is None:
        end_date_str = get_app_current_date().strftime('%Y-%m-%d')

    rows = query_db("""
        SELECT SUBSTR(date, 1, 7) as exp_month, COALESCE(SUM(amount), 0) as month_total
        FROM expenses
        WHERE user_id = %s AND date <= %s
        GROUP BY SUBSTR(date, 1, 7)
        ORDER BY exp_month DESC
        LIMIT 3
    """, (user_id, end_date_str))

    if not rows:
        return 0.0, False

    totals = [float(r['month_total']) for r in rows if r['month_total'] is not None and float(r['month_total']) > 0]
    if not totals:
        return 0.0, False

    if len(totals) >= 2:
        avg_expenses = round(sum(totals) / len(totals), 2)
        return avg_expenses, True
    else:
        # Only single month of data exists: mark as limited history
        return totals[0], False


def evaluate_user_financial_health(user_id, target_date=None):
    """
    Fetches financial data for a user strictly filtered by current calendar month
    (or the specified target_date month), computes objective health metrics,
    persists the analysis in the database, and returns complete diagnostic telemetry.
    """
    start_date, end_date = get_calendar_month_range(target_date)
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    month_str = start_date.strftime('%Y-%m')

    # ---------------------------------------------------------
    # 1. MONTHLY INCOME (CURRENT CALENDAR MONTH)
    # ---------------------------------------------------------
    income_row = query_db(
        """
        SELECT COALESCE(SUM(amount), 0) AS total
        FROM incomes
        WHERE user_id = %s
          AND date >= %s AND date <= %s
        """,
        (user_id, start_str, end_str),
        one=True
    )

    monthly_income = (
        float(income_row["total"])
        if income_row and income_row["total"] is not None
        else 0.0
    )

    # ---------------------------------------------------------
    # 2. MONTHLY EXPENSES (CURRENT CALENDAR MONTH)
    # ---------------------------------------------------------
    expense_row = query_db(
        """
        SELECT COALESCE(SUM(amount), 0) AS total
        FROM expenses
        WHERE user_id = %s
          AND date >= %s AND date <= %s
        """,
        (user_id, start_str, end_str),
        one=True
    )

    monthly_expenses = (
        float(expense_row["total"])
        if expense_row and expense_row["total"] is not None
        else 0.0
    )

    # ---------------------------------------------------------
    # 3. EMERGENCY FUND (DEDICATED ALLOCATION ONLY)
    # ---------------------------------------------------------
    # Distinguish explicit emergency reserve from unallocated general cash
    emergency_goal = query_db(
        """
        SELECT id, name, goal_name,
               COALESCE(current_amount, current_savings, 0.0) as current_amount,
               target_amount, status
        FROM financial_goals
        WHERE user_id = %s
          AND (
              LOWER(COALESCE(name, '')) LIKE %s
              OR LOWER(COALESCE(goal_name, '')) LIKE %s
              OR LOWER(COALESCE(name, '')) LIKE %s
              OR LOWER(COALESCE(goal_name, '')) LIKE %s
          )
          AND LOWER(TRIM(status)) NOT IN ('cancelled', 'canceled', 'archived')
        ORDER BY current_amount DESC
        LIMIT 1
        """,
        (
            user_id,
            "%emergency%",
            "%emergency%",
            "%safety%",
            "%safety%"
        ),
        one=True
    )

    if emergency_goal:
        emergency_fund = float(emergency_goal["current_amount"] or 0.0)
        emergency_fund_configured = True
    else:
        emergency_fund = 0.0
        emergency_fund_configured = False

    # ---------------------------------------------------------
    # 4. MONTHLY EXPENSE BASIS & RUNWAY
    # ---------------------------------------------------------
    monthly_expense_basis, has_sufficient_history = get_user_monthly_expense_basis(user_id, end_str)
    # If historical calculation returned 0.0 but current month has expenses, fallback to current month
    if monthly_expense_basis <= 0.0 and monthly_expenses > 0.0:
        monthly_expense_basis = monthly_expenses
        has_sufficient_history = False

    # ---------------------------------------------------------
    # 5. TOTAL ACTIVE BUDGET FOR CURRENT MONTH
    # ---------------------------------------------------------
    budget_row = query_db(
        """
        SELECT total_budget
        FROM budgets
        WHERE user_id = %s AND month_year = %s
        LIMIT 1
        """,
        (user_id, month_str),
        one=True
    )

    if not budget_row:
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
        if budget_row and budget_row["total_budget"] is not None
        else 0.0
    )

    # ---------------------------------------------------------
    # 6. ACTIVE GOALS COUNT (STANDARDIZED STATUS FILTERING)
    # ---------------------------------------------------------
    # Unfinished goals in supported active statuses ('Active', 'In Progress')
    # Excludes 'Completed', 'Cancelled', 'Archived', 'Paused'
    goals_rows = query_db(
        """
        SELECT id, status,
               COALESCE(current_amount, current_savings, 0.0) as current_amount,
               target_amount
        FROM financial_goals
        WHERE user_id = %s
        """,
        (user_id,)
    )

    active_goals_count = count_active_goals(goals_rows) if goals_rows else 0

    # ---------------------------------------------------------
    # 7. CALCULATE FINANCIAL HEALTH
    # ---------------------------------------------------------
    health_data = calculate_financial_health(
        total_income=monthly_income,
        total_expenses=monthly_expenses,
        emergency_fund=emergency_fund,
        total_budget=total_budget,
        active_goals_count=active_goals_count,
        emergency_fund_configured=emergency_fund_configured,
        monthly_expense_basis=monthly_expense_basis,
        has_sufficient_expense_history=has_sufficient_history
    )

    # Add calendar month telemetry
    health_data["calendar_month"] = month_str
    health_data["month_start"] = start_str
    health_data["month_end"] = end_str

    # ---------------------------------------------------------
    # 8. CHECK IF FINANCIAL ANALYSIS ALREADY EXISTS
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
    # 9. UPDATE EXISTING ANALYSIS
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
    # 10. INSERT NEW ANALYSIS
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
    # 11. RETURN RESULT
    # ---------------------------------------------------------
    return health_data