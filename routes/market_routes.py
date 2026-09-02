"""
FinAI Backend Foundation - Market Routes Blueprint
Handles equity listings, securities explorer, and market telemetry (/market and /stocks).
"""

from flask import Blueprint, render_template, request
from services.auth_helper import login_required
from database import query_db

market_bp = Blueprint('market', __name__)


from services.stock_service import StockService


@market_bp.route('/market', methods=['GET'])
@market_bp.route('/stocks', methods=['GET'])
@login_required
def market():
    query_str = request.args.get('q', '').strip()
    if query_str:
        stock_list = StockService.search_stocks(query_str)
    else:
        stock_list = StockService.get_all_stocks()

    return render_template('stocks.html', stocks=stock_list, query_str=query_str)


@market_bp.route('/stocks/<symbol>')
@market_bp.route('/market/<symbol>')
@login_required
def stock_detail(symbol):
    stock = query_db("SELECT * FROM stocks WHERE symbol = %s", (symbol.upper(),), one=True)
    if not stock:
        return render_template('base.html', error_message="Security Not Found"), 404
    return render_template('stock_detail.html', stock=stock)
