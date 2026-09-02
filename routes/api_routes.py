"""
FinAI Backend Foundation - JSON API Blueprint
Provides clean RESTful API foundation for future AJAX and client integrations.
Endpoints:
- /api/health
- /api/dashboard
- /api/income
- /api/expenses
- /api/goals
- /api/assistant
- /api/market
"""

from flask import Blueprint, jsonify, session
from services.auth_helper import login_required, get_current_user_id
from services.income_service import IncomeService
from services.expense_service import ExpenseService
from services.goal_service import GoalService
from database import query_db

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/health', methods=['GET'])
def api_health():
    """System health check endpoint."""
    return jsonify({
        "status": "ok",
        "service": "FinAI REST API",
        "version": "2.4.0"
    }), 200


@api_bp.route('/dashboard', methods=['GET'])
@login_required
def api_dashboard():
    """JSON API returning authenticated user's high-level dashboard metrics."""
    user_id = get_current_user_id()
    total_income = float(IncomeService.get_total_income(user_id))
    total_expenses = float(ExpenseService.get_total_expenses(user_id))
    net_savings = max(total_income - total_expenses, 0.0)

    return jsonify({
        "status": "success",
        "user_id": user_id,
        "metrics": {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_savings": net_savings,
            "savings_rate_pct": round((net_savings / total_income * 100), 1) if total_income > 0 else 0.0
        }
    }), 200


@api_bp.route('/income', methods=['GET'])
@login_required
def api_income():
    """JSON API returning authenticated user's income transactions."""
    user_id = get_current_user_id()
    incomes = IncomeService.get_user_incomes(user_id)
    # Serialize decimals
    for inc in incomes:
        inc['amount'] = float(inc['amount'])
    return jsonify({
        "status": "success",
        "count": len(incomes),
        "incomes": incomes
    }), 200


@api_bp.route('/expenses', methods=['GET'])
@login_required
def api_expenses():
    """JSON API returning authenticated user's expense transactions."""
    user_id = get_current_user_id()
    expenses = ExpenseService.get_user_expenses(user_id)
    for exp in expenses:
        exp['amount'] = float(exp['amount'])
    return jsonify({
        "status": "success",
        "count": len(expenses),
        "expenses": expenses
    }), 200


@api_bp.route('/goals', methods=['GET'])
@login_required
def api_goals():
    """JSON API returning authenticated user's goal progress."""
    user_id = get_current_user_id()
    goals = GoalService.get_user_goals(user_id)
    return jsonify({
        "status": "success",
        "count": len(goals),
        "goals": goals
    }), 200


@api_bp.route('/market', methods=['GET'])
@login_required
def api_market():
    """JSON API returning available market assets telemetry."""
    stocks = query_db("SELECT symbol, company_name, sector, current_price, volatility, risk_rating FROM stocks ORDER BY symbol ASC")
    for s in stocks:
        s['current_price'] = float(s['current_price'])
    return jsonify({
        "status": "success",
        "count": len(stocks),
        "stocks": stocks
    }), 200


@api_bp.route('/assistant', methods=['GET'])
@login_required
def api_assistant():
    """JSON API returning recent assistant conversation history."""
    user_id = get_current_user_id()
    history = query_db("SELECT id, user_message, ai_response, created_at FROM ai_conversations WHERE user_id = %s ORDER BY created_at ASC", (user_id,))
    return jsonify({
        "status": "success",
        "count": len(history),
        "conversations": history
    }), 200
