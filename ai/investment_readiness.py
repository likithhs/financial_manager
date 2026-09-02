import json
from database import query_db, execute_db
from ai.financial_analyzer import evaluate_user_financial_health

def evaluate_investment_readiness(user_id):
    """
    Evaluates whether the user has adequate financial stability to begin investing.
    Rule: Financial stability comes before investment recommendations.
    Returns readiness status (READY vs NOT READY), readiness score, reasons, and actionable suggestions.
    """
    # 1. Fetch Latest Financial Health
    health = evaluate_user_financial_health(user_id)
    
    # 2. Fetch Risk Profile
    risk_row = query_db("SELECT risk_level, score FROM risk_profiles WHERE user_id = %s ORDER BY id DESC LIMIT 1", (user_id,), one=True)
    user_risk = risk_row['risk_level'] if risk_row else "Conservative (Default)"
    
    # 3. Decision Evaluation
    is_ready = True
    readiness_score = 0
    reasons = []
    suggestions = []

    # Check A: Income Existence & Positive Cashflow
    if health['total_income'] <= 0:
        is_ready = False
        reasons.append("No recorded income: An active and predictable cash flow is required before allocating funds to investments.")
        suggestions.append("Record your regular monthly income sources under Personal Finances.")
    elif health['savings'] <= 0:
        is_ready = False
        reasons.append("Negative or Zero Savings: Monthly expenses exceed or equal your total earnings, leaving zero surplus for investing.")
        suggestions.append("Audit discretionary spending and reduce monthly living costs to create positive savings buffer.")
    else:
        readiness_score += 35
        reasons.append(f"Positive monthly savings buffer of ₹{health['savings']:,.2f} ({health['savings_rate']}% savings rate).")

    # Check B: Emergency Runway
    if health['emergency_fund_ratio'] < 1.0:
        is_ready = False
        reasons.append("Underdeveloped Emergency Fund: You currently have less than 1 month of living expenses saved in liquid cash.")
        suggestions.append("Set a target in Goals to accumulate at least 3 to 6 months of basic living expenses before taking market risks.")
    elif health['emergency_fund_ratio'] < 3.0:
        readiness_score += 25
        reasons.append("Emerging safety fund (1-3 months expenses). Acceptable for conservative low-risk investments.")
        suggestions.append("Continue building emergency fund in tandem with conservative recurring deposits.")
    else:
        readiness_score += 35
        reasons.append(f"Strong safety net: {health['emergency_fund_ratio']} months of expense runway safely secured.")

    # Check C: Expense Ratio
    if health['expense_ratio'] > 85.0 and health['total_income'] > 0:
        is_ready = False
        reasons.append(f"Excessive Expense Ratio ({health['expense_ratio']}%): Spending consumes almost all income.")
        suggestions.append("Aim to bring monthly expense ratio below 70% to ensure sustainable investment continuity.")
    elif health['expense_ratio'] <= 70.0:
        readiness_score += 20
        reasons.append(f"Healthy expense ratio ({health['expense_ratio']}%).")
    else:
        readiness_score += 10
        reasons.append(f"Moderate expense ratio ({health['expense_ratio']}%).")

    # Check D: Health Classification
    if health['health_status'] in ['Poor', 'Needs Improvement']:
        is_ready = False
        reasons.append(f"Overall financial health is evaluated as '{health['health_status']}', indicating high risk of capital distress.")
        suggestions.append("Improve financial health score by adhering to budgets and eliminating unnecessary expenditures.")
    else:
        readiness_score += 10

    # Final Classification
    status_label = "READY FOR CONSIDERATION" if is_ready else "NOT READY"

    # Persist or update in DB
    existing = query_db("SELECT id FROM investment_readiness WHERE user_id = %s", (user_id,), one=True)
    reasons_json = json.dumps(reasons)
    suggestions_json = json.dumps(suggestions)

    if existing:
        execute_db("""
            UPDATE investment_readiness
            SET is_ready = %s, readiness_score = %s, reasons_json = %s, suggestions_json = %s, evaluated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (1 if is_ready else 0, readiness_score, reasons_json, suggestions_json, existing['id']))
    else:
        execute_db("""
            INSERT INTO investment_readiness (user_id, is_ready, readiness_score, reasons_json, suggestions_json)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, 1 if is_ready else 0, readiness_score, reasons_json, suggestions_json))

    return {
        "is_ready": is_ready,
        "status_label": status_label,
        "readiness_score": readiness_score,
        "reasons": reasons,
        "suggestions": suggestions,
        "health": health,
        "risk_level": user_risk
    }
