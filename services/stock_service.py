import os
import requests
from config import Config
from database import query_db, execute_db

# Pre-defined realistic offline stock directory for academic demo and offline presentation
FALLBACK_STOCKS = {
    "TCS": {
        "symbol": "TCS", "name": "Tata Consultancy Services", "sector": "Information Technology",
        "market": "NSE", "price": 3850.00, "prev_close": 3810.00, "pe": 28.5,
        "market_cap": "₹14.2 Lakh Cr (Large Cap)", "high_52w": 4250.00, "low_52w": 3310.00,
        "volatility": "Low", "risk_rating": "Low", "beta": 0.75,
        "trend": [3780, 3805, 3810, 3830, 3850],
        "description": "India's largest IT consulting and software services exporter with exceptional balance sheet strength and dividend consistency."
    },
    "INFY": {
        "symbol": "INFY", "name": "Infosys Limited", "sector": "Information Technology",
        "market": "NSE", "price": 1540.00, "prev_close": 1560.00, "pe": 24.2,
        "market_cap": "₹6.4 Lakh Cr (Large Cap)", "high_52w": 1760.00, "low_52w": 1350.00,
        "volatility": "Moderate", "risk_rating": "Moderate", "beta": 0.95,
        "trend": [1580, 1565, 1560, 1530, 1540],
        "description": "Global leader in digital consulting, cloud migration and business AI transformation services."
    },
    "RELIANCE": {
        "symbol": "RELIANCE", "name": "Reliance Industries Ltd", "sector": "Energy & Telecom",
        "market": "NSE", "price": 2920.00, "prev_close": 2895.00, "pe": 26.8,
        "market_cap": "₹19.8 Lakh Cr (Large Cap)", "high_52w": 3050.00, "low_52w": 2220.00,
        "volatility": "Moderate", "risk_rating": "Moderate", "beta": 1.05,
        "trend": [2870, 2890, 2895, 2905, 2920],
        "description": "Diversified energy, petrochemicals, retail (Reliance Retail), and telecom/digital giant (Jio Platforms)."
    },
    "HDFCBANK": {
        "symbol": "HDFCBANK", "name": "HDFC Bank Ltd", "sector": "Banking & Financial Services",
        "market": "NSE", "price": 1620.00, "prev_close": 1605.00, "pe": 18.9,
        "market_cap": "₹12.3 Lakh Cr (Large Cap)", "high_52w": 1750.00, "low_52w": 1360.00,
        "volatility": "Low", "risk_rating": "Low", "beta": 0.85,
        "trend": [1590, 1600, 1605, 1612, 1620],
        "description": "Premier private sector financial institution with vast distribution network and best-in-class asset quality."
    },
    "ITC": {
        "symbol": "ITC", "name": "ITC Limited", "sector": "FMCG & Consumer Goods",
        "market": "NSE", "price": 430.00, "prev_close": 428.00, "pe": 25.1,
        "market_cap": "₹5.3 Lakh Cr (Large Cap)", "high_52w": 499.00, "low_52w": 399.00,
        "volatility": "Low", "risk_rating": "Low", "beta": 0.65,
        "trend": [422, 425, 428, 429, 430],
        "description": "Conglomerate dominating Indian FMCG, paperboards, luxury hotels, and agricultural commodities."
    },
    "TATAMOTORS": {
        "symbol": "TATAMOTORS", "name": "Tata Motors Ltd", "sector": "Automotive & EVs",
        "market": "NSE", "price": 980.00, "prev_close": 960.00, "pe": 16.4,
        "market_cap": "₹3.2 Lakh Cr (Large Cap)", "high_52w": 1179.00, "low_52w": 590.00,
        "volatility": "High", "risk_rating": "High", "beta": 1.35,
        "trend": [940, 955, 960, 970, 980],
        "description": "Global automaker with strong leadership in Indian passenger Electric Vehicles and luxury brand Jaguar Land Rover."
    },
    "ZOMATO": {
        "symbol": "ZOMATO", "name": "Zomato Limited", "sector": "Internet & Quick Commerce",
        "market": "NSE", "price": 240.00, "prev_close": 235.00, "pe": 78.0,
        "market_cap": "₹2.1 Lakh Cr (Large Cap)", "high_52w": 298.00, "low_52w": 88.00,
        "volatility": "High", "risk_rating": "High", "beta": 1.45,
        "trend": [225, 230, 235, 238, 240],
        "description": "Hyper-growth consumer tech platform operating India's top food delivery network and quick commerce arm (Blinkit)."
    },
    "AAPL": {
        "symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology & Consumer Electronics",
        "market": "NASDAQ", "price": 225.00, "prev_close": 222.50, "pe": 33.2,
        "market_cap": "$3.4 Trillion (Mega Cap)", "high_52w": 237.00, "low_52w": 164.00,
        "volatility": "Moderate", "risk_rating": "Moderate", "beta": 1.05,
        "trend": [218, 221, 222.5, 224, 225],
        "description": "Global technology company known for iPhone, Mac, iPad, wearables, and high-margin services ecosystem."
    },
    "MSFT": {
        "symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Enterprise Software & Cloud",
        "market": "NASDAQ", "price": 430.00, "prev_close": 425.00, "pe": 35.8,
        "market_cap": "$3.2 Trillion (Mega Cap)", "high_52w": 468.00, "low_52w": 309.00,
        "volatility": "Low", "risk_rating": "Low", "beta": 0.88,
        "trend": [420, 422, 425, 428, 430],
        "description": "World technology leader driving enterprise productivity, Azure cloud infrastructure, and OpenAI partnership."
    },
    "NVDA": {
        "symbol": "NVDA", "name": "NVIDIA Corporation", "sector": "Semiconductors & AI Compute",
        "market": "NASDAQ", "price": 125.00, "prev_close": 118.00, "pe": 52.4,
        "market_cap": "$3.0 Trillion (Mega Cap)", "high_52w": 140.00, "low_52w": 40.00,
        "volatility": "High", "risk_rating": "High", "beta": 1.65,
        "trend": [112, 115, 118, 122, 125],
        "description": "Dominant global creator of GPUs and CUDA architectures powering the global generative AI revolution."
    }
}

