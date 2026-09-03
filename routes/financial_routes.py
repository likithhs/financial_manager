from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.auth_routes import login_required
from services.financial_service import FinancialService
from ai.financial_analyzer import evaluate_user_financial_health

financial_bp = Blueprint('financial', __name__)

INCOME_CATEGORIES = ["Salary / Wages", "Freelance / Consulting", "Business Income", "Investments / Dividends", "Allowance / Gift", "Rental Income", "Other Income"]
EXPENSE_CATEGORIES = ["Food & Dining", "Transport & Fuel", "Education & Courses", "Bills & Utilities", "Shopping & Discretionary", "Entertainment", "Healthcare & Medical", "Rent & Housing", "Other Expenses"]

# -------------------------------------------------------------
# INCOME ROUTES
# -------------------------------------------------------------
@financial_bp.route('/income', methods=['GET'])
@login_required
def income():
    user_id = session['user_id']
    incomes = FinancialService.get_user_incomes(user_id)
    total_income = sum(float(i['amount']) for i in incomes)
    today_date = date.today().strftime('%Y-%m-%d')
    return render_template('income.html', incomes=incomes, total_income=total_income, categories=INCOME_CATEGORIES, today_date=today_date)

@financial_bp.route('/income/add', methods=['POST'])
@login_required
def add_income():
    user_id = session['user_id']
    source = request.form.get('source', '')
    amount = request.form.get('amount', 0)
    category = request.form.get('category', 'Salary / Wages')
    inc_date = request.form.get('date', date.today().strftime('%Y-%m-%d'))
    description = request.form.get('description', '')

    try:
        amount = float(amount)
        if amount <= 0:
            flash('Income amount must be greater than zero.', 'danger')
            return redirect(url_for('financial.income'))
    except ValueError:
        flash('Invalid amount entered.', 'danger')
        return redirect(url_for('financial.income'))

    FinancialService.add_income(user_id, source, amount, category, inc_date, description)
    evaluate_user_financial_health(user_id) # Re-evaluate health score
    flash('Income entry recorded successfully.', 'success')
    return redirect(url_for('financial.income'))

@financial_bp.route('/income/delete/<int:income_id>', methods=['POST'])
@login_required
def delete_income(income_id):
    user_id = session['user_id']
    FinancialService.delete_income(income_id, user_id)
    evaluate_user_financial_health(user_id)
    flash('Income entry removed.', 'info')
    return redirect(url_for('financial.income'))

# -------------------------------------------------------------
# EXPENSE ROUTES
# -------------------------------------------------------------
@financial_bp.route('/expenses', methods=['GET'])
@login_required
def expenses():
    user_id = session['user_id']
    user_expenses = FinancialService.get_user_expenses(user_id)
    total_expenses = sum(float(e['amount']) for e in user_expenses)
    today_date = date.today().strftime('%Y-%m-%d')
    return render_template('expenses.html', expenses=user_expenses, total_expenses=total_expenses, categories=EXPENSE_CATEGORIES, today_date=today_date)

@financial_bp.route('/expenses/add', methods=['POST'])
@financial_bp.route('/expense/add', methods=['POST'])
@login_required
def add_expense():
    user_id = session['user_id']
    title = request.form.get('title', '') or request.form.get('category', 'Expense')
    amount = request.form.get('amount', 0)
    category = request.form.get('category', 'Food & Dining')
    exp_date = request.form.get('date', date.today().strftime('%Y-%m-%d'))
    description = request.form.get('description', '')

    try:
        amount = float(amount)
        if amount <= 0:
            flash('Expense amount must be greater than zero.', 'danger')
            return redirect(url_for('financial.expenses'))
    except ValueError:
        flash('Invalid amount entered.', 'danger')
        return redirect(url_for('financial.expenses'))

    FinancialService.add_expense(user_id, category, amount, exp_date, description, title)
    evaluate_user_financial_health(user_id) # Re-evaluate health score
    flash('Expense entry recorded successfully.', 'success')
    return redirect(url_for('financial.expenses'))

@financial_bp.route('/expenses/delete/<int:expense_id>', methods=['POST'])
@financial_bp.route('/expense/delete/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    user_id = session['user_id']
    FinancialService.delete_expense(expense_id, user_id)
    evaluate_user_financial_health(user_id)
    flash('Expense entry removed.', 'info')
    return redirect(url_for('financial.expenses'))
