from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.auth_routes import login_required
from services.financial_service import FinancialService
from ai.financial_analyzer import evaluate_user_financial_health

goal_bp = Blueprint('goal', __name__)

GOAL_PRESETS = [
    "Emergency Fund (3-6 Months Expenses)",
    "Higher Education & Certifications",
    "Vehicle / Two-Wheeler / Car",
    "Travel & Vacation",
    "Laptop & Technology Equipment",
    "Home Down Payment",
    "Retirement Corpus",
    "Other Long-Term Goal"
]

@goal_bp.route('/goals', methods=['GET'])
@login_required
def goals():
    user_id = session['user_id']
    user_goals = FinancialService.get_user_goals(user_id)
    today_date = date.today().strftime('%Y-%m-%d')
    return render_template('goals.html', goals=user_goals, presets=GOAL_PRESETS, today_date=today_date)

@goal_bp.route('/goals/add', methods=['POST'])
@login_required
def add_goal():
    user_id = session['user_id']
    name = request.form.get('name', '')
    target_amount = request.form.get('target_amount', 0)
    current_amount = request.form.get('current_amount', 0)
    target_date = request.form.get('target_date', date.today().strftime('%Y-%m-%d'))
    priority = request.form.get('priority', 'Medium')
    description = request.form.get('description', '')

    try:
        target_amount = float(target_amount)
        current_amount = float(current_amount or 0.0)
        if target_amount <= 0:
            flash('Target amount must be greater than zero.', 'danger')
            return redirect(url_for('goal.goals'))
    except ValueError:
        flash('Invalid target or starting amount entered.', 'danger')
        return redirect(url_for('goal.goals'))

    FinancialService.add_goal(user_id, name, target_amount, current_amount, target_date, priority, description)
    evaluate_user_financial_health(user_id)
    flash(f"Goal '{name}' created successfully!", 'success')
    return redirect(url_for('goal.goals'))

@goal_bp.route('/goals/add-funds/<int:goal_id>', methods=['POST'])
@login_required
def add_funds(goal_id):
    """
    CUMULATIVE UPDATE:
    Adds deposit to current balance (e.g. 5,000 + 2,000 = 7,000).
    """
    user_id = session['user_id']
    added_amount = request.form.get('added_amount', 0)

    try:
        added_amount = float(added_amount)
        if added_amount <= 0:
            flash('Contribution amount must be greater than zero.', 'danger')
            return redirect(url_for('goal.goals'))
    except ValueError:
        flash('Invalid contribution amount.', 'danger')
        return redirect(url_for('goal.goals'))

    success = FinancialService.add_funds_to_goal(goal_id, user_id, added_amount)
    if success:
        evaluate_user_financial_health(user_id)
        flash(f"Successfully added ₹{added_amount:,.2f} to your goal progress!", 'success')
    else:
        flash('Failed to update goal. Please try again.', 'danger')

    return redirect(url_for('goal.goals'))

@goal_bp.route('/goals/delete/<int:goal_id>', methods=['POST'])
@login_required
def delete_goal(goal_id):
    user_id = session['user_id']
    FinancialService.delete_goal(goal_id, user_id)
    evaluate_user_financial_health(user_id)
    flash('Financial goal removed.', 'info')
    return redirect(url_for('goal.goals'))
