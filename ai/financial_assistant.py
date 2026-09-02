import json
import re

from database import query_db, execute_db

from ai.financial_analyzer import evaluate_user_financial_health
from ai.investment_readiness import evaluate_investment_readiness
from ai.intent_classifier import IntentClassifier
from ai.financial_calculator import FinancialCalculator
from ai.goal_analyzer import GoalAnalyzer
from ai.stock_recommender import analyze_stock_suitability


class FinAIAssistant:
    """
    Intelligent Conversational Assistant for Personal Financial Guidance.

    Provides:
    - Financial health analysis
    - Investment readiness
    - Risk profile information
    - Financial goal analysis
    - Savings guidance
    - Budget analysis
    - Portfolio information
    - What-if financial calculations
    - Stock analysis
    - Investment education
    """

    # =============================================================
    # USER CONTEXT
    # =============================================================

    @staticmethod
    def get_user_full_context(user_id):
        """
        Collect all relevant financial information for a user.
        """

        # ---------------------------------------------------------
        # USER
        # ---------------------------------------------------------

        user = query_db(
            """
            SELECT id, name, email, role
            FROM users
            WHERE id = %s
            """,
            (user_id,),
            one=True
        )

        # ---------------------------------------------------------
        # FINANCIAL HEALTH
        # ---------------------------------------------------------

        health = evaluate_user_financial_health(user_id)

        # ---------------------------------------------------------
        # INVESTMENT READINESS
        # ---------------------------------------------------------

        readiness = evaluate_investment_readiness(user_id)

        # ---------------------------------------------------------
        # RISK PROFILE
        # ---------------------------------------------------------

        risk_row = query_db(
            """
            SELECT risk_level, score
            FROM risk_profiles
            WHERE user_id = %s
            ORDER BY id DESC
            LIMIT 1
            """,
            (user_id,),
            one=True
        )

        if risk_row:
            risk_level = risk_row.get(
                "risk_level",
                "Moderate (Not yet fully assessed)"
            )
        else:
            risk_level = "Moderate (Not yet fully assessed)"

        # ---------------------------------------------------------
        # FINANCIAL GOALS
        # ---------------------------------------------------------

        goals = query_db(
            """
            SELECT
                id,
                goal_name,
                target_amount,
                current_amount,
                target_date,
                priority,
                status
            FROM financial_goals
            WHERE user_id = %s
            ORDER BY target_date ASC
            """,
            (user_id,)
        )

        # ---------------------------------------------------------
        # PORTFOLIO
        # ---------------------------------------------------------

        holdings = query_db(
            """
            SELECT
                symbol,
                company_name,
                quantity,
                buy_price
            FROM portfolio_holdings
            WHERE user_id = %s
            """,
            (user_id,)
        )

        # ---------------------------------------------------------
        # WATCHLIST
        # ---------------------------------------------------------

        watchlist = query_db(
            """
            SELECT
                symbol,
                company_name
            FROM stock_watchlist
            WHERE user_id = %s
            """,
            (user_id,)
        )

        return {
            "user": user,
            "health": health,
            "readiness": readiness,
            "risk_level": risk_level,
            "goals": goals or [],
            "holdings": holdings or [],
            "watchlist": watchlist or []
        }

    # =============================================================
    # MAIN RESPONSE FUNCTION
    # =============================================================

    @staticmethod
    def respond(user_id, user_message):
        """
        Process a user's financial question and return
        a personalized response.
        """

        # ---------------------------------------------------------
        # GET USER CONTEXT
        # ---------------------------------------------------------

        ctx = FinAIAssistant.get_user_full_context(user_id)

        msg = user_message.strip().lower()

        # ---------------------------------------------------------
        # CLASSIFY INTENT
        # ---------------------------------------------------------

        intent = IntentClassifier.classify(user_message)

        # ---------------------------------------------------------
        # BASIC FINANCIAL DATA
        # ---------------------------------------------------------

        health = ctx["health"]
        readiness = ctx["readiness"]

        income = float(health.get("total_income", 0))
        expenses = float(health.get("total_expenses", 0))
        savings = float(health.get("savings", 0))

        savings_rate = float(
            health.get("savings_rate", 0)
        )

        health_status = health.get(
            "health_status",
            "Unknown"
        )

        health_score = health.get(
            "score",
            0
        )

        is_ready = readiness.get(
            "is_ready",
            False
        )

        risk = ctx.get(
            "risk_level",
            "Moderate (Not yet fully assessed)"
        )

        user_name = (
            ctx["user"]["name"]
            if ctx.get("user")
            else "Investor"
        )

        # ---------------------------------------------------------
        # GOALS
        # ---------------------------------------------------------

        goal_summary = GoalAnalyzer.get_goal_summary(user_id)

        user_goals = goal_summary.get(
            "goals",
            []
        )

        # =========================================================
        # 1. FINANCIAL HEALTH
        # =========================================================

        if intent == "financial_health":

            factors = health.get(
                "factors",
                []
            )

            if factors:
                factor_text = "\n".join(
                    f"• {factor}"
                    for factor in factors
                )
            else:
                factor_text = "No additional factors available."

            response = (
                "**Your Financial Health Analysis**\n\n"
                f"• **Health Score:** {health_score}/100\n"
                f"• **Status:** {health_status}\n"
                f"• **Monthly Income:** ₹{income:,.2f}\n"
                f"• **Monthly Expenses:** ₹{expenses:,.2f}\n"
                f"• **Savings:** ₹{savings:,.2f}\n"
                f"• **Savings Rate:** {savings_rate:.2f}%\n"
                f"• **Expense Ratio:** "
                f"{health.get('expense_ratio', 0)}%\n"
                f"• **Emergency Fund:** "
                f"{health.get('emergency_fund_ratio', 0)} months\n\n"
                "**Key Factors:**\n"
                f"{factor_text}"
            )

        # =========================================================
        # 2. INVESTMENT AFFORDABILITY
        # =========================================================

        elif intent == "investment_affordability":

            if savings <= 0:

                response = (
                    "**Investment Affordability Analysis**\n\n"
                    f"Based on your current recorded cashflow, "
                    f"you currently have **₹{savings:,.2f}** "
                    f"available as monthly surplus.\n\n"
                    f"Your recorded income is "
                    f"₹{income:,.2f} and expenses are "
                    f"₹{expenses:,.2f}.\n\n"
                    "At this stage, I would prioritize building "
                    "a positive monthly savings buffer before investing."
                )

            else:

                suggested_amount = round(
                    savings * 0.20,
                    2
                )

                readiness_text = (
                    "READY FOR CONSIDERATION"
                    if is_ready
                    else "NOT READY"
                )

                response = (
                    "**Investment Affordability Analysis**\n\n"
                    f"Your current monthly surplus is "
                    f"**₹{savings:,.2f}**.\n\n"
                    f"A conservative starting allocation could be around "
                    f"**₹{suggested_amount:,.2f} per month**, "
                    "provided your emergency fund and essential "
                    "goals are adequately funded.\n\n"
                    f"Your investment readiness is currently "
                    f"**{readiness_text}**."
                )

        # =========================================================
        # 3. INVESTMENT ADVICE
        # =========================================================

        elif intent == "investment":

            if not is_ready:

                response = (
                    f"Hello {user_name}.\n\n"
                    "Based on your financial profile, you are currently "
                    "**NOT READY** for higher-risk investing.\n\n"
                    f"• Financial Health: **{health_status}**\n"
                    f"• Health Score: **{health_score}/100**\n"
                    f"• Monthly Savings: **₹{savings:,.2f}**\n"
                    f"• Emergency Fund: "
                    f"**{health.get('emergency_fund_ratio', 0)} months**\n\n"
                    "**Recommended next step:**\n"
                    "Build your emergency fund and maintain a positive "
                    "monthly cashflow before taking significant market risk."
                )

            elif "conservative" in risk.lower():

                response = (
                    "**Investment Suggestions for a Conservative Profile**\n\n"
                    "1. **Fixed Income:** "
                    "Bank FDs and suitable government-backed options.\n\n"
                    "2. **Debt Funds:** "
                    "Consider suitable high-quality debt funds.\n\n"
                    "3. **Gold:** "
                    "Consider gold as a diversification component.\n\n"
                    "4. **Index Funds:** "
                    "A smaller allocation to broad-market equity.\n\n"
                    "⚠️ Educational information only. "
                    "Market-linked investments can lose value."
                )

            elif "aggressive" in risk.lower():

                response = (
                    "**Investment Suggestions for an Aggressive Profile**\n\n"
                    "1. **Diversified Equity Funds**\n"
                    "2. **Flexi-Cap Funds**\n"
                    "3. **Mid/Small-Cap Exposure**\n"
                    "4. **International Diversification**\n"
                    "5. **Debt/Liquid Allocation for Stability**\n\n"
                    "⚠️ Higher potential returns come with higher risk."
                )

            else:

                response = (
                    "**Investment Suggestions for a Moderate Profile**\n\n"
                    "1. **Large-Cap / Index Funds** – "
                    "core growth allocation.\n\n"
                    "2. **Flexi-Cap Funds** – "
                    "diversified equity exposure.\n\n"
                    "3. **Hybrid Funds** – "
                    "combination of equity and debt.\n\n"
                    "4. **Debt / Fixed Income** – "
                    "stability.\n\n"
                    "5. **Gold** – diversification.\n\n"
                    "⚠️ Market-linked investments involve risk."
                )

        # =========================================================
        # 4. RISK PROFILE
        # =========================================================

        elif intent == "risk_profile":

            response = (
                "**Your Investment Risk Profile**\n\n"
                "Your current evaluated risk level is:\n\n"
                f"### **{risk}**\n\n"
                "This profile is used to determine how much investment "
                "risk may be appropriate for your financial situation.\n\n"
                "It considers factors such as financial stability, "
                "investment experience and risk tolerance."
            )

        # =========================================================
        # 5. FINANCIAL GOALS
        # =========================================================

        elif intent == "goals":

            if not user_goals:

                response = (
                    f"You currently don't have any financial goals, "
                    f"{user_name}.\n\n"
                    "You can create goals such as:\n"
                    "• Emergency Fund\n"
                    "• Laptop Purchase\n"
                    "• Education\n"
                    "• Travel\n"
                    "• Long-term Savings"
                )

            elif (
                "prioritize" in msg
                or "which goal" in msg
                or "goal priority" in msg
            ):

                priority_order = sorted(
                    user_goals,
                    key=lambda g: (
                        {
                            "High": 1,
                            "Medium": 2,
                            "Low": 3
                        }.get(
                            g.get("priority"),
                            2
                        ),
                        -float(g.get("remaining", 0))
                    )
                )

                response = (
                    "**Your Goal Priority Analysis**\n\n"
                )

                for index, goal in enumerate(
                    priority_order,
                    1
                ):

                    response += (
                        f"{index}. **{goal.get('name', 'Unnamed Goal')}**\n"
                        f"   Priority: **{goal.get('priority', 'Medium')}**\n"
                        f"   Progress: **{goal.get('progress_pct', 0)}%**\n"
                        f"   Status: **{goal.get('status', 'Active')}**\n\n"
                    )

                response += (
                    "💡 **Recommendation:** Focus first on "
                    "high-priority essential goals, especially "
                    "emergency savings."
                )

            elif (
                "how much" in msg
                or "save every month" in msg
                or "how much should i save" in msg
            ):

                response = (
                    "**Monthly Savings Required for Your Goals**\n\n"
                )

                active_found = False

                for goal in user_goals:

                    if not goal.get("completed", False):

                        active_found = True

                        response += (
                            f"• **{goal.get('name', 'Unnamed Goal')}**\n"
                            f"  Remaining: "
                            f"₹{float(goal.get('remaining', 0)):,.2f}\n"
                            f"  Monthly required: "
                            f"₹{float(goal.get('monthly_required', 0)):,.2f}\n"
                            f"  Progress: "
                            f"{goal.get('progress_pct', 0)}%\n"
                            f"  Status: **{goal.get('status', 'Active')}**\n\n"
                        )

                if not active_found:

                    response += (
                        "🎉 All your current financial goals "
                        "are completed."
                    )

                else:

                    response += (
                        "Your current recorded monthly savings are "
                        f"approximately **₹{savings:,.2f}**."
                    )

            else:

                response = (
                    "**Your Financial Goal Progress**\n\n"
                )

                for goal in user_goals:

                    response += (
                        f"• **{goal.get('name', 'Unnamed Goal')}**\n"
                        f"  Target: "
                        f"₹{float(goal.get('target_amount', 0)):,.2f}\n"
                        f"  Current: "
                        f"₹{float(goal.get('current_amount', 0)):,.2f}\n"
                        f"  Remaining: "
                        f"₹{float(goal.get('remaining', 0)):,.2f}\n"
                        f"  Progress: "
                        f"**{goal.get('progress_pct', 0)}%**\n"
                        f"  Status: "
                        f"**{goal.get('status', 'Active')}**\n"
                    )

                    monthly_required = float(
                        goal.get(
                            "monthly_required",
                            0
                        )
                    )

                    if monthly_required > 0:

                        response += (
                            f"  Required monthly saving: "
                            f"₹{monthly_required:,.2f}\n"
                        )

                    response += "\n"

        # =========================================================
        # 6. SAVINGS
        # =========================================================

        elif intent == "savings":

            response = (
                "Here are 4 targeted strategies based on your "
                "current cashflow:\n\n"
                f"**Monthly Income:** ₹{income:,.2f}\n"
                f"**Monthly Expenses:** ₹{expenses:,.2f}\n"
                f"**Current Savings:** ₹{savings:,.2f}\n\n"
                "1. **Apply the 50/30/20 Rule**\n"
                "   Aim for roughly 50% needs, 30% wants and "
                "20% savings where your income allows.\n\n"
                "2. **Audit Recurring Expenses**\n"
                "   Review subscriptions, dining and unnecessary spending.\n\n"
                "3. **Set Category Budgets**\n"
                "   Configure spending limits in the Budget module.\n\n"
                "4. **Automate Goal Contributions**\n"
                "   Treat your savings contribution as a regular "
                "monthly bill."
            )

        # =========================================================
        # 7. BUDGET
        # =========================================================

        elif intent == "budget":

            budget_row = query_db(
                """
                SELECT total_budget
                FROM budgets
                WHERE user_id = %s
                ORDER BY id DESC
                LIMIT 1
                """,
                (user_id,),
                one=True
            )

            budget = (
                float(budget_row["total_budget"])
                if budget_row
                and budget_row["total_budget"] is not None
                else 0.0
            )

            if budget <= 0:

                response = (
                    "**Budget Analysis**\n\n"
                    "You currently do not have an active "
                    "budget configured.\n\n"
                    "I recommend creating a monthly budget based "
                    "on your expected income and essential expenses."
                )

            else:

                utilization = FinancialCalculator.budget_utilization(
                    expenses,
                    budget
                )

                remaining_budget = max(
                    0,
                    budget - expenses
                )

                response = (
                    "**Your Budget Status**\n\n"
                    f"• Budget: ₹{budget:,.2f}\n"
                    f"• Spending: ₹{expenses:,.2f}\n"
                    f"• Remaining: ₹{remaining_budget:,.2f}\n"
                    f"• Utilization: {utilization}%\n\n"
                )

                if utilization > 100:

                    response += (
                        "⚠️ You have exceeded your current budget."
                    )

                elif utilization >= 80:

                    response += (
                        "⚠️ You have used most of your available budget."
                    )

                else:

                    response += (
                        "✅ Your spending is currently within your budget."
                    )

        # =========================================================
        # 8. PORTFOLIO
        # =========================================================

        elif intent == "portfolio":

            holdings = ctx.get(
                "holdings",
                []
            )

            if not holdings:

                response = (
                    "**Your Portfolio**\n\n"
                    "You currently have no recorded "
                    "portfolio holdings."
                )

            else:

                response = (
                    "**Your Current Portfolio**\n\n"
                )

                for holding in holdings:

                    response += (
                        f"• **{holding.get('symbol', '')}** — "
                        f"{holding.get('company_name', '')}\n"
                        f"  Quantity: {holding.get('quantity', 0)}\n"
                        f"  Buy Price: "
                        f"₹{float(holding.get('buy_price', 0)):,.2f}\n\n"
                    )

        # =========================================================
        # 9. WHAT-IF ANALYSIS
        # =========================================================

        elif intent == "what_if":

            # -----------------------------------------------------
            # Extract numbers from message
            # Handles:
            # 5000
            # 5,000
            # 5000.50
            # -----------------------------------------------------

            number_matches = re.findall(
                r"\d+(?:,\d{3})*(?:\.\d+)?",
                msg
            )

            numbers = []

            for value in number_matches:

                try:
                    numbers.append(
                        float(value.replace(",", ""))
                    )
                except ValueError:
                    continue

            amount = (
                numbers[0]
                if numbers
                else 0.0
            )

            # -----------------------------------------------------
            # Default period = 12 months
            # -----------------------------------------------------

            months = 12

            # -----------------------------------------------------
            # Check months
            # Example:
            # for 12 months
            # 12 month
            # 12 mo
            # -----------------------------------------------------

            month_match = re.search(
                r"(\d+(?:\.\d+)?)\s*(?:months?|mos?|mo)\b",
                msg
            )

            # -----------------------------------------------------
            # Check years
            # Example:
            # for 2 years
            # 2 year
            # 2 yrs
            # -----------------------------------------------------

            year_match = re.search(
                r"(\d+(?:\.\d+)?)\s*(?:years?|yrs?|yr)\b",
                msg
            )

            if month_match:

                months = int(
                    float(
                        month_match.group(1)
                    )
                )

            elif year_match:

                months = int(
                    float(
                        year_match.group(1)
                    ) * 12
                )

            # Prevent invalid periods

            if months <= 0:
                months = 12

            # -----------------------------------------------------
            # NO AMOUNT
            # -----------------------------------------------------

            if amount <= 0:

                response = (
                    "**Financial What-If Analysis**\n\n"
                    "I can estimate scenarios such as:\n\n"
                    "• What happens if I save ₹5,000 every month?\n"
                    "• What happens if I invest ₹2,000 every month?\n"
                    "• What happens if I increase my savings?\n\n"
                    "Tell me the amount and time period and I can "
                    "calculate an educational estimate."
                )

            # -----------------------------------------------------
            # SAVING SCENARIO
            # -----------------------------------------------------

            elif (
                "save" in msg
                or "saving" in msg
                or "savings" in msg
            ):

                total_saved = amount * months

                response = (
                    "**Financial What-If Analysis**\n\n"
                    f"If you save **₹{amount:,.2f} per month** "
                    f"for **{months} months**:\n\n"
                    f"• Monthly saving: ₹{amount:,.2f}\n"
                    f"• Time period: {months} months\n"
                    f"• Total amount saved: "
                    f"**₹{total_saved:,.2f}**\n\n"
                    "This is a simple savings estimate and does "
                    "not include investment returns or interest."
                )

            # -----------------------------------------------------
            # INVESTMENT SCENARIO
            # -----------------------------------------------------

            elif (
                "invest" in msg
                or "investment" in msg
            ):

                future_value = (
                    FinancialCalculator.future_investment_value(
                        monthly_investment=amount,
                        months=months,
                        annual_return_rate=10
                    )
                )

                total_invested = amount * months

                estimated_growth = (
                    future_value - total_invested
                )

                response = (
                    "**Financial What-If Analysis**\n\n"
                    f"If you invest **₹{amount:,.2f} per month** "
                    f"for **{months} months**:\n\n"
                    f"• Monthly investment: ₹{amount:,.2f}\n"
                    f"• Time period: {months} months\n"
                    f"• Total amount invested: "
                    f"₹{total_invested:,.2f}\n"
                    f"• Estimated future value: "
                    f"**₹{future_value:,.2f}**\n"
                    f"• Estimated growth: "
                    f"**₹{estimated_growth:,.2f}**\n\n"
                    "⚠️ This is an educational estimate using an "
                    "assumed 10% annual return. Actual investment "
                    "returns are not guaranteed."
                )

            # -----------------------------------------------------
            # INCREASE SAVINGS SCENARIO
            # -----------------------------------------------------

            elif "increase" in msg:

                new_savings = (
                    savings + amount
                )

                response = (
                    "**Financial What-If Analysis**\n\n"
                    f"Your current monthly savings are "
                    f"₹{savings:,.2f}.\n\n"
                    f"If you increase your savings by "
                    f"₹{amount:,.2f} per month:\n\n"
                    f"• Current savings: ₹{savings:,.2f}\n"
                    f"• Increase: ₹{amount:,.2f}\n"
                    f"• New monthly savings: "
                    f"**₹{new_savings:,.2f}**\n\n"
                    "Increasing your monthly savings can help you "
                    "reach your financial goals faster."
                )

            # -----------------------------------------------------
            # UNKNOWN WHAT-IF
            # -----------------------------------------------------

            else:

                response = (
                    "**Financial What-If Analysis**\n\n"
                    f"You entered an amount of "
                    f"**₹{amount:,.2f}**.\n\n"
                    "Try asking:\n"
                    "• What if I save ₹5,000 every month for 12 months?\n"
                    "• What if I invest ₹2,000 every month for 2 years?\n"
                    "• What if I increase my savings by ₹3,000?"
                )

        # =========================================================
        # 10. STOCK ANALYSIS
        # =========================================================

        elif intent == "stocks" or any(
            symbol in msg.upper()
            for symbol in [
                "TCS",
                "INFY",
                "RELIANCE",
                "HDFCBANK",
                "ITC",
                "TATAMOTORS",
                "ZOMATO",
                "AAPL",
                "MSFT",
                "NVDA"
            ]
        ):

            symbols = [
                "TCS",
                "INFY",
                "RELIANCE",
                "HDFCBANK",
                "ITC",
                "TATAMOTORS",
                "ZOMATO",
                "AAPL",
                "MSFT",
                "NVDA"
            ]

            matched_sym = next(
                (
                    symbol
                    for symbol in symbols
                    if symbol in msg.upper()
                ),
                None
            )

            if not matched_sym:

                response = (
                    "Please provide a stock symbol, for example "
                    "**TCS**, **INFY**, **RELIANCE**, or **ITC**."
                )

            else:

                try:

                    analysis = analyze_stock_suitability(
                        user_id,
                        matched_sym
                    )

                    stock = analysis["stock"]

                    response = (
                        f"**Stock Analysis: "
                        f"{stock['name']} ({stock['symbol']})**\n\n"
                        f"• **Current Price:** "
                        f"₹{float(stock['price']):,.2f} "
                        f"({float(stock['pct_change']):+0.2f}%)\n"
                        f"• **Sector:** {stock['sector']}\n"
                        f"• **Market Cap:** "
                        f"{stock['market_cap']}\n"
                        f"• **Risk Rating:** "
                        f"{stock['risk_rating']}\n"
                        f"• **P/E:** {stock['pe']}\n"
                        f"• **AI Suitability:** "
                        f"**{analysis['suitability_status']}**\n\n"
                        f"**Rationale:** "
                        f"{analysis['guidance']}\n\n"
                        "⚠️ Educational information only. "
                        "Stock prices can rise or fall."
                    )

                except Exception as exc:

                    response = (
                        f"I couldn't complete the stock analysis "
                        f"for **{matched_sym}** right now.\n\n"
                        f"Technical reason: {str(exc)}"
                    )

        # =========================================================
        # 11. MUTUAL FUNDS VS STOCKS
        # =========================================================

        elif any(
            phrase in msg
            for phrase in [
                "difference between mutual funds and stocks",
                "mutual fund vs stock",
                "stocks vs mutual funds"
            ]
        ):

            response = (
                "**Mutual Funds vs Direct Stocks**\n\n"
                "1. **Diversification:** Mutual funds hold multiple "
                "securities, while a stock represents ownership "
                "in one company.\n\n"
                "2. **Management:** Mutual funds are managed "
                "according to their stated investment strategy.\n\n"
                "3. **Risk:** Individual stocks can be more volatile "
                "than diversified funds.\n\n"
                "4. **Suitability:** Diversified funds can be easier "
                "for beginners who do not want to research "
                "individual companies."
            )

        # =========================================================
        # 12. SIP
        # =========================================================

        elif any(
            phrase in msg
            for phrase in [
                "what is sip",
                "explain sip",
                "systematic investment plan"
            ]
        ):

            response = (
                "**What is a Systematic Investment Plan (SIP)?**\n\n"
                "An SIP is a method of investing a fixed amount "
                "into a mutual fund at regular intervals, "
                "commonly monthly.\n\n"
                "**Advantages:**\n"
                "• Encourages investing discipline.\n"
                "• Helps spread purchases over time.\n"
                "• Can support long-term compounding.\n\n"
                "SIP returns are not guaranteed."
            )

        # =========================================================
        # 13. BONDS
        # =========================================================

        elif any(
            phrase in msg
            for phrase in [
                "what are bonds",
                "explain bonds",
                "what is debenture",
                "fixed income"
            ]
        ):

            response = (
                "**What are Bonds and Fixed-Income Securities?**\n\n"
                "A bond is a debt instrument where an investor "
                "lends money to an issuer for a defined period.\n\n"
                "• Government securities generally have lower "
                "credit risk.\n"
                "• Corporate bonds have issuer-specific credit risk.\n"
                "• Fixed-income investments can provide stability "
                "and income."
            )

        # =========================================================
        # 14. ETF
        # =========================================================

        elif any(
            phrase in msg
            for phrase in [
                "what is etf",
                "explain etf"
            ]
        ):

            response = (
                "**What is an ETF?**\n\n"
                "An Exchange Traded Fund is a fund that trades "
                "on a stock exchange and usually tracks an index, "
                "sector, commodity or other underlying asset.\n\n"
                "ETFs can provide diversification and generally "
                "have transparent holdings, but they still carry "
                "investment risk."
            )

        # =========================================================
        # 15. DEFAULT RESPONSE
        # =========================================================

        else:

            readiness_text = (
                "Ready for Consideration"
                if is_ready
                else "Not Ready"
            )

            response = (
                f"Hello {user_name}! I am your **FinAI Assistant**.\n\n"
                "I have analyzed your current financial profile:\n\n"
                f"• **Monthly Income:** ₹{income:,.2f}\n"
                f"• **Monthly Expenses:** ₹{expenses:,.2f}\n"
                f"• **Savings:** ₹{savings:,.2f}\n"
                f"• **Financial Health:** "
                f"**{health_status} ({health_score}/100)**\n"
                f"• **Risk Profile:** **{risk}**\n"
                f"• **Investment Readiness:** "
                f"**{readiness_text}**\n"
                f"• **Financial Goals:** {len(user_goals)}\n\n"
                "You can ask me:\n"
                "• 'Show me my financial goals'\n"
                "• 'How is my financial health?'\n"
                "• 'How can I improve my savings?'\n"
                "• 'Can I afford to invest?'\n"
                "• 'What is my risk profile?'\n"
                "• 'Where should I invest?'\n"
                "• 'Tell me about TCS'\n"
                "• 'Show me my portfolio'\n"
                "• 'What if I save ₹5,000 every month for 12 months?'\n"
                "• 'What if I invest ₹2,000 every month for 2 years?'"
            )

        # =========================================================
        # SAVE CONVERSATION
        # =========================================================

        try:

            execute_db(
                """
                INSERT INTO ai_conversations
                (
                    user_id,
                    user_message,
                    ai_response,
                    context_used_json
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    user_id,
                    user_message,
                    response,
                    json.dumps(
                        {
                            "intent": intent,
                            "health_score": health_score,
                            "health_status": health_status,
                            "risk": risk,
                            "is_ready": is_ready
                        }
                    )
                )
            )

        except Exception as exc:

            print(
                f"Warning: Could not save AI conversation: {exc}"
            )

        return response