from database import query_db, execute_db
from services.stock_service import StockService
from ai.investment_readiness import evaluate_investment_readiness

def analyze_stock_suitability(user_id, symbol):
    """
    Evaluates compatibility between a selected stock and the user's financial condition & risk profile.
    Returns suitability classification, suitability score (0-100), key factors, and safety warnings.
    """
    stock = StockService.get_stock_by_symbol(symbol)
    if not stock:
        return {
            "error": f"Stock symbol '{symbol}' not found in registry.",
            "status": "NOT_FOUND"
        }

    # 1. Fetch user risk profile & readiness
    readiness = evaluate_investment_readiness(user_id)
    risk_row = query_db("SELECT risk_level FROM risk_profiles WHERE user_id = %s ORDER BY id DESC LIMIT 1", (user_id,), one=True)
    user_risk = risk_row['risk_level'] if risk_row else "Moderate"
    
    # Stock attributes
    stock_volatility = stock.get("volatility", "Moderate")
    stock_risk = stock.get("risk_rating", "Moderate")
    stock_pe = stock.get("pe", 20.0)
    stock_name = stock.get("name", symbol)
    sector = stock.get("sector", "General")

    # 2. Gatekeeper: If user is financially NOT READY
    if not readiness['is_ready']:
        suitability_status = "Not Suitable for Current Profile"
        suitability_score = 20
        reasons = [
            f"Financial stability constraint: Your current financial health is evaluated as '{readiness['health']['health_status']}'.",
            "Emergency liquidity and basic cashflow stability must be established before allocating capital to volatile equities.",
            f"Investing in direct stocks like {stock_name} introduces market capital risk that is unsuitable during an emergency fund buildup phase."
        ]
        guidance = "Focus on building your emergency savings buffer before engaging in individual stock research."

    # 3. Risk Profile Matrix Matching
    elif user_risk == "Conservative":
        if stock_risk == "Low":
            suitability_status = "Suitable for Further Research"
            suitability_score = 75
            reasons = [
                f"{stock_name} is a large-cap company with low historical volatility and defensive characteristics.",
                "Stable earnings track record aligns with conservative risk limits for moderate long-term equity allocation.",
                "P/E valuation is relatively grounded compared to broader high-beta speculative names."
            ]
            guidance = "Consider researching this stock as a small part of a core diversified portfolio, maintaining adequate debt/cash buffer."
        elif stock_risk == "Moderate":
            suitability_status = "Watchlist"
            suitability_score = 55
            reasons = [
                f"{stock_name} exhibits moderate market sensitivity.",
                "Conservative investors should monitor earnings reports and look for favorable valuation dips rather than aggressive entry.",
                "Direct equity exposure should not exceed 10-15% of your total investable net worth."
            ]
            guidance = "Add to your watchlist to observe price consistency over 2-3 quarters."
        else: # High risk stock for Conservative user
            suitability_status = "Not Suitable for Current Profile"
            suitability_score = 25
            reasons = [
                f"{stock_name} has high market volatility and a beta > 1.3.",
                "This stock experiences sharp cyclical corrections that conflict with your capital preservation objective.",
                "Valuation multiples (P/E) or earnings volatility create downside risk that exceeds conservative tolerance."
            ]
            guidance = "Prioritize fixed income, index funds, or low-volatility bluechip equities."

    elif user_risk == "Moderate":
        if stock_risk in ["Low", "Moderate"]:
            suitability_status = "Suitable for Further Research"
            suitability_score = 85
            reasons = [
                f"{stock_name} fits well within your Moderate risk tolerance.",
                f"Operating in the {sector} sector with steady cash flows and balanced growth prospects.",
                "Supports balanced capital growth while keeping overall portfolio beta within manageable bounds."
            ]
            guidance = "A good candidate for fundamental analysis, balance sheet inspection, and systematic dollar-cost averaging."
        else: # High risk stock for Moderate user
            suitability_status = "Higher Risk"
            suitability_score = 48
            reasons = [
                f"{stock_name} exhibits high growth characteristics but also elevated volatility.",
                "Price swings may lead to temporary drawdowns exceeding 15-25% during market pullbacks.",
                "Appropriate only as a strictly sized satellite position (<5% of total portfolio)."
            ]
            guidance = "Treat with caution: conduct thorough due diligence on competitive moats and avoid allocating large lumpsum capital."

    else: # Aggressive user
        if stock_risk == "High":
            suitability_status = "Suitable for Further Research"
            suitability_score = 88
            reasons = [
                f"{stock_name} offers strong high-growth potential aligned with your aggressive long-term horizon.",
                "High beta and volatility are acceptable given your capacity to endure short-term market cycles.",
                f"Sector leadership in {sector} provides substantial upside exposure during economic expansion."
            ]
            guidance = "Suitable for high-growth capital allocation with a minimum 5-year investment horizon."
        else:
            suitability_status = "Suitable for Further Research"
            suitability_score = 80
            reasons = [
                f"{stock_name} provides steady defensive anchoring to complement aggressive high-growth holdings.",
                "Helps temper overall portfolio volatility without sacrificing reasonable equity returns.",
                "Offers consistent cash flows or dividend yields."
            ]
            guidance = "Useful as a stabilizing foundation asset within an aggressive growth portfolio."

    disclaimer = (
        "Educational & Risk Disclaimer: This AI stock analysis is for educational decision-support purposes only. "
        "It does not constitute financial advice, nor does it guarantee future stock price performance. "
        "Always perform your own due diligence before making investment commitments."
    )

    reasons_text = " | ".join(reasons)

    # Persist in DB
    execute_db("""
        INSERT INTO stock_analysis (user_id, symbol, company_name, suitability_status, suitability_score, analysis_reasons, user_risk_level, stock_risk_level)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (user_id, symbol, stock_name, suitability_status, suitability_score, reasons_text, user_risk, stock_risk))

    return {
        "stock": stock,
        "symbol": symbol,
        "company_name": stock_name,
        "suitability_status": suitability_status,
        "suitability_score": suitability_score,
        "reasons": reasons,
        "guidance": guidance,
        "user_risk_level": user_risk,
        "stock_risk_level": stock_risk,
        "disclaimer": disclaimer,
        "readiness_status": readiness['status_label']
    }