class StockService:
    @staticmethod
    def get_all_stocks():
        """Retrieve all stocks from DB or fallback dictionary."""
        db_stocks = query_db("SELECT * FROM stocks ORDER BY symbol ASC")
        if db_stocks and len(db_stocks) > 0:
            formatted = []
            for s in db_stocks:
                price = float(s['current_price'])
                prev = float(s['previous_close'])
                change = round(price - prev, 2)
                pct_change = round((change / prev) * 100, 2) if prev > 0 else 0.0
                formatted.append({
                    "symbol": s['symbol'],
                    "name": s['company_name'],
                    "sector": s['sector'],
                    "market": s.get('market', 'NSE'),
                    "price": price,
                    "prev_close": prev,
                    "change": change,
                    "pct_change": pct_change,
                    "pe": float(s['pe_ratio']),
                    "market_cap": s['market_cap'],
                    "high_52w": float(s['high_52w']),
                    "low_52w": float(s['low_52w']),
                    "volatility": s['volatility'],
                    "risk_rating": s['risk_rating'],
                    "description": s['description']
                })
            return formatted
        
        # Fallback dictionary
        res = []
        for sym, d in FALLBACK_STOCKS.items():
            change = round(d["price"] - d["prev_close"], 2)
            pct = round((change / d["prev_close"]) * 100, 2)
            res.append({
                "symbol": d["symbol"], "name": d["name"], "sector": d["sector"],
                "market": d["market"], "price": d["price"], "prev_close": d["prev_close"],
                "change": change, "pct_change": pct, "pe": d["pe"],
                "market_cap": d["market_cap"], "high_52w": d["high_52w"],
                "low_52w": d["low_52w"], "volatility": d["volatility"],
                "risk_rating": d["risk_rating"], "description": d["description"]
            })
        return res

    @staticmethod
    def search_stocks(query_str):
        """Searches stocks by ticker or company name."""
        all_s = StockService.get_all_stocks()
        if not query_str:
            return all_s
        q = query_str.strip().lower()
        return [s for s in all_s if q in s['symbol'].lower() or q in s['name'].lower() or q in s['sector'].lower()]

    @staticmethod
    def get_stock_by_symbol(symbol):
        """Fetch stock details for a single ticker."""
        sym_clean = symbol.strip().upper()
        
        # Try database first
        db_s = query_db("SELECT * FROM stocks WHERE symbol = %s", (sym_clean,), one=True)
        if db_s:
            price = float(db_s['current_price'])
            prev = float(db_s['previous_close'])
            change = round(price - prev, 2)
            pct = round((change / prev) * 100, 2) if prev > 0 else 0.0
            trend = FALLBACK_STOCKS.get(sym_clean, {}).get("trend", [prev * 0.98, prev * 0.99, prev, (prev + price)/2, price])
            return {
                "symbol": db_s['symbol'],
                "name": db_s['company_name'],
                "sector": db_s['sector'],
                "market": db_s.get('market', 'NSE'),
                "price": price,
                "prev_close": prev,
                "change": change,
                "pct_change": pct,
                "pe": float(db_s['pe_ratio']),
                "market_cap": db_s['market_cap'],
                "high_52w": float(db_s['high_52w']),
                "low_52w": float(db_s['low_52w']),
                "volatility": db_s['volatility'],
                "risk_rating": db_s['risk_rating'],
                "description": db_s['description'],
                "trend": trend,
                "mode": "Demo / Offline Mode (Live API Key not set)" if not Config.STOCK_API_KEY else "External Market API Active"
            }

        # Fallback check
        if sym_clean in FALLBACK_STOCKS:
            d = FALLBACK_STOCKS[sym_clean]
            change = round(d["price"] - d["prev_close"], 2)
            pct = round((change / d["prev_close"]) * 100, 2)
            return {
                **d,
                "change": change,
                "pct_change": pct,
                "mode": "Demo / Offline Mode"
            }
            
        return None
