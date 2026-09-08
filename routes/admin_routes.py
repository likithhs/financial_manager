import sys
import platform
import time
import flask
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

@admin_bp.route('/health', methods=['GET'])
@admin_required
def health():
    """
    Dedicated Admin System Health & Diagnostic Console.
    Visualizes server vitals, database latency, table record counts, and environment metrics.
    """
    start_time = time.time()
    db_status = "Disconnected"
    db_latency = 0.0
    try:
        res = query_db("SELECT 1 as ping", one=True)
        if res and res.get('ping') == 1:
            db_status = "Connected"
            db_latency = round((time.time() - start_time) * 1000, 2)
    except Exception as e:
        db_status = f"Error: {str(e)}"

    tables_telemetry = {}
    table_names = [
        'users', 'incomes', 'expenses', 'financial_goals',
        'risk_profiles', 'stocks', 'ai_conversations', 'stock_watchlist'
    ]
    for t in table_names:
        try:
            row = query_db(f"SELECT COUNT(*) as count FROM {t}", one=True)
            tables_telemetry[t] = row['count'] if row else 0
        except Exception:
            tables_telemetry[t] = 0

    system_info = {
        "python_version": sys.version.split()[0],
        "flask_version": flask.__version__,
        "platform": platform.platform(),
        "db_engine": "MySQL 8.0 (mysql-connector-python)",
        "db_latency_ms": db_latency,
        "server_status": "Operational" if db_status == "Connected" else "Degraded",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    }

    return render_template(
        'admin/health.html',
        db_status=db_status,
        db_latency=db_latency,
        tables_telemetry=tables_telemetry,
        system_info=system_info
    )
