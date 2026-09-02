"""
FinAI Backend Foundation - Expense Routes Blueprint
Handles categorized outlays and living expenses (/expenses).
"""

from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.auth_helper import login_required, get_current_user_id
from services.expense_service import ExpenseService
from services.validators import ValidationError
from ai.financial_analyzer import evaluate_user_financial_health

expense_bp = Blueprint('expense', __name__)


@expense_bp.route('/expenses', methods=['GET'])
@login_required
def expenses():
    user_id = get_current_user_id()
    expenses_list = ExpenseService.get_user_expenses(user_id)
    total_expenses = float(ExpenseService.get_total_expenses(user_id))
    categories = ExpenseService.get_categories()
    today_date = date.today().strftime('%Y-%m-%d')
    return render_template(
        'expenses.html',
        expenses=expenses_list,
        total_expenses=total_expenses,
        categories=categories,
        today_date=today_date
    )


@expense_bp.route('/expenses/add', methods=['POST'])
@login_required
def add_expense():
    user_id = get_current_user_id()
    title = request.form.get('title', '').strip()
    amount = request.form.get('amount', 0)
    category = request.form.get('category', 'Other')
    exp_date = request.form.get('date', date.today().strftime('%Y-%m-%d'))
    description = request.form.get('description', '').strip()

    try:
        ExpenseService.add_expense(user_id, title, amount, category, exp_date, description)
        evaluate_user_financial_health(user_id)
        flash('Expense entry logged successfully.', 'success')
    except ValidationError as ve:
        flash(ve.message, 'danger')

    return redirect(url_for('expense.expenses'))


@expense_bp.route('/expenses/delete/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    user_id = get_current_user_id()
    ExpenseService.delete_expense(expense_id, user_id)
    evaluate_user_financial_health(user_id)
    flash('Expense entry removed.', 'info')
    return redirect(url_for('expense.expenses'))
