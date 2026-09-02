"""
FinAI Backend Foundation - Dashboard Routes Blueprint
Handles executive overview telemetry and aggregated user metrics (/dashboard).
"""

from flask import Blueprint, render_template, session
from services.auth_helper import login_required
from database import query_db
from services.income_service import IncomeService
from services.expense_service import ExpenseService
from services.goal_service import GoalService
from services.portfolio_service import PortfolioService
from ai.financial_analyzer import evaluate_user_financial_health
from ai.investment_readiness import evaluate_investment_readiness
from ai.investment_recommender import generate_investment_recommendations

dashboard_bp = Blueprint('dashboard_bp', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    """Executive Cockpit view for the authenticated user."""
    user_id = session['user_id']

    # 1. Financial Health & Diagnosis
    health = evaluate_user_financial_health(user_id)

    # 2. Risk Profile
    risk_row = query_db(
        "SELECT risk_level, score FROM risk_profiles WHERE user_id = %s ORDER BY id DESC LIMIT 1",
        (user_id,),
        one=True
    )
    user_risk = risk_row['risk_level'] if risk_row else "Not Assessed Yet"

    # 3. Investment Readiness
    readiness = evaluate_investment_readiness(user_id)

    # 4. Latest Recommendation Snapshot
    latest_rec = generate_investment_recommendations(user_id)

    # 5. Portfolio & Watchlist Snapshot
    portfolio_summary = PortfolioService.get_user_portfolio_summary(user_id)
    watchlist_count = query_db(
        "SELECT COUNT(*) as count FROM stock_watchlist WHERE user_id = %s",
        (user_id,),
        one=True
    )['count']

    # 6. Latest Stock Analysis
    latest_stock_analysis = query_db(
        "SELECT * FROM stock_analysis WHERE user_id = %s ORDER BY evaluated_at DESC LIMIT 1",
        (user_id,),
        one=True
    )

    # 7. Recent Incomes and Expenses
    recent_incomes = IncomeService.get_user_incomes(user_id)[:3]
    recent_expenses = ExpenseService.get_user_expenses(user_id)[:3]

    # 8. Goals Preview
    goals_preview = GoalService.get_user_goals(user_id)[:2]

    return render_template(
        'dashboard.html',
        health=health,
        risk_level=user_risk,
        readiness=readiness,
        latest_rec=latest_rec,
        portfolio=portfolio_summary,
        watchlist_count=watchlist_count,
        latest_stock_analysis=latest_stock_analysis,
        recent_incomes=recent_incomes,
        recent_expenses=recent_expenses,
        goals=goals_preview
    )
