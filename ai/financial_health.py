def calculate_financial_health(total_income, total_expenses, emergency_fund=0, total_budget=0, active_goals_count=0):
    """
    Evaluates personal financial health based on income, expenses, savings, budget, and runway.
    Returns a dictionary containing score (0-100), status, breakdown, and clear explanations.
    """
    total_income = float(total_income or 0.0)
    total_expenses = float(total_expenses or 0.0)
    emergency_fund = float(emergency_fund or 0.0)
    total_budget = float(total_budget or 0.0)
    
    # 1. Base Savings and Ratios
    savings = total_income - total_expenses
    
    if total_income > 0:
        savings_rate = round((savings / total_income) * 100, 2)
        expense_ratio = round((total_expenses / total_income) * 100, 2)
    else:
        savings_rate = 0.0
        expense_ratio = 100.0 if total_expenses > 0 else 0.0

    # 2. Emergency Fund Ratio (Months of Expenses Covered)
    if total_expenses > 0:
        # If user has explicit emergency savings or general positive savings
        available_savings_buffer = max(0.0, emergency_fund if emergency_fund > 0 else savings)
        emergency_fund_ratio = round(available_savings_buffer / total_expenses, 2)
    else:
        emergency_fund_ratio = 6.0 if total_income > 0 else 0.0

    # 3. Scoring Breakdown (Total: 100 pts)
    score = 0
    factors = []

    # Factor A: Savings Rate (Max 35 pts)
    if total_income <= 0:
        score += 0
        factors.append("No active recorded income.")
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

    # Factor C: Emergency Runway (Max 25 pts)
    if emergency_fund_ratio >= 6.0:
        score += 25
        factors.append("Strong financial safety net (6+ months emergency runway).")
    elif emergency_fund_ratio >= 3.0:
        score += 18
        factors.append("Adequate emergency buffer (3-5 months expense coverage).")
    elif emergency_fund_ratio >= 1.0:
        score += 10
        factors.append("Minimal emergency fund (1-2 months). Vulnerable to unexpected shocks.")
    else:
        score += 2
        factors.append("Underdeveloped emergency reserve (<1 month). Priority should be building cash buffer.")

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
        discipline_score += 5 # Neutral if no budget set yet
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
        "emergency_fund_ratio": emergency_fund_ratio,
        "explanation": explanation,
        "factors": factors
    }
