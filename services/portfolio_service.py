from database import query_db, execute_db
from services.stock_service import StockService

class PortfolioService:
    # -------------------------------------------------------------
    # PORTFOLIO MANAGEMENT
    # -------------------------------------------------------------
    @staticmethod
    def get_or_create_portfolio(user_id):
        portfolio = query_db("SELECT * FROM portfolios WHERE user_id = %s", (user_id,), one=True)
        if not portfolio:
            execute_db("INSERT INTO portfolios (user_id, name) VALUES (%s, %s)", (user_id, "My Investment Portfolio"))
            portfolio = query_db("SELECT * FROM portfolios WHERE user_id = %s", (user_id,), one=True)
        return portfolio

    @staticmethod
    def get_user_portfolio_summary(user_id):
        portfolio = PortfolioService.get_or_create_portfolio(user_id)
        if not portfolio:
            return {
                "portfolio_id": None,
                "name": "My Investment Portfolio",
                "total_invested": 0.0,
                "total_current_value": 0.0,
                "total_gain_loss": 0.0,
                "total_gain_loss_pct": 0.0,
                "holdings": [],
                "holdings_count": 0,
                "asset_allocation": {}
            }
        portfolio_id = portfolio['id']
        
        holdings = query_db("SELECT * FROM portfolio_holdings WHERE portfolio_id = %s ORDER BY id DESC", (portfolio_id,))
        
        total_invested = 0.0
        total_current_value = 0.0
        enriched_holdings = []
        asset_alloc = {}

        for h in holdings:
            qty = int(h['quantity'])
            buy_price = float(h['buy_price'])
            invested_val = qty * buy_price
            total_invested += invested_val

            # Get live or demo stock quote
            stock_info = StockService.get_stock_by_symbol(h['symbol'])
            current_price = float(stock_info['price']) if stock_info else buy_price
            current_val = qty * current_price
            total_current_value += current_val

            holding_gain = current_val - invested_val
            holding_gain_pct = round((holding_gain / invested_val * 100), 2) if invested_val > 0 else 0.0

            asset_type = h.get('asset_type', 'Equity Stock')
            asset_alloc[asset_type] = asset_alloc.get(asset_type, 0.0) + current_val

            enriched_holdings.append({
                **h,
                "invested_val": invested_val,
                "current_price": current_price,
                "current_val": current_val,
                "holding_gain": holding_gain,
                "holding_gain_pct": holding_gain_pct
            })

        total_gain_loss = total_current_value - total_invested
        total_gain_loss_pct = round((total_gain_loss / total_invested * 100), 2) if total_invested > 0 else 0.0

        # Percentages for asset allocation
        alloc_breakdown = {}
        for a_type, val in asset_alloc.items():
            pct = round((val / total_current_value * 100), 1) if total_current_value > 0 else 0.0
            alloc_breakdown[a_type] = pct

        return {
            "portfolio": portfolio,
            "holdings": enriched_holdings,
            "total_invested": total_invested,
            "total_current_value": total_current_value,
            "total_gain_loss": total_gain_loss,
            "total_gain_loss_pct": total_gain_loss_pct,
            "allocation": alloc_breakdown,
            "disclaimer": "This application is for educational and informational purposes and does not execute real stock trades."
        }

    @staticmethod
    def add_holding(user_id, symbol, company_name, asset_type, quantity, buy_price, buy_date, notes=""):
        portfolio = PortfolioService.get_or_create_portfolio(user_id)
        return execute_db("""
            INSERT INTO portfolio_holdings (portfolio_id, user_id, symbol, company_name, asset_type, quantity, buy_price, buy_date, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (portfolio['id'], user_id, symbol.strip().upper(), company_name.strip(), asset_type, int(quantity), float(buy_price), buy_date, notes.strip()))

    @staticmethod
    def delete_holding(holding_id, user_id):
        return execute_db("DELETE FROM portfolio_holdings WHERE id = %s AND user_id = %s", (holding_id, user_id))

    # -------------------------------------------------------------
    # WATCHLIST MANAGEMENT
    # -------------------------------------------------------------
    @staticmethod
    def get_user_watchlist(user_id):
        items = query_db("SELECT * FROM stock_watchlist WHERE user_id = %s ORDER BY id DESC", (user_id,))
        enriched = []
        for itm in items:
            stock = StockService.get_stock_by_symbol(itm['symbol'])
            if stock:
                enriched.append({
                    "id": itm['id'],
                    "symbol": itm['symbol'],
                    "company_name": itm['company_name'],
                    "price": stock['price'],
                    "change": stock['change'],
                    "pct_change": stock['pct_change'],
                    "sector": stock['sector'],
                    "risk_rating": stock['risk_rating']
                })
            else:
                enriched.append({
                    "id": itm['id'],
                    "symbol": itm['symbol'],
                    "company_name": itm['company_name'],
                    "price": 0.0,
                    "change": 0.0,
                    "pct_change": 0.0,
                    "sector": "N/A",
                    "risk_rating": "N/A"
                })
        return enriched

    @staticmethod
    def add_to_watchlist(user_id, symbol, company_name):
        existing = query_db("SELECT id FROM stock_watchlist WHERE user_id = %s AND symbol = %s", (user_id, symbol.strip().upper()), one=True)
        if not existing:
            return execute_db("""
                INSERT INTO stock_watchlist (user_id, symbol, company_name)
                VALUES (%s, %s, %s)
            """, (user_id, symbol.strip().upper(), company_name.strip()))
        return existing['id']

    @staticmethod
    def remove_from_watchlist(item_id, user_id):
        return execute_db("DELETE FROM stock_watchlist WHERE id = %s AND user_id = %s", (item_id, user_id))
