"""
FinAI Backend Foundation - Income Routes Blueprint
Handles user earnings, salary logs, and transaction-based inflows (/income).
"""

from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.auth_helper import login_required, get_current_user_id
from services.income_service import IncomeService
from services.validators import ValidationError
from ai.financial_analyzer import evaluate_user_financial_health

income_bp = Blueprint('income', __name__)

INCOME_CATEGORIES = [
    "Salary / Wages",
    "Freelance / Consulting",
    "Business Income",
    "Investments / Dividends",
    "Allowance / Gift",
    "Rental Income",
    "Other Income"
]


@income_bp.route('/income', methods=['GET'])
@login_required
def income():
    user_id = get_current_user_id()
    incomes = IncomeService.get_user_incomes(user_id)
    total_income = float(IncomeService.get_total_income(user_id))
    today_date = date.today().strftime('%Y-%m-%d')
    return render_template(
        'income.html',
        incomes=incomes,
        total_income=total_income,
        categories=INCOME_CATEGORIES,
        today_date=today_date
    )


@income_bp.route('/income/add', methods=['POST'])
@login_required
def add_income():
    user_id = get_current_user_id()
    source = request.form.get('source', '').strip()
    amount = request.form.get('amount', 0)
    category = request.form.get('category', 'Salary / Wages')
    inc_date = request.form.get('date', date.today().strftime('%Y-%m-%d'))
    description = request.form.get('description', '').strip()

    try:
        IncomeService.add_income(user_id, source, amount, category, inc_date, description)
        evaluate_user_financial_health(user_id)
        flash('Income entry recorded successfully.', 'success')
    except ValidationError as ve:
        flash(ve.message, 'danger')

    return redirect(url_for('income.income'))


@income_bp.route('/income/delete/<int:income_id>', methods=['POST'])
@login_required
def delete_income(income_id):
    user_id = get_current_user_id()
    IncomeService.delete_income(income_id, user_id)
    evaluate_user_financial_health(user_id)
    flash('Income entry removed.', 'info')
    return redirect(url_for('income.income'))
