from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.auth_routes import login_required
from services.financial_service import FinancialService
from ai.financial_analyzer import evaluate_user_financial_health

budget_bp = Blueprint('budget', __name__)

@budget_bp.route('/budget', methods=['GET'])
@login_required
def budget():
    user_id = session['user_id']
    current_month = date.today().strftime('%Y-%m')
    
    # Get budget summary for current month
    summary = FinancialService.get_budget_summary(user_id, current_month)
    
    # Also fetch overall income & expenses for comparative savings rate calculation
    health_data = evaluate_user_financial_health(user_id)

    return render_template('budget.html', summary=summary, health=health_data, current_month=current_month)

@budget_bp.route('/budget/set', methods=['POST'])
@login_required
def set_budget():
    user_id = session['user_id']
    month_year = request.form.get('month_year', date.today().strftime('%Y-%m'))
    total_budget = request.form.get('total_budget', 0)

    try:
        total_budget = float(total_budget)
        if total_budget < 0:
            flash('Budget amount cannot be negative.', 'danger')
            return redirect(url_for('budget.budget'))
    except ValueError:
        flash('Invalid budget amount entered.', 'danger')
        return redirect(url_for('budget.budget'))

    FinancialService.set_budget(user_id, month_year, total_budget)
    evaluate_user_financial_health(user_id)
    flash(f"Monthly budget for {month_year} set to ₹{total_budget:,.2f}.", 'success')
    return redirect(url_for('budget.budget'))
