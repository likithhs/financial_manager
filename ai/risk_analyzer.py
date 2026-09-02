"""
FinAI Intelligent Risk Profiling & Psychometric Assessment Engine
Evaluates user risk tolerance across 3 Structured Assessment Pillars (10 comprehensive questions).
"""

import json
from database import query_db, execute_db

RISK_PILLARS = [
    {
        "pillar_id": "capacity",
        "pillar_title": "Pillar 1: Financial Capacity & Time Horizon",
        "pillar_desc": "Evaluates your ability to bear financial drawdowns based on horizon, income, and liabilities.",
        "pillar_icon": "fa-solid fa-hourglass-half",
        "questions": [
            {
                "id": "q1",
                "number": 1,
                "question": "What is your primary investment time horizon before you need access to this capital?",
                "subtitle": "Longer investment horizons allow compounding and sufficient time to ride out market dips.",
                "options": [
                    {"text": "Short-term: Less than 12 months (Immediate liquidity required)", "points": 1, "badge": "Very Low Risk"},
                    {"text": "Medium-term: 1 to 3 years (Near-term milestones or planned purchases)", "points": 2, "badge": "Low Risk"},
                    {"text": "Long-term: 3 to 7 years (Wealth building, major financial goals)", "points": 3, "badge": "Moderate Risk"},
                    {"text": "Decade+: 7+ years (Long-term retirement, generational compounding)", "points": 4, "badge": "High Risk"}
                ]
            },
            {
                "id": "q2",
                "number": 2,
                "question": "How secure and predictable is your current primary source of monthly income?",
                "subtitle": "A steady income stream provides a reliable safety cushion for regular capital deployment.",
                "options": [
                    {"text": "Unpredictable / Commission-only / Irregular freelancing", "points": 1, "badge": "Vulnerable"},
                    {"text": "Moderately steady with periodic or seasonal variations", "points": 2, "badge": "Fluctuating"},
                    {"text": "Reliable salaried employment or established consistent business", "points": 3, "badge": "Stable"},
                    {"text": "Highly secure position with multiple diversified income streams", "points": 4, "badge": "Very Secure"}
                ]
            },
            {
                "id": "q3",
                "number": 3,
                "question": "How many months of mandatory living expenses do you hold in liquid emergency funds?",
                "subtitle": "Emergency reserves prevent you from being forced to liquidate investments at a loss during crises.",
                "options": [
                    {"text": "No emergency fund (Living paycheck to paycheck)", "points": 1, "badge": "Critical Risk"},
                    {"text": "1 to 2 months of expenses saved in bank", "points": 2, "badge": "Thin Buffer"},
                    {"text": "3 to 6 months of living expenses safely preserved", "points": 3, "badge": "Adequate Buffer"},
                    {"text": "6+ months of living expenses fully secured in liquid deposits", "points": 4, "badge": "Strong Buffer"}
                ]
            },
            {
                "id": "q4",
                "number": 4,
                "question": "What proportion of your monthly income is committed toward debt repayments and EMIs?",
                "subtitle": "Lower debt obligations significantly enhance your capacity to absorb investment volatility.",
                "options": [
                    {"text": "Heavy debt: Over 50% of monthly income goes toward EMIs/loans", "points": 1, "badge": "High Debt"},
                    {"text": "Moderate debt: 30% to 50% of monthly income goes toward debt", "points": 2, "badge": "Moderate Debt"},
                    {"text": "Light debt: Under 30% of income committed to debt service", "points": 3, "badge": "Manageable"},
                    {"text": "Zero debt: Completely debt-free with no monthly loan obligations", "points": 4, "badge": "Zero Debt"}
                ]
            }
        ]
    },
    {
        "pillar_id": "knowledge",
        "pillar_title": "Pillar 2: Market Experience & Financial Literacy",
        "pillar_desc": "Evaluates your familiarity with asset classes, inflation dynamics, and market cycles.",
        "pillar_icon": "fa-solid fa-graduation-cap",
        "questions": [
            {
                "id": "q5",
                "number": 5,
                "question": "What is your prior level of personal investment experience?",
                "subtitle": "Hands-on participation in market cycles develops emotional discipline and resilience.",
                "options": [
                    {"text": "Novice: Zero experience (Only savings accounts and cash)", "points": 1, "badge": "Beginner"},
                    {"text": "Basic: Bank Fixed Deposits, Post Office schemes, or physical Gold", "points": 2, "badge": "Conservative"},
                    {"text": "Intermediate: Mutual Funds, Index SIPs, or Debt Instruments", "points": 3, "badge": "Informed"},
                    {"text": "Advanced: Direct Equities, ETFs, Derivatives, or Sectoral Funds", "points": 4, "badge": "Experienced"}
                ]
            },
            {
                "id": "q6",
                "number": 6,
                "question": "How do you view inflation and its impact on your savings over time?",
                "subtitle": "Real wealth generation requires outpacing inflation to preserve future purchasing power.",
                "options": [
                    {"text": "I prioritize principal safety; inflation is not a primary concern for me", "points": 1, "badge": "Preservation"},
                    {"text": "I prefer guaranteed returns even if they slightly trail inflation", "points": 2, "badge": "Cautious"},
                    {"text": "I want returns that reliably match or beat inflation by 2% to 3%", "points": 3, "badge": "Inflation-Beater"},
                    {"text": "I actively seek high real returns to compound purchasing power significantly", "points": 4, "badge": "Growth-Driven"}
                ]
            },
            {
                "id": "q7",
                "number": 7,
                "question": "When making financial decisions, which approach best describes your process?",
                "subtitle": "Analytical decision making allows navigating volatile conditions without panic.",
                "options": [
                    {"text": "I only invest in government-backed or bank-guaranteed schemes", "points": 1, "badge": "Risk-Averse"},
                    {"text": "I rely on family or bank manager advice before doing anything", "points": 2, "badge": "Guided"},
                    {"text": "I research mutual funds, diversification, and asset allocation strategies", "points": 3, "badge": "Analytical"},
                    {"text": "I study financial balance sheets, valuation metrics, and market trends", "points": 4, "badge": "Self-Directed"}
                ]
            }
        ]
    },
    {
        "pillar_id": "psychology",
        "pillar_title": "Pillar 3: Psychological Risk Tolerance & Volatility Response",
        "pillar_desc": "Evaluates your emotional temperament and behavioral reaction when capital fluctuates.",
        "pillar_icon": "fa-solid fa-brain",
        "questions": [
            {
                "id": "q8",
                "number": 8,
                "question": "If your portfolio dropped by 20% in 3 months due to a market correction, what would you do?",
                "subtitle": "Your instinctual behavioral response during a drawdown defines your true risk profile.",
                "options": [
                    {"text": "Sell all positions immediately to cut losses and preserve remaining cash", "points": 1, "badge": "Panic Exit"},
                    {"text": "Feel intense anxiety, stop further investing, and move capital to fixed deposits", "points": 2, "badge": "Cautious Hold"},
                    {"text": "Stay patient, continue automated SIPs, and wait for market recovery", "points": 3, "badge": "Disciplined"},
                    {"text": "View it as a massive discount opportunity and aggressively allocate more capital", "points": 4, "badge": "Opportunistic"}
                ]
            },
            {
                "id": "q9",
                "number": 9,
                "question": "Which potential annual return profile would you choose for a ₹1,00,000 investment?",
                "subtitle": "Balancing expected upside against downside volatility risk.",
                "options": [
                    {"text": "Guaranteed 6% gain (₹6,000) with 0% risk of losing any capital", "points": 1, "badge": "Zero Volatility"},
                    {"text": "Potential 10% gain (₹10,000) with a small risk of losing up to 3%", "points": 2, "badge": "Mild Volatility"},
                    {"text": "Potential 18% gain (₹18,000) with a risk of losing up to 10%", "points": 3, "badge": "Moderate Swing"},
                    {"text": "Potential 30%+ gain (₹30,000+) with a risk of losing up to 20%", "points": 4, "badge": "High Volatility"}
                ]
            },
            {
                "id": "q10",
                "number": 10,
                "question": "What percentage of your surplus monthly savings are you comfortable putting into market equities?",
                "subtitle": "Direct benchmark for your personal asset allocation comfort.",
                "options": [
                    {"text": "0% — Strictly fixed deposits, PPF, and guaranteed instruments", "points": 1, "badge": "0% Equity"},
                    {"text": "10% to 25% — Small allocation to conservative large-cap funds", "points": 2, "badge": "20% Equity"},
                    {"text": "26% to 60% — Balanced 50:50 allocation between debt and growth funds", "points": 3, "badge": "50% Equity"},
                    {"text": "Over 60% — Aggressive allocation to diversified growth equities and stocks", "points": 4, "badge": "70%+ Equity"}
                ]
            }
        ]
    }
]

