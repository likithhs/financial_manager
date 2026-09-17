import json
import re

from database import query_db, execute_db

from ai.financial_analyzer import evaluate_user_financial_health
from ai.investment_readiness import evaluate_investment_readiness
from ai.intent_classifier import IntentClassifier
from ai.financial_calculator import FinancialCalculator
from ai.goal_analyzer import GoalAnalyzer
from ai.stock_recommender import analyze_stock_suitability
from services.ai_service import AIService
from ai.sentiment_engine import SentimentEngine
from ai.conversational_engine import ConversationalEngine


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
    # FINANCIAL DOMAIN GUARDRAIL
    # =============================================================

    @staticmethod
    def is_financial_domain_query(user_message):
        """
        Enforces strict domain boundaries:
        Only personal finance, budgeting, investments, goals, cashflow, debt,
        and financial education are allowed. General non-financial questions
        (coding, trivia, sports, cooking, politics, pop culture) are refused.
        """
        if not user_message:
            return False

        msg = user_message.strip().lower()

        # Allow basic greetings and conversational starters
        greetings = [
            "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
            "who are you", "what can you do", "help", "how does this work",
            "what is finai", "tell me about yourself", "start"
        ]
        if any(msg == g or msg.startswith(g + " ") or msg.endswith(" " + g) for g in greetings):
            return True

        # Clear Non-Financial Keywords / Patterns (Instant Refusal)
        non_financial_patterns = [
            r"\b(python|javascript|typescript|c\+\+|java|golang|rust|ruby|php|swift|kotlin|html|css|sql|coding|code|script|algorithm|leetcode|bug|debug|function|compiler|github|git|software)\b",
            r"\b(recipe|recipes|cook|cooking|bake|baking|ingredients|dish|dishes|curry|pasta|pizza|cake|soup|dessert|sandwich)\b",
            r"\b(cricket|football|soccer|basketball|tennis|ipl|fifa|messi|ronaldo|world cup|match score|tournament|stadium|wicket|scorecard|gaming|minecraft|playstation)\b",
            r"\b(movie|movies|actor|actress|hollywood|bollywood|song|songs|lyrics|sing a song|sing|poem|poems|poetry|write a story|novel|fiction|joke|jokes|riddle)\b",
            r"\b(capital of|president of|prime minister of|history of|solar system|planet|astronomy|weather in|temperature today|rain tomorrow|geography)\b",
            r"\b(write an essay|solve physics|solve chemistry|biology|homework)\b",
            r"\b(diagnose my|medical advice|symptoms of|prescription|headache|fever|cough)\b",
            r"\b(fix my car|car engine|engine repair|mechanic|plumbing|leaking pipe|appliance repair)\b",
            r"\b(legal lawsuit|divorce lawyer|traffic ticket)\b"
        ]

        for pattern in non_financial_patterns:
            if re.search(pattern, msg):
                return False

        # Permitted Financial Domain Keywords & Phrases
        financial_keywords = [
            "income", "salary", "earn", "earning", "compensation", "revenue", "paycheck",
            "expense", "expenses", "spending", "spend", "spent", "cost", "bill", "bills",
            "budget", "budgeting", "save", "savings", "surplus", "deficit", "cashflow", "cash flow",
            "emergency", "reserve", "reserves", "liquidity", "buffer", "safety net",
            "invest", "investing", "investment", "investments", "investor",
            "readiness", "ready to invest", "afford to invest",
            "stock", "stocks", "share", "shares", "equity", "equities",
            "mutual fund", "mutual funds", "mf", "sip", "sips", "etf", "etfs",
            "bond", "bonds", "debenture", "fixed deposit", "fixed deposits", "fd", "fds",
            "gold", "silver", "commodity", "crypto", "cryptocurrency", "bitcoin",
            "portfolio", "diversify", "diversification", "allocation", "asset allocation",
            "dividend", "dividends", "yield", "capital gain", "capital gains",
            "nifty", "sensex", "market", "bull", "bear", "rally", "correction", "crash",
            "goal", "goals", "target", "milestone", "retire", "retirement", "pension", "fire",
            "wealth", "wealth building", "net worth", "worth", "rich", "crorepati", "millionaire",
            "compound", "compounding", "interest", "return", "returns", "roi", "cagr",
            "debt", "debts", "loan", "loans", "borrow", "borrowing", "emi", "emis", "credit", "credit score", "cibil",
            "tax", "taxes", "taxation", "80c", "deduction", "itr", "inflation",
            "risk", "risk profile", "risk tolerance", "conservative", "moderate", "aggressive",
            "health score", "financial health", "score", "pillar", "diagnostics",
            "rupee", "rupees", "rs", "inr", "lakh", "crore", "money", "cash", "finance", "financial",
            "tcs", "infosys", "infy", "reliance", "hdfc", "icici", "wipro", "itc", "sbi", "tatamotors", "tata",
            "what if i save", "what if i invest", "how much can i", "should i buy", "should i invest", "where to invest",
            # Human sentiment & personal life finance
            "stressed", "stress", "anxious", "anxiety", "worried", "worry", "scared", "fear", "afraid",
            "overwhelmed", "broke", "struggling", "struggle", "excited", "lost", "confused", "guilt", "regret",
            "advice", "advise", "guide", "guidance", "future", "dream", "dreams", "lifestyle", "career",
            "afford", "buy a car", "afford a car", "car loan", "car emi", "buy a house", "buy a home",
            "home loan", "mortgage", "marriage", "wedding", "baby", "children",
            "college", "insurance", "freedom", "independence", "pension"
        ]

        # Extract words to guarantee word-boundary matching (prevents e.g. 'rs' in 'reverse')
        words = set(re.findall(r"\b[a-z0-9_]+\b", msg))

        for kw in financial_keywords:
            if " " in kw:
                if kw in msg:
                    return True
            else:
                if kw in words:
                    return True

        if re.search(r"(₹|\brs\.?|\binr\b|\$|\b\d+k\b|\blakh|\bcrore)", msg):
            return True

        return False

    # =============================================================
    # SYSTEM PROMPT BUILDER (WITH LIVE FINANCIAL CONTEXT)
    # =============================================================

    @staticmethod
    def build_system_prompt(ctx):
        """Constructs an exhaustive financial advisory system prompt with live user metrics."""
        user = ctx.get("user") or {}
        health = ctx.get("health") or {}
        readiness = ctx.get("readiness") or {}
        risk_level = ctx.get("risk_level", "Moderate")
        goals = ctx.get("goals") or []
        holdings = ctx.get("holdings") or []

        user_name = user.get("name", "User")
        income = float(health.get("total_income", 0))
        expenses = float(health.get("total_expenses", 0))
        savings = float(health.get("savings", 0))
        savings_rate = float(health.get("savings_rate", 0))
        health_score = health.get("score", 0)
        health_status = health.get("health_status", "Unknown")
        emergency_months = health.get("emergency_fund_ratio", 0)
        is_ready = readiness.get("is_ready", False)

        goals_summary = []
        for g in goals[:5]:
            name = g.get('goal_name') or g.get('name', 'Goal')
            target = float(g.get('target_amount', 0))
            saved = float(g.get('current_amount', 0))
            pct = round((saved / target * 100), 1) if target > 0 else 0
            goals_summary.append(f"- {name}: ₹{saved:,.0f} / ₹{target:,.0f} ({pct}%, Priority: {g.get('priority', 'Medium')})")

        holdings_summary = []
        for h in holdings[:5]:
            sym = h.get('symbol', '')
            qty = h.get('quantity', 0)
            avg = float(h.get('buy_price', 0))
            holdings_summary.append(f"- {sym}: {qty} shares @ ₹{avg:,.2f}")

        prompt = f"""You are FinAI, an empathetic, world-class Certified Financial Planner (CFP), wealth strategist, and behavioral finance coach.
You communicate with the natural warmth, emotional intelligence, conversational brilliance, and nuance of ChatGPT.

=== CORE PERSONA & BEHAVIORAL INTELLIGENCE ===
1. Emotional Resonance & Empathy First:
   People's relationship with money is deeply personal and emotional.
   - If the user expresses stress, anxiety, worry, or fear (e.g. debt burden, bills, fear of market crashes, feeling broke): ALWAYS validate their feelings with sincere compassion and reassurance first. Remind them that financial challenges are solvable step-by-step.
   - If the user expresses ambition, excitement, or big dreams (e.g. becoming rich, retiring early, 10x returns): Match their positive energy and channel it into proven, disciplined compounding strategies.
   - If the user expresses confusion or feels like a beginner: Strip away Wall Street jargon and explain concepts using intuitive, relatable everyday analogies.
   - If the user expresses guilt or regret (e.g. bad investment, impulse spending): Offer grace. Treat past mistakes as valuable learning experiences and focus on the forward path.

2. Natural Human Dialogue (Not Robotic Predefined Responses):
   - Speak naturally like a caring, brilliant mentor sitting across a coffee table.
   - Use engaging transitions, fluid paragraphs, and thoughtful storytelling.
   - Break answers down into clean markdown sections (headers, bullet points, bold key takeaways).
   - Conclude every response with an open, friendly follow-up question that invites continued dialogue.

3. Strict Domain Focus:
   - Your expertise is strictly dedicated to personal finance, budgeting, emergency reserves, cashflow, debt elimination, mutual funds, stocks, financial goals, retirement, and tax optimization.
   - If the user asks something completely outside personal finance (e.g., coding, sports scores, cooking recipes, general pop culture):
     Politely decline with warmth: "I'd love to chat, but as your personal FinAI Financial Advisor, my specialty is strictly dedicated to the Financial Advisory & Wealth Management domain. Let's focus on your savings, investments, or any financial questions you have on your mind!"

=== USER'S LIVE FINANCIAL DASHBOARD (GROUND YOUR ADVICE HERE) ===
User Name: {user_name}
• Total Monthly Income: ₹{income:,.2f}
• Total Monthly Expenses: ₹{expenses:,.2f}
• Monthly Net Savings: ₹{savings:,.2f}
• Savings Rate: {savings_rate:.1f}%
• 6-Pillar Financial Health Score: {health_score}/100 ({health_status})
• Emergency Fund Coverage: {emergency_months:.1f} months of living expenses
• Behavioral Risk Profile: {risk_level}
• Investment Readiness Verdict: {"READY for disciplined market investing" if is_ready else "FOCUS ON SAFETY FIRST - build emergency reserve and positive monthly cashflow before taking high market risk"}

Active Financial Goals:
{chr(10).join(goals_summary) if goals_summary else "No active financial goals logged yet."}

Current Portfolio Holdings:
{chr(10).join(holdings_summary) if holdings_summary else "No active equity holdings recorded."}

=== GUIDELINES FOR ACTION ===
- Always address {user_name} warmly by name.
- Always use the Indian Rupee symbol (₹) for calculations and numbers.
- Provide practical, realistic, life-friendly steps.
- Remind users that market investments carry market risk and guidance is educational."""
        return prompt

    # =============================================================
    # DB PERSISTENCE HELPER
    # =============================================================

    @staticmethod
    def _save_conversation(user_id, user_message, response, context_data=None):
        """Persist conversation exchange to database."""
        try:
            execute_db(
                """
                INSERT INTO ai_conversations
                (user_id, user_message, ai_response, context_used_json)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    user_id,
                    user_message,
                    response,
                    json.dumps(context_data or {})
                )
            )
        except Exception as exc:
            print(f"Warning: Could not save AI conversation: {exc}")

    # =============================================================
    # MAIN ORCHESTRATOR FUNCTION
    # =============================================================

    @staticmethod
    def respond(user_id, user_message, return_meta=False):
        """
        Process a user's financial question and return a response.
        Enforces domain guardrails, attempts external multi-provider LLM,
        and falls back to local Conversational Intelligence Engine.
        """
        ctx = FinAIAssistant.get_user_full_context(user_id)
        user_name = ctx["user"]["name"] if ctx.get("user") else "Investor"

        # 1. Strict Financial Domain Guardrail
        if not FinAIAssistant.is_financial_domain_query(user_message):
            refusal = (
                f"Hello {user_name}! I would love to chat, but as your specialized **FinAI Financial Assistant**, "
                "my capabilities and expertise are strictly dedicated to the **Financial Advisory & Wealth Management domain**.\n\n"
                "I am here to help you master your money—including cashflow optimization, budgeting, emergency reserves, "
                "6-pillar health diagnostics, investment readiness, mutual funds, stocks, debt freedom, and retirement goals.\n\n"
                "What personal finance question or goal can we work on together today?"
            )
            FinAIAssistant._save_conversation(user_id, user_message, refusal, {"guardrail_triggered": True})
            return (refusal, "FinAI Domain Guardrail") if return_meta else refusal

        # 2. Attempt External Multi-Provider LLM (Gemini, OpenAI, Groq)
        if AIService.is_api_configured():
            try:
                system_prompt = FinAIAssistant.build_system_prompt(ctx)
                history_rows = query_db(
                    """
                    SELECT user_message, ai_response 
                    FROM ai_conversations 
                    WHERE user_id = %s 
                    ORDER BY id DESC LIMIT 4
                    """,
                    (user_id,)
                )
                chat_history = list(reversed(history_rows)) if history_rows else []
                
                llm_reply = AIService.generate_response(system_prompt, user_message, chat_history)
                if llm_reply:
                    provider_info = AIService.get_provider_status()
                    provider_name = provider_info.get("display_name", "AI Engine")
                    FinAIAssistant._save_conversation(user_id, user_message, llm_reply, {"provider": provider_name})
                    return (llm_reply, provider_name) if return_meta else llm_reply
            except Exception as e:
                print(f"External LLM invocation failed, falling back to local: {e}")

        # 3. Conversational Engine (ChatGPT Caliber with Sentiment Awareness)
        local_reply = ConversationalEngine.generate_chat_response(user_id, user_message, ctx)
        sentiment_info = SentimentEngine.analyze_sentiment(user_message)
        provider_label = "FinAI Conversational Engine"
        FinAIAssistant._save_conversation(
            user_id,
            user_message,
            local_reply,
            {"provider": provider_label, "sentiment": sentiment_info.get("sentiment")}
        )
        return (local_reply, provider_label) if return_meta else local_reply

    # =============================================================
    # LOCAL CONVERSATIONAL ENGINE (FALLBACK)
    # =============================================================

    @staticmethod
    def respond_local(user_id, user_message, ctx=None):
        """
        Built-in conversational assistant powered by ConversationalEngine.
        """
        if not ctx:
            ctx = FinAIAssistant.get_user_full_context(user_id)
        reply = ConversationalEngine.generate_chat_response(user_id, user_message, ctx)
        sentiment_info = SentimentEngine.analyze_sentiment(user_message)
        return reply, {
            'sentiment': sentiment_info.get('sentiment'),
            'provider': 'FinAI Conversational Engine'
        }
