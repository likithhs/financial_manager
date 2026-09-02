from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.auth_routes import login_required
from services.stock_service import StockService
from ai.stock_recommender import analyze_stock_suitability
from database import query_db

stock_bp = Blueprint('stock', __name__)

@stock_bp.route('/stocks', methods=['GET'])
@login_required
def stocks():
    query_str = request.args.get('q', '').strip()
    stock_list = StockService.search_stocks(query_str)
    return render_template('stocks.html', stocks=stock_list, query_str=query_str)

@stock_bp.route('/stocks/<symbol>', methods=['GET'])
@login_required
def stock_detail(symbol):
    stock_data = StockService.get_stock_by_symbol(symbol)
    if not stock_data:
        flash(f"Stock ticker '{symbol}' was not found.", 'danger')
        return redirect(url_for('stock.stocks'))
    return render_template('stock_detail.html', stock=stock_data)

@stock_bp.route('/stock-analysis', methods=['GET', 'POST'])
@login_required
def stock_analysis():
    user_id = session['user_id']
    symbol = request.args.get('symbol') or request.form.get('symbol') or 'TCS'
    symbol = symbol.strip().upper()

    analysis_result = analyze_stock_suitability(user_id, symbol)
    if "error" in analysis_result:
        flash(analysis_result['error'], 'danger')
        return redirect(url_for('stock.stocks'))

    all_stocks = StockService.get_all_stocks()

    return render_template(
        'stock_analysis.html',
        analysis=analysis_result,
        all_stocks=all_stocks,
        current_symbol=symbol
    )