# Flattened list for quick iterations
ALL_QUESTIONS = []
for p in RISK_PILLARS:
    ALL_QUESTIONS.extend(p["questions"])

RISK_QUESTIONS = ALL_QUESTIONS


def evaluate_risk_profile(answers_dict):
    """
    Evaluates risk score from submitted questionnaire dictionary {q1: 2, q2: 3, ...}.
    Returns total score (10 to 40), percentage score (25% to 100%), risk level, and full explanation.
    """
    total_score = 0
    total_questions = len(ALL_QUESTIONS)

    for q in ALL_QUESTIONS:
        qid = q["id"]
        chosen_points = int(answers_dict.get(qid, 2))
        total_score += chosen_points

    score_pct = round((total_score / (total_questions * 4)) * 100, 1)

    if total_score <= 18:
        risk_level = "Conservative"
        explanation = (
            "Your profile indicates a Conservative risk tolerance. You strongly prioritize capital security, "
            "steady predictable returns, and low volatility over aggressive capital appreciation. "
            "FinAI recommends allocating predominantly to Fixed Deposits (50%), Sovereign Gold Bonds (20%), "
            "and Liquid Debt Instruments (20%), with a minimal exposure to Large-Cap Index Funds (10%)."
        )
        color_theme = "good"
        badge_bg = "#10b981"
    elif total_score <= 29:
        risk_level = "Moderate"
        explanation = (
            "Your profile indicates a Moderate / Balanced risk tolerance. You are comfortable accepting calculated "
            "market fluctuations in exchange for healthy wealth compounding over a 3 to 7 year horizon. "
            "FinAI recommends a balanced 50:50 allocation: 50% in Broad Market Equity Index Funds & Mid-Caps, "
            "30% in Fixed Income / Debt Instruments, and 20% in Gold or Liquid Emergency Assets."
        )
        color_theme = "warning"
        badge_bg = "#f59e0b"
    else:
        risk_level = "Aggressive"
        explanation = (
            "Your profile indicates an Aggressive / Growth risk tolerance. You have substantial risk capacity, "
            "a long-term horizon, and the psychological discipline to navigate significant market drawdowns. "
            "FinAI recommends a high-growth allocation: 70% in Equities (Large-Cap, Mid-Cap, Multi-Cap & Direct Stocks), "
            "15% in Thematic / Small-Cap funds, 10% in Debt for tactical rebalancing, and 5% in Gold."
        )
        color_theme = "excellent"
        badge_bg = "#8b5cf6"

    return {
        "score": total_score,
        "max_score": total_questions * 4,
        "score_pct": score_pct,
        "risk_level": risk_level,
        "explanation": explanation,
        "color_theme": color_theme,
        "badge_bg": badge_bg,
        "answers": answers_dict
    }


def save_user_risk_profile(user_id, evaluated_risk):
    """Persists risk evaluation to risk_profiles and risk_assessments tables."""
    execute_db("""
        INSERT INTO risk_profiles (user_id, score, risk_level, explanation)
        VALUES (%s, %s, %s, %s)
    """, (
        user_id,
        evaluated_risk['score'],
        evaluated_risk['risk_level'],
        evaluated_risk['explanation']
    ))

    try:
        execute_db("""
            INSERT INTO risk_assessments (user_id, score, risk_profile, assessment_data)
            VALUES (%s, %s, %s, %s)
        """, (
            user_id,
            evaluated_risk['score'],
            evaluated_risk['risk_level'],
            json.dumps(evaluated_risk['answers'])
        ))
    except Exception:
        pass

    return True
