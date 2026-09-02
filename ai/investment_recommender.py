import json
from database import query_db, execute_db
from ai.investment_readiness import evaluate_investment_readiness

def generate_investment_recommendations(user_id):
    """
    Generates personalized asset allocation and general investment suggestions.
    Checks investment readiness first. If user is NOT READY, returns guidance to stabilize finances.
    """
    readiness = evaluate_investment_readiness(user_id)
    
    # 1. If user is NOT READY, return restricted response
    if not readiness['is_ready']:
        return {
            "is_ready": False,
            "status": "RESTRICTED",
            "message": "Investment recommendations are withheld until basic financial stability is established.",
            "readiness": readiness,
            "recommendations": [],
            "allocation": {},
            "disclaimer": "Investment recommendations are subject to financial stability. Always prioritize emergency cash reserves before investing in market instruments."
        }

    # 2. Fetch Risk Profile
    risk_row = query_db("SELECT risk_level FROM risk_profiles WHERE user_id = %s ORDER BY id DESC LIMIT 1", (user_id,), one=True)
    risk_level = risk_row['risk_level'] if risk_row else "Moderate"
    
    # 3. Formulate Asset Allocations & Instruments
    if risk_level == "Conservative":
        primary_category = "Capital Preservation & Fixed Income"
        allocation = {
            "Fixed Deposits / Govt Securities": 50,
            "Debt Mutual Funds & Short-term Bonds": 30,
            "Sovereign Gold Bonds / Gold ETFs": 10,
            "Large-Cap Index / Bluechip Funds": 10
        }
        instruments = [
            {
                "name": "High-Safety Bank Fixed Deposits & Post Office Term Deposits",
                "category": "Fixed Income / Guaranteed Returns",
                "risk": "Very Low",
                "recommended_horizon": "1 - 5 Years",
                "advantages": "Predictable guaranteed capital returns, zero market volatility, high liquidity in emergency.",
                "risks": "Inflation risk (returns may barely beat inflation after tax deductions)."
            },
            {
                "name": "Sovereign Gold Bonds (SGB) & Gold Mutual Funds",
                "category": "Precious Metals / Inflation Hedge",
                "risk": "Low to Moderate",
                "recommended_horizon": "5 - 8 Years",
                "advantages": "Sovereign backing, 2.5% annual interest payout, long-term inflation hedge.",
                "risks": "Gold price fluctuations over short horizons."
            },
            {
                "name": "Banking & PSU Debt Mutual Funds / Corporate Bond Funds",
                "category": "Debt Instruments",
                "risk": "Low",
                "recommended_horizon": "2 - 4 Years",
                "advantages": "Higher tax efficiency than traditional savings, high credit quality issuers.",
                "risks": "Interest rate risk and minor credit spread shifts."
            },
            {
                "name": "Large Cap Index Mutual Funds (e.g. Nifty 50 Index Fund)",
                "category": "Diversified Equity",
                "risk": "Moderate",
                "recommended_horizon": "5+ Years",
                "advantages": "Exposure to nation’s top 50 bluechip companies with lowest expense ratios.",
                "risks": "Standard market fluctuations during broader economic downturns."
            }
        ]
        rationale = (
            "Given your Conservative risk profile, the portfolio prioritizes 80% fixed income and capital preservation "
            "assets to safeguard principal while allocating a small 10-20% cushion toward bluechip index funds and gold to offset inflation."
        )

    elif risk_level == "Aggressive":
        primary_category = "Aggressive Equity & Long-Term Capital Growth"
        allocation = {
            "Diversified & Flexi-Cap Equity Funds": 40,
            "Mid-Cap & Small-Cap Mutual Funds": 30,
            "International / Thematic Technology ETFs": 15,
            "Debt Funds & Liquid Reserves": 15
        }
        instruments = [
            {
                "name": "Flexi-Cap & Large & Mid-Cap Equity Funds",
                "category": "Active Equity Mutual Funds",
                "risk": "Moderate to High",
                "recommended_horizon": "5 - 10 Years",
                "advantages": "Dynamic fund manager allocation across market caps with high compounding potential.",
                "risks": "Cyclical market corrections and drawdown volatility."
            },
            {
                "name": "Mid-Cap & Emerging Companies Growth Funds",
                "category": "High Growth Equity",
                "risk": "High",
                "recommended_horizon": "7+ Years",
                "advantages": "Captures exponential corporate growth phases of fast-expanding industry leaders.",
                "risks": "High short-term volatility and prolonged drawdown periods."
            },
            {
                "name": "Global Equity ETFs & Sectoral Technology Funds",
                "category": "International / Sectoral",
                "risk": "High",
                "recommended_horizon": "5+ Years",
                "advantages": "Geographical diversification and exposure to global tech megatrends.",
                "risks": "Currency exchange volatility and sector concentration risk."
            },
            {
                "name": "Short Duration Debt & Arbitrage Funds",
                "category": "Liquid Debt Cushion",
                "risk": "Low",
                "recommended_horizon": "1 - 3 Years",
                "advantages": "Provides ready liquidity for buying market dips (systematic transfer plans).",
                "risks": "Lower yields compared to equity."
            }
        ]
        rationale = (
            "Given your Aggressive risk profile and strong financial runway, the strategy focuses 85% on growth equities "
            "to maximize long-term compound wealth, with a 15% debt cushion to handle liquidity requirements without distress selling."
        )

    else: # Moderate
        primary_category = "Balanced Wealth Creation & Hybrid Allocation"
        allocation = {
            "Large-Cap & Flexi-Cap Mutual Funds": 45,
            "Hybrid & Balanced Advantage Funds": 25,
            "Corporate Bond Funds & Debt Assets": 20,
            "Gold ETFs / Multi-Asset Funds": 10
        }
        instruments = [
            {
                "name": "Balanced Advantage Funds (Dynamic Asset Allocation)",
                "category": "Hybrid Mutual Funds",
                "risk": "Moderate",
                "recommended_horizon": "3 - 5 Years",
                "advantages": "Automatically shifts between equity and debt based on market valuations to curb downside.",
                "risks": "Moderate returns that lag pure equities in runaway bull markets."
            },
            {
                "name": "Nifty 50 / S&P 500 Index Funds & Large-Cap Funds",
                "category": "Core Passive Equity",
                "risk": "Moderate",
                "recommended_horizon": "5+ Years",
                "advantages": "Low cost, transparent exposure to premier corporate leaders.",
                "risks": "Subject to broader stock market cycles."
            },
            {
                "name": "Target Maturity Debt Funds & Corporate Bonds",
                "category": "Fixed Income",
                "risk": "Low to Moderate",
                "recommended_horizon": "3 - 5 Years",
                "advantages": "Predictable coupon payouts, stable bond yields, superior to plain savings accounts.",
                "risks": "Mild bond duration and interest rate sensitivity."
            },
            {
                "name": "Sovereign Gold Bonds & Silver / Gold ETFs",
                "category": "Commodity Hedge",
                "risk": "Moderate",
                "recommended_horizon": "5+ Years",
                "advantages": "Reliable portfolio shock absorber during geopolitical and inflationary turbulence.",
                "risks": "No regular cashflow beyond SGB sovereign interest."
            }
        ]
        rationale = (
            "Given your Moderate risk profile, the portfolio employs a balanced 70:30 Equity/Debt-Gold hybrid mix "
            "aimed at solid capital appreciation while softening market drawdowns via dynamic debt allocation."
        )

    disclaimer = (
        "Educational & Informational Disclaimer: Mutual fund and market investments are subject to market risks. "
        "Past performance is not indicative of future returns. Please read all scheme-related documents carefully before investing."
    )

    # Persist in DB
    existing = query_db("SELECT id FROM investment_recommendations WHERE user_id = %s", (user_id,), one=True)
    alloc_json = json.dumps(allocation)
    factors_json = json.dumps(readiness['reasons'])
    instruments_json = json.dumps(instruments)

    if existing:
        execute_db("""
            UPDATE investment_recommendations
            SET primary_category = %s, risk_level = %s, recommended_allocation_json = %s,
                rationale = %s, advantages = %s, risks = %s, factors_considered = %s, evaluated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (primary_category, risk_level, alloc_json, rationale, instruments_json, disclaimer, factors_json, existing['id']))
    else:
        execute_db("""
            INSERT INTO investment_recommendations (user_id, primary_category, risk_level, recommended_allocation_json, rationale, advantages, risks, factors_considered)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (user_id, primary_category, risk_level, alloc_json, rationale, instruments_json, disclaimer, factors_json))

    return {
        "is_ready": True,
        "status": "APPROVED",
        "primary_category": primary_category,
        "risk_level": risk_level,
        "allocation": allocation,
        "instruments": instruments,
        "rationale": rationale,
        "disclaimer": disclaimer,
        "readiness": readiness
    }
