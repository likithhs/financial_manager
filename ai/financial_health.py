def calculate_financial_health(
    total_income,
    total_expenses,
    emergency_fund=0.0,
    total_budget=0.0,
    active_goals_count=0,
    emergency_fund_configured=None,
    monthly_expense_basis=None,
    has_sufficient_expense_history=True
):
    """
    Evaluates personal financial health based on monthly income, monthly expenses,
    savings rate, budget discipline, emergency runway, and goal planning.

    Parameters:
    - total_income (float): Current calendar month's total recorded income.
    - total_expenses (float): Current calendar month's total recorded expenses.
    - emergency_fund (float): Funds explicitly allocated to emergency/safety reserves.
    - total_budget (float): Active monthly budget target.
    - active_goals_count (int): Count of unfinished qualifying active goals.
    - emergency_fund_configured (bool or None): Explicit flag indicating whether the user
      has designated an emergency fund. If None, infers from emergency_fund > 0.
    - monthly_expense_basis (float or None): Monthly burn rate basis (e.g. 3-month rolling average).
      If None, defaults to current month's expenses.
    - has_sufficient_expense_history (bool): Whether historical expense basis is reliable.

    Returns:
    A telemetry dictionary containing score (0-100), health_status, metrics,
    emergency fund configuration state, runway status, and clear diagnostic explanations.
    """
    total_income = float(total_income or 0.0)
    total_expenses = float(total_expenses or 0.0)
    emergency_fund = float(emergency_fund or 0.0)
    total_budget = float(total_budget or 0.0)
    active_goals_count = int(active_goals_count or 0)

    # Resolve explicit emergency fund configuration state
    # Never treat general savings as an emergency fund
    if emergency_fund_configured is None:
        emergency_fund_configured = (emergency_fund > 0.0)

    # 1. Monthly Savings & Ratios
    savings = round(total_income - total_expenses, 2)

    if total_income > 0:
        savings_rate = round((savings / total_income) * 100, 2)
        expense_ratio = round((total_expenses / total_income) * 100, 2)
    else:
        savings_rate = 0.0
        expense_ratio = 100.0 if total_expenses > 0 else 0.0

    # 2. Emergency Fund Ratio & Runway (Months of Expenses Covered)
    # Determine monthly expense basis (burn rate)
    if monthly_expense_basis is not None:
        burn_basis = float(monthly_expense_basis)
    else:
        burn_basis = total_expenses

    if not emergency_fund_configured:
        emergency_fund_ratio = 0.0
        emergency_fund_status = "Not Configured"
        runway_label = "Emergency fund not configured"
    elif burn_basis <= 0:
        emergency_fund_ratio = 0.0
        emergency_fund_status = "Insufficient Expense Data"
        runway_label = "Insufficient historical expense data to compute runway"
    else:
        # Avoid division by zero, negative, or misleading runway
        emergency_fund_ratio = round(max(0.0, emergency_fund) / burn_basis, 2)
        if emergency_fund_ratio >= 6.0:
            emergency_fund_status = "Strong"
        elif emergency_fund_ratio >= 3.0:
            emergency_fund_status = "Adequate"
        elif emergency_fund_ratio >= 1.0:
            emergency_fund_status = "Minimal"
        else:
            emergency_fund_status = "Underdeveloped"

        if not has_sufficient_expense_history:
            runway_label = f"Estimated: {emergency_fund_ratio} months (limited expense history)"
        else:
            runway_label = f"{emergency_fund_ratio} months"

    # 3. Scoring Breakdown (Total: 100 pts)
    score = 0
    factors = []

    # Factor A: Savings Rate (Max 35 pts)
    if total_income <= 0:
        score += 0
        factors.append("No active recorded income for the current calendar month.")
    elif savings_rate >= 35:
        score += 35
        factors.append(f"Outstanding savings rate of {savings_rate}% (target: >30%).")
    elif savings_rate >= 20:
        score += 28
        factors.append(f"Healthy savings rate of {savings_rate}% (well above standard 20%).")
    elif savings_rate >= 10:
        score += 18
        factors.append(f"Modest savings rate of {savings_rate}%. Room for optimization.")
    elif savings_rate > 0:
        score += 8
        factors.append(f"Low positive savings rate of {savings_rate}%. Spending consumes most income.")
    else:
        score += 0
        factors.append(f"Negative savings rate ({savings_rate}%). Expenses exceed income.")

    # Factor B: Expense Ratio (Max 25 pts)
    if total_income > 0:
        if expense_ratio <= 50:
            score += 25
            factors.append(f"Optimal expense control: expenses consume only {expense_ratio}% of earnings.")
        elif expense_ratio <= 70:
            score += 20
            factors.append(f"Balanced living costs: expenses consume {expense_ratio}% of income.")
        elif expense_ratio <= 85:
            score += 12
            factors.append(f"Elevated living costs: {expense_ratio}% of income is spent.")
        else:
            score += 4
            factors.append(f"High expense strain: {expense_ratio}% of earnings goes toward expenditures.")
    else:
        score += 0
        if total_expenses > 0:
            factors.append(f"Living expenses recorded (₹{total_expenses:,.2f}) without active income.")
        else:
            factors.append("No recorded living expenses or income for the current month.")

    # Factor C: Emergency Runway (Max 25 pts)
    # Strictly evaluates explicit emergency reserve; never credits unallocated general cash
    if not emergency_fund_configured:
        score += 0
        factors.append("Emergency fund has not been configured. Dedicated safety net is unestablished.")
    elif burn_basis <= 0:
        # Emergency reserve exists, but no expense basis is available to establish runway
        score += 5
        factors.append(f"Emergency reserve is configured (₹{emergency_fund:,.2f}), but expense history is empty so runway cannot be calculated.")
    elif emergency_fund_ratio >= 6.0:
        score += 25
        factors.append(f"Strong financial safety net ({emergency_fund_ratio} months emergency runway).")
    elif emergency_fund_ratio >= 3.0:
        score += 18
        factors.append(f"Adequate emergency buffer ({emergency_fund_ratio} months expense coverage).")
    elif emergency_fund_ratio >= 1.0:
        score += 10
        factors.append(f"Minimal emergency fund ({emergency_fund_ratio} months). Vulnerable to unexpected shocks.")
    else:
        score += 2
        factors.append(f"Underdeveloped emergency reserve ({emergency_fund_ratio} months). Priority should be building cash buffer.")

    if emergency_fund_configured and burn_basis > 0 and not has_sufficient_expense_history:
        factors.append("Note: Runway estimate is based on limited historical expense data.")

    # Factor D: Budget Discipline & Goal Planning (Max 15 pts)
    discipline_score = 0
    if total_budget > 0:
        if total_expenses <= total_budget:
            discipline_score += 10
            factors.append("Budget discipline is maintained (spending within monthly target).")
        else:
            discipline_score += 3
            factors.append("Spending has exceeded the designated monthly budget.")
    else:
        discipline_score += 5  # Neutral if no budget set yet
        factors.append("No active monthly budget configured.")

    if active_goals_count > 0:
        discipline_score += 5
        factors.append(f"Active financial planning in place ({active_goals_count} tracked goal(s)).")
    
    score += discipline_score
    score = min(100, max(0, score))

    # 4. Health Classification
    if score >= 85:
        health_status = "Excellent"
        summary_verdict = "Your financial health is Excellent. You maintain disciplined expense management, a strong savings rate, and a robust safety reserve."
    elif score >= 70:
        health_status = "Good"
        summary_verdict = "Your financial health is Good. You have positive monthly cash flow and manageable expenditures with good financial stability."
    elif score >= 50:
        health_status = "Moderate"
        summary_verdict = "Your financial health is Moderate. While you manage your basic obligations, your savings buffer and spending ratio leave room for improvement."
    elif score >= 35:
        health_status = "Needs Improvement"
        summary_verdict = "Your financial health Needs Improvement. High living expenses or thin savings reserves present vulnerability to unexpected events."
    else:
        health_status = "Poor"
        summary_verdict = "Your financial health is Poor. Monthly outlays exceed or severely consume earnings, resulting in negative or near-zero financial runway."

    # Explanation construction
    explanation = f"{summary_verdict} Key indicators: " + " ".join(factors)

    return {
        "score": score,
        "health_status": health_status,
        "total_income": total_income,
        "total_expenses": total_expenses,
        "savings": savings,
        "savings_rate": savings_rate,
        "expense_ratio": expense_ratio,
        "emergency_fund": emergency_fund,
        "emergency_fund_configured": emergency_fund_configured,
        "emergency_fund_ratio": emergency_fund_ratio,
        "emergency_fund_status": emergency_fund_status,
        "monthly_expense_basis": burn_basis if burn_basis > 0 else 0.0,
        "runway_label": runway_label,
        "has_sufficient_expense_history": has_sufficient_expense_history,
        "explanation": explanation,
        "factors": factors
    }
