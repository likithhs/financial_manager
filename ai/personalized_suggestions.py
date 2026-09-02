def generate_smart_suggestions(health_data, readiness_data, risk_level):
    """
    Generates actionable, prioritized financial suggestions based on live metrics.
    """
    suggestions = []
    
    # 1. Budget & Cashflow tips
    if health_data['total_income'] <= 0:
        suggestions.append({
            "category": "Income Tracking",
            "priority": "High",
            "title": "Record Regular Income Sources",
            "description": "Log your salary, freelance earnings, or monthly allowances to enable personalized budget tracking."
        })
    elif health_data['savings_rate'] < 20:
        suggestions.append({
            "category": "Savings Optimization",
            "priority": "High",
            "title": "Optimize Discretionary Spending",
            "description": f"Your current savings rate is {health_data['savings_rate']}%. Aim to follow the 50/30/20 rule: 50% for Needs, 30% for Wants, and 20% for Savings."
        })

    # 2. Emergency Fund tips
    if health_data['emergency_fund_ratio'] < 3.0:
        suggestions.append({
            "category": "Emergency Safety Net",
            "priority": "Critical",
            "title": "Build 3-6 Months Liquid Safety Fund",
            "description": f"You currently have {health_data['emergency_fund_ratio']} months of expense buffer. Prioritize setting aside liquid cash before committing to market volatility."
        })

    # 3. Investment readiness suggestions
    if not readiness_data.get('is_ready', False):
        suggestions.append({
            "category": "Investment Readiness",
            "priority": "Medium",
            "title": "Establish Financial Stability First",
            "description": "Maintain disciplined monthly budget adherence for 2-3 consecutive months to qualify for market investment recommendations."
        })
    else:
        if risk_level == "Conservative":
            suggestions.append({
                "category": "Investment Allocation",
                "priority": "Medium",
                "title": "Explore Sovereign Gold Bonds & Fixed Deposits",
                "description": "Lock in favorable interest rates on high-grade bank FDs and allocate 10% to Sovereign Gold Bonds to protect against inflation."
            })
        elif risk_level == "Moderate":
            suggestions.append({
                "category": "Investment Allocation",
                "priority": "Medium",
                "title": "Start a Systematic Investment Plan (SIP)",
                "description": "Automate monthly SIPs in low-cost Nifty 50 Index Funds and Balanced Advantage Funds to benefit from rupee cost averaging."
            })
        elif risk_level == "Aggressive":
            suggestions.append({
                "category": "Investment Allocation",
                "priority": "Medium",
                "title": "Diversify Across High-Growth Sectors",
                "description": "Combine core flexi-cap funds with select quality mid-cap equities, ensuring single stock positions do not exceed 10% of your portfolio."
            })

    return suggestions
