from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.auth_routes import admin_required
from database import query_db, execute_db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/', methods=['GET'])
@admin_required
def dashboard():
    # System Metrics
    user_count = query_db("SELECT COUNT(*) as count FROM users", one=True)['count']
    income_stats = query_db("SELECT COUNT(*) as count, SUM(amount) as total FROM incomes", one=True)
    expense_stats = query_db("SELECT COUNT(*) as count, SUM(amount) as total FROM expenses", one=True)
    ai_query_count = query_db("SELECT COUNT(*) as count FROM ai_conversations", one=True)['count']
    stock_analysis_count = query_db("SELECT COUNT(*) as count FROM stock_analysis", one=True)['count']
    goals_count = query_db("SELECT COUNT(*) as count FROM financial_goals", one=True)['count']

    recent_users = query_db("SELECT * FROM users ORDER BY created_at DESC LIMIT 5")
    recent_analyses = query_db("SELECT * FROM stock_analysis ORDER BY evaluated_at DESC LIMIT 5")

    return render_template(
        'admin/dashboard.html',
        user_count=user_count,
        income_count=income_stats['count'],
        income_total=float(income_stats['total'] or 0.0),
        expense_count=expense_stats['count'],
        expense_total=float(expense_stats['total'] or 0.0),
        ai_query_count=ai_query_count,
        stock_analysis_count=stock_analysis_count,
        goals_count=goals_count,
        recent_users=recent_users,
        recent_analyses=recent_analyses
    )

@admin_bp.route('/users', methods=['GET'])
@admin_required
def users():
    all_users = query_db("SELECT * FROM users ORDER BY id ASC")
    return render_template('admin/users.html', users=all_users)

@admin_bp.route('/reports', methods=['GET'])
@admin_required
def reports():
    all_incomes = query_db("SELECT i.*, u.name as user_name FROM incomes i JOIN users u ON i.user_id = u.id ORDER BY i.id DESC LIMIT 20")
    all_expenses = query_db("SELECT e.*, u.name as user_name FROM expenses e JOIN users u ON e.user_id = u.id ORDER BY e.id DESC LIMIT 20")
    all_ai_logs = query_db("SELECT a.*, u.name as user_name FROM ai_conversations a JOIN users u ON a.user_id = u.id ORDER BY a.id DESC LIMIT 20")
    all_inv_recs = query_db("SELECT r.*, u.name as user_name FROM investment_recommendations r JOIN users u ON r.user_id = u.id ORDER BY r.id DESC LIMIT 20")

    return render_template(
        'admin/reports.html',
        incomes=all_incomes,
        expenses=all_expenses,
        ai_logs=all_ai_logs,
        inv_recs=all_inv_recs
    )
