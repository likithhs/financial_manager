"""
FinAI Conversational Intelligence Engine
Generates rich, empathetic, human-grade conversational responses (ChatGPT caliber)
for personal finance questions, understanding nuanced language and emotional sentiment.
"""

import re
from ai.sentiment_engine import SentimentEngine


class ConversationalEngine:
    """
    Generates dynamic, human-like financial advisory responses.
    Synthesizes user sentiment, live financial metrics, and conversational context.
    """

    @staticmethod
    def generate_chat_response(user_id, user_message, ctx):
        """
        Generates a humanized, sentiment-aware, conversational response
        grounded in the user's live profile.
        """
        user = ctx.get("user") or {}
        health = ctx.get("health") or {}
        readiness = ctx.get("readiness") or {}
        risk_level = ctx.get("risk_level", "Moderate")
        goals = ctx.get("goals") or []
        holdings = ctx.get("holdings") or []

        user_name = user.get("name", "Investor")
        income = float(health.get("total_income", 0))
        expenses = float(health.get("total_expenses", 0))
        savings = float(health.get("savings", 0))
        savings_rate = float(health.get("savings_rate", 0))
        health_score = int(health.get("score", 0))
        health_status = health.get("health_status", "Developing")
        emergency_months = float(health.get("emergency_fund_ratio", 0))
        is_ready = readiness.get("is_ready", False)

        # 1. Analyze Sentiment
        sentiment_data = SentimentEngine.analyze_sentiment(user_message)
        sentiment = sentiment_data["sentiment"]
        opening = sentiment_data["empathetic_opening"]

        msg = user_message.lower().strip()

        # 2. Match Conversational Financial Intent
        response_body = ConversationalEngine._synthesize_advisory(
            msg, user_name, income, expenses, savings, savings_rate,
            health_score, health_status, emergency_months, is_ready,
            risk_level, goals, holdings, sentiment
        )

        # 3. Combine opening, conversational body, and interactive follow-up
        full_response = f"{opening}\n\n{response_body}"
        return full_response

    @staticmethod
    def _synthesize_advisory(
        msg, user_name, income, expenses, savings, savings_rate,
        health_score, health_status, emergency_months, is_ready,
        risk_level, goals, holdings, sentiment
    ):
        """Synthesizes humanized conversational guidance based on financial topic."""

        # -------------------------------------------------------------
        # A. STRESS, DEBT OVERWHELM & PAYCHECK-TO-PAYCHECK
        # -------------------------------------------------------------
        if any(w in msg for w in [
            "debt", "loan", "emi", "credit card", "broke", "paycheck to paycheck",
            "drowning", "struggling", "bills", "behind", "can't save", "overwhelmed"
        ]) or sentiment == "ANXIETY_STRESS":
            
            steps = []
            if savings <= 0:
                steps.append(
                    f"1. **Stabilize Immediate Cashflow:** Right now, your monthly expenses (₹{expenses:,.0f}) "
                    f"are consuming all of your recorded income (₹{income:,.0f}). The very first victory is creating "
                    f"even a small monthly breathing room of ₹1,000 to ₹3,000 by temporarily pausing non-essential discretionary spends."
                )
            else:
                steps.append(
                    f"1. **Leverage Your Existing Surplus:** You currently have a recorded monthly surplus of "
                    f"**₹{savings:,.0f}**. This is your primary engine to attack debt or build safety."
                )

            steps.append(
                "2. **The Debt Avalanche vs. Snowball:** If you have multiple loans or credit cards, list them out. "
                "The **Avalanche method** (paying off the highest interest rate first) saves the most money mathematically, "
                "while the **Snowball method** (paying off the smallest balance first) gives you quick psychological wins."
            )
            steps.append(
                "3. **Build a Micro-Buffer:** Don't throw 100% of every spare rupee at debt. Keep a modest ₹10,000–₹25,000 "
                "micro-reserve so that an unexpected medical bill or vehicle repair doesn't force you back into high-interest borrowing."
            )

            body = (
                f"Here is how we can systematically turn this situation around, {user_name}:\n\n"
                + "\n\n".join(steps)
                + "\n\n"
                "Remember, building financial peace of mind isn't about extreme deprivation—it's about intentionality. "
                "Which specific expense or debt is weighing on your mind the most right now? Let's break it down together."
            )
            return body

        # -------------------------------------------------------------
        # B. WEALTH BUILDING, BECOMING RICH, FIRE, COMPOUNDING
        # -------------------------------------------------------------
        if any(w in msg for w in [
            "rich", "wealth", "crorepati", "millionaire", "retire early", "fire",
            "double my money", "10x", "skyrocket", "financial freedom", "compound"
        ]) or sentiment == "AMBITION_EXCITEMENT":
            
            body = (
                f"Building true, generational wealth is a journey of disciplined leverage and compounding. "
                f"Here is the realistic, proven wealth architecture that turns ambitious earners into crorepatis:\n\n"
                f"### 1. The Core Wealth Equation\n"
                f"Wealth is built on three pillars: **(Income – Expenses) × High-ROI Assets × Time**.\n"
                f"• Your current recorded monthly savings rate is **{savings_rate:.1f}%**.\n"
                f"• Top wealth builders target a savings rate of **30% to 50%**, aggressively channeling the surplus into equity assets.\n\n"
                f"### 2. The Power of Consistent Compounding (Rule of 72)\n"
                f"If you invest ₹15,000 to ₹25,000 per month in diversified equity index funds compounding at an average 12% annual return:\n"
                f"• In 10 years: You accumulate ~**₹35 to ₹58 Lakhs**.\n"
                f"• In 15 years: You cross ~**₹1 Crore**.\n"
                f"• In 20 years: That expands to ~**₹2.5 to ₹4 Crores**.\n"
                f"Notice how the real explosion happens between years 10 and 20! That's the hockey-stick curve of compound interest.\n\n"
                f"### 3. Your Actionable Gameplan Today\n"
                f"• Currently, your 6-Pillar Health Score is **{health_score}/100**.\n"
                f"• Ensure your baseline liquidity ({emergency_months:.1f} months currently) reaches at least 3–6 months so you never have to interrupt your compounding engine during market dips.\n\n"
                f"What is your target retirement age or net-worth milestone? We can calculate the exact monthly SIP needed to get you there!"
            )
            return body

        # -------------------------------------------------------------
        # C. BEGINNER / CONFUSED / "WHERE DO I START?" / EXPLAIN SIMPLY
        # -------------------------------------------------------------
        if any(w in msg for w in [
            "where do i start", "where to start", "how do i begin", "new to this",
            "beginner", "explain simply", "confused", "lost", "explain like"
        ]) or sentiment == "CONFUSION_OVERWHELM":

            body = (
                f"Let's make personal finance crystal clear and completely stress-free, {user_name}. "
                f"Think of your finances like building a house—you need a solid concrete foundation before putting up the roof.\n\n"
                f"### The 5-Step Financial Hierarchy:\n"
                f"1. **Cashflow Clarity (Ground Floor):** Know what comes in and what goes out. Right now, your income is ₹{income:,.0f} and expenses are ₹{expenses:,.0f}.\n"
                f"2. **Emergency Cushion (The Foundation):** Stash 3 to 6 months of living expenses in a high-yield savings account or liquid fund. This protects you from life's surprises.\n"
                f"3. **Kill Toxic Debt (Reinforced Walls):** Clear any loans with interest rates above 10% (like credit cards or personal loans).\n"
                f"4. **Automated Investing (The Engine):** Start a monthly Systematic Investment Plan (SIP) in a broad market index fund (like Nifty 50 or S&P 500). Set it to auto-debit the day after your salary lands.\n"
                f"5. **Goal Tracking (The Roof):** Earmark specific pots of money for specific milestones (house down payment, vacations, retirement).\n\n"
                f"You don't have to do all five at once! Master step 1 and 2 first. "
                f"Would you like to start by reviewing your monthly budget breakdown or setting up your emergency buffer?"
            )
            return body

        # -------------------------------------------------------------
        # D. FEAR OF LOSS, SAFETY, MARKET CRASHES & CAUTION
        # -------------------------------------------------------------
        if any(w in msg for w in [
            "safe", "safety", "crash", "recession", "scared", "lose money",
            "risk", "guaranteed", "fixed return", "fd", "gold"
        ]) or sentiment == "CAUTION_FEAR":

            body = (
                f"Your focus on safety is the mark of a wise investor. Capital preservation is priority number one.\n\n"
                f"### The Hidden Risk: Inflation\n"
                f"While keeping money in a bank locker or traditional savings account feels safe, it has a silent predator: **Inflation** (typically 5–7% per year). "
                f"If your cash earns 3% while inflation is 6%, your purchasing power actually shrinks by 3% every single year.\n\n"
                f"### The Low-Risk Wealth Shield Strategy:\n"
                f"• **Tier 1 (Zero-Risk Liquidity):** Keep your 3–6 month emergency reserve in Bank Fixed Deposits or Sovereign Treasury Bills. Guaranteed capital, instant access.\n"
                f"• **Tier 2 (Inflation Hedge):** Allocate 10–15% to Sovereign Gold Bonds (SGB) or physical gold. Historically, gold acts as a parachute during geopolitical tensions and currency depreciation.\n"
                f"• **Tier 3 (High-Grade Debt Funds):** High-quality corporate bond funds or banking/PSU debt funds provide steady, predictable yields with minimal price volatility.\n"
                f"• **Tier 4 (Conservative Equity Growth):** When you feel ready, even a 15–20% allocation to large-cap index funds allows your portfolio to beat inflation without keeping you awake at night.\n\n"
                f"Your current risk profile is categorized as **{risk_level}**. How do you feel about splitting your surplus between guaranteed FDs and gold to start?"
            )
            return body

        # -------------------------------------------------------------
        # E. CAN I AFFORD TO INVEST? / INVESTMENT READINESS
        # -------------------------------------------------------------
        if any(w in msg for w in [
            "can i invest", "afford to invest", "ready to invest", "should i invest",
            "how much to invest", "where to invest", "investment readiness"
        ]):
            if savings <= 0:
                body = (
                    f"Let's be completely transparent with your numbers, {user_name}.\n\n"
                    f"• **Monthly Income:** ₹{income:,.2f}\n"
                    f"• **Monthly Expenses:** ₹{expenses:,.2f}\n"
                    f"• **Current Monthly Surplus:** ₹{savings:,.2f}\n\n"
                    f"Right now, investing in volatile markets would put undue pressure on your daily life. "
                    f"If you invested without a cash buffer, any unexpected expense (medical, car repair, household) "
                    f"might force you to sell your investments at an unfavorable price.\n\n"
                    f"**My Honest Recommendation:**\n"
                    f"Let's focus first on carving out a surplus of at least **₹2,000 to ₹5,000** per month through expense optimization. "
                    f"Once we have that recurring cashflow and a 1-month emergency buffer, we will activate your investment engine immediately!"
                )
            else:
                suggested_sip = round(savings * 0.40, -2)
                body = (
                    f"You are in an encouraging position! You currently have a monthly cash surplus of **₹{savings:,.2f}** "
                    f"(a savings rate of **{savings_rate:.1f}%**).\n\n"
                    f"### Investment Readiness Check:\n"
                    f"• **Readiness Status:** {'🟢 Ready for Market Allocation' if is_ready else '🟡 Building Foundation First'}\n"
                    f"• **Emergency Fund:** {emergency_months:.1f} months of expenses saved\n"
                    f"• **Risk Tolerance:** {risk_level}\n\n"
                    f"### Suggested Action Plan:\n"
                    f"A sensible, balanced approach right now would be allocating **₹{suggested_sip:,.0f} per month** into systematic investing, "
                    f"while directing the remaining **₹{(savings - suggested_sip):,.0f}** towards bolstering your emergency reserves.\n\n"
                    f"Would you prefer broad index mutual funds, diversified flexi-cap funds, or a mix of equity and debt?"
                )
            return body

        # -------------------------------------------------------------
        # F. FINANCIAL HEALTH SCORE & COMPREHENSIVE DIAGNOSTICS
        # -------------------------------------------------------------
        if any(w in msg for w in [
            "health score", "financial health", "how am i doing", "status",
            "diagnostics", "analyze my finances", "financial situation"
        ]):
            body = (
                f"Here is your personalized **Financial Health Diagnostic & Executive Summary**, {user_name}:\n\n"
                f"### Overall Score: **{health_score}/100** ({health_status})\n\n"
                f"| Metric | Your Current Number | Healthy Benchmark | Status |\n"
                f"| :--- | :--- | :--- | :--- |\n"
                f"| **Monthly Income** | ₹{income:,.2f} | Predictable & Steady | {'🟢' if income > 0 else '🔴'} |\n"
                f"| **Monthly Expenses** | ₹{expenses:,.2f} | < 70% of Income | {'🟢' if savings > 0 else '🔴'} |\n"
                f"| **Savings Rate** | {savings_rate:.1f}% | 20% – 35% | {'🟢' if savings_rate >= 20 else '🟡' if savings_rate > 0 else '🔴'} |\n"
                f"| **Emergency Fund** | {emergency_months:.1f} Months | 3 – 6 Months | {'🟢' if emergency_months >= 3 else '🟡' if emergency_months >= 1 else '🔴'} |\n"
                f"| **Risk Profile** | {risk_level} | Matched to Goals | 🟢 Balanced |\n\n"
                f"### Top Strategic Priorities to Level Up Your Score:\n"
                f"1. {'Increase your recorded monthly income or log income transactions' if income == 0 else 'Keep lifestyle inflation low as your income scales'}.\n"
                f"2. {'Target building a ₹25,000 starter emergency fund' if emergency_months < 1 else 'Grow your emergency fund to 3–6 months of living expenses'}.\n"
                f"3. {'Optimize high discretionary spending to generate monthly investment surplus' if savings <= 0 else f'Automate a monthly SIP of ₹{savings * 0.3:.0f} into diversified equity'}.\n\n"
                f"What part of your financial health would you like us to optimize first?"
            )
            return body

        # -------------------------------------------------------------
        # G. BUDGETING, SAVING & EXPENSE CONTROL
        # -------------------------------------------------------------
        if any(w in msg for w in [
            "budget", "budgeting", "save", "savings", "spend", "spending",
            "cut expenses", "expense control", "50/30/20"
        ]):
            target_needs = income * 0.50
            target_wants = income * 0.30
            target_savings = income * 0.20

            body = (
                f"Smart budgeting isn't about starving your lifestyle—it's about telling your money where to go "
                f"instead of wondering where it went!\n\n"
                f"### The 50/30/20 Blueprint tailored to your income (₹{income:,.0f}):\n"
                f"• **50% for Needs (₹{target_needs:,.0f}):** Rent, groceries, utilities, basic transportation, and minimum debt payments.\n"
                f"• **30% for Wants (₹{target_wants:,.0f}):** Dining out, entertainment, shopping, weekend trips, and hobbies.\n"
                f"• **20% for Savings & Wealth (₹{target_savings:,.0f}):** Emergency buffer, mutual fund SIPs, and goal funding.\n\n"
                f"### 3 Practical Psychological Spending Hacks:\n"
                f"1. **The 48-Hour Rule:** Whenever you want to buy something non-essential over ₹2,000, wait 48 hours. 70% of the impulse desire fades.\n"
                f"2. **Reverse Budgeting (Pay Yourself First):** Move your savings target to a separate account the very morning your paycheck hits.\n"
                f"3. **Subscription Audit:** Review recurring debits (OTT platforms, gym memberships, apps) and cancel whatever you haven't used in 30 days.\n\n"
                f"Would you like us to review your recent expenses to uncover where your biggest financial leaks are?"
            )
            return body

        # -------------------------------------------------------------
        # H. STOCKS, EQUITIES, PORTFOLIO & MUTUAL FUNDS
        # -------------------------------------------------------------
        if any(w in msg for w in [
            "stock", "stocks", "share", "shares", "portfolio", "mutual fund",
            "etf", "sip", "nifty", "sensex", "equity", "market"
        ]):
            body = (
                f"When approached with discipline rather than gambling, equities are the single greatest wealth-generating engine in modern history.\n\n"
                f"### Core Principles for Market Success:\n"
                f"1. **Index Over Single-Stock Guesswork:** For 90% of investors, low-cost broad index funds (like Nifty 50 or Nifty Next 50) outperform active fund managers and stock pickers over a 10-year horizon.\n"
                f"2. **SIP Beats Market Timing:** Trying to time the market bottoms and tops is a fool's errand. Investing fixed amounts every month (Rupee Cost Averaging) buys more units when prices are low and fewer when prices are high.\n"
                f"3. **Asset Allocation:** Balance your equities with debt or gold according to your **{risk_level}** risk profile. A classic 70% Equity / 20% Debt / 10% Gold allocation allows you to ride market bull runs while staying resilient in drawdowns.\n\n"
                f"Currently, your recorded equity holdings include: "
                f"{len(holdings)} positions. "
                f"Are you interested in evaluating a specific company's fundamentals, or designing an automated mutual fund SIP strategy?"
            )
            return body

        # -------------------------------------------------------------
        # I. FINANCIAL GOALS & RETIREMENT
        # -------------------------------------------------------------
        if any(w in msg for w in [
            "goal", "goals", "milestone", "retire", "retirement", "pension",
            "buy a house", "buy a car", "wedding", "education"
        ]):
            goals_text = ""
            if goals:
                goals_text = "\n".join([f"• **{g.get('name', 'Goal')}**: Target ₹{float(g.get('target_amount', 0)):,.0f}" for g in goals[:3]])
            else:
                goals_text = "No active financial goals logged in your dashboard yet."

            body = (
                f"Every rupee should have a purpose. Aligning your money with personal life milestones transforms saving from a chore into an exciting journey!\n\n"
                f"### Your Active Goals:\n{goals_text}\n\n"
                f"### How to Categorize Goals for Maximum Return:\n"
                f"• **Short-Term (< 2 years):** (e.g. Vacation, electronics, emergency fund). Keep 100% in safe, liquid instruments like Bank FDs or Liquid Funds. Never put money you need in 12 months into the stock market!\n"
                f"• **Medium-Term (2–5 years):** (e.g. Car down payment, wedding). Use Conservative or Balanced Hybrid Funds.\n"
                f"• **Long-Term (> 5–7 years):** (e.g. Home purchase, child's education, early retirement). High equity allocation (Flexi-cap, Large & Mid-cap funds) to maximize compounding.\n\n"
                f"Would you like to calculate how much you need to invest monthly for a specific goal you're working towards?"
            )
            return body

        # -------------------------------------------------------------
        # J. GENERAL FINANCIAL STRATEGY & ADVISORY CONVERSATION
        # -------------------------------------------------------------
        body = (
            f"I'm here as your dedicated personal wealth strategist and advisor, {user_name}.\n\n"
            f"Whether you want to optimize your monthly cashflow (currently **₹{income:,.0f}** income vs **₹{expenses:,.0f}** expenses), "
            f"grow your **{emergency_months:.1f}-month emergency buffer**, reduce interest on debt, or build an automated investment strategy tailored to your **{risk_level}** risk profile—we can tackle it step by step.\n\n"
            f"What is the most pressing financial question or goal on your mind right now?"
        )
        return body
