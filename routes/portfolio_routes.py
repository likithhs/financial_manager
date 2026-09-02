from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.auth_routes import login_required
from services.portfolio_service import PortfolioService
from services.stock_service import StockService

portfolio_bp = Blueprint('portfolio', __name__)

ASSET_TYPES = ["Equity Stock", "Mutual Fund", "Bond / Debenture", "Gold / SGB", "Fixed Deposit"]

# -------------------------------------------------------------
# PORTFOLIO ROUTES
# -------------------------------------------------------------
@portfolio_bp.route('/portfolio', methods=['GET'])
@login_required
def portfolio():
    user_id = session['user_id']
    summary = PortfolioService.get_user_portfolio_summary(user_id)
    all_stocks = StockService.get_all_stocks()
    today_date = date.today().strftime('%Y-%m-%d')
    return render_template('portfolio.html', summary=summary, all_stocks=all_stocks, asset_types=ASSET_TYPES, today_date=today_date)

@portfolio_bp.route('/portfolio/add', methods=['POST'])
@login_required
def add_holding():
    user_id = session['user_id']
    symbol = request.form.get('symbol', '').strip().upper()
    company_name = request.form.get('company_name', '').strip()
    asset_type = request.form.get('asset_type', 'Equity Stock')
    quantity = request.form.get('quantity', 1)
    buy_price = request.form.get('buy_price', 0)
    buy_date = request.form.get('buy_date', date.today().strftime('%Y-%m-%d'))
    notes = request.form.get('notes', '')

    # Auto-fill name if matching stock symbol
    if not company_name:
        stock_info = StockService.get_stock_by_symbol(symbol)
        company_name = stock_info['name'] if stock_info else symbol

    try:
        qty = int(quantity)
        price = float(buy_price)
        if qty <= 0 or price <= 0:
            flash('Quantity and buy price must be positive numbers.', 'danger')
            return redirect(url_for('portfolio.portfolio'))
    except ValueError:
        flash('Invalid quantity or price entered.', 'danger')
        return redirect(url_for('portfolio.portfolio'))

    PortfolioService.add_holding(user_id, symbol, company_name, asset_type, qty, price, buy_date, notes)
    flash(f"Holding '{symbol}' added to your portfolio.", 'success')
    return redirect(url_for('portfolio.portfolio'))

@portfolio_bp.route('/portfolio/delete/<int:holding_id>', methods=['POST'])
@login_required
def delete_holding(holding_id):
    user_id = session['user_id']
    PortfolioService.delete_holding(holding_id, user_id)
    flash('Holding removed from your portfolio.', 'info')
    return redirect(url_for('portfolio.portfolio'))

# -------------------------------------------------------------
# WATCHLIST ROUTES
# -------------------------------------------------------------
@portfolio_bp.route('/watchlist', methods=['GET'])
@login_required
def watchlist():
    user_id = session['user_id']
    watchlist_items = PortfolioService.get_user_watchlist(user_id)
    all_stocks = StockService.get_all_stocks()
    return render_template('watchlist.html', watchlist=watchlist_items, all_stocks=all_stocks)

@portfolio_bp.route('/watchlist/add', methods=['POST'])
@login_required
def add_watchlist():
    user_id = session['user_id']
    symbol = request.form.get('symbol', '').strip().upper()
    company_name = request.form.get('company_name', '').strip()

    if not company_name:
        stock_info = StockService.get_stock_by_symbol(symbol)
        company_name = stock_info['name'] if stock_info else symbol

    if not symbol:
        flash('Please select or specify a stock symbol.', 'danger')
        return redirect(url_for('portfolio.watchlist'))

    PortfolioService.add_to_watchlist(user_id, symbol, company_name)
    flash(f"Added '{symbol}' to your Watchlist.", 'success')
    return redirect(url_for('portfolio.watchlist'))

@portfolio_bp.route('/watchlist/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_watchlist(item_id):
    user_id = session['user_id']
    PortfolioService.remove_from_watchlist(item_id, user_id)
    flash('Stock removed from Watchlist.', 'info')
    return redirect(url_for('portfolio.watchlist'))
