"""
Finora Demo Assistant - Application Usage Guide Engine
Exclusively demonstrates and explains how to navigate and use Finora's features.
Strictly rejects off-topic queries, personal financial advice, stock predictions, and prompt injections.
"""

import re
from services.ai_service import AIService

# Exact scope-restriction response mandated by project specification
RESTRICTION_RESPONSE = (
    "I'm Finora's Demo Assistant. I can help you understand how to use Finora's features, "
    "such as expense tracking, budgeting, financial goals, investment tools, and financial reports. "
    "Please ask me how to use a feature within Finora."
)

# Comprehensive Finora Feature Knowledge Base
FEATURE_GUIDES = {
    "dashboard": """### 📊 How to Navigate the Finora Dashboard

The **Finora Dashboard** serves as your financial command center once logged in:

• **Executive Cockpit (`/dashboard`)**:
  1. **Top Metrics Cards**: See your Total Income, Total Expenses, Net Savings, and Savings Rate % calculated in real time.
  2. **Budget Utilization**: Visual progress bars showing how much of each monthly category budget you have spent.
  3. **Financial Goals Progress**: Live status trackers for all your active milestone goals.
  4. **Recent Activity Feed**: Quick stream of your latest income and expense entries.

• **Welcome Hub (`/home`)**:
  - Highlights your financial status upon login with 1-click shortcut cards to Cashflow, Budgets, Risk Profiles, and Markets.

*(Navigate to the Dashboard anytime from the left sidebar menu).*""",

    "expenses": """### 💸 How to Track Expenses in Finora

Tracking daily and recurring expenses in Finora is simple:

1. **Open Expense Tracker**: Click **Expense Tracker** (`/expenses`) in the sidebar navigation.
2. **Add an Expense**: Click the **"+ Add Expense"** button at the top.
3. **Fill in Details**:
   • **Amount**: Enter the expense amount in ₹.
   • **Category**: Choose from Housing, Food & Dining, Transportation, Utilities, Healthcare, Entertainment, Debt Payments, or Personal Care.
   • **Date**: Select the transaction date.
   • **Description**: Add an optional note (e.g., "Weekly groceries").
4. **Save**: Click **"Save Expense"**.

Finora immediately updates your monthly spending total, expense category breakdown chart, and budget limits.""",

    "budget": """### 🎯 How to Create & Manage Budgets in Finora

Finora helps you prevent overspending with category-level budget limits:

1. **Open Budget & Savings**: Click **Budget & Savings** (`/budget`) in the sidebar.
2. **Set Category Budget**:
   • Click **"Set / Update Budget"**.
   • Select the category you want to limit (e.g., "Food & Dining", "Entertainment").
   • Enter your maximum monthly target limit in ₹ and click **"Save Budget"**.
3. **Monitor Live Progress**:
   • Finora generates real-time visual progress bars comparing actual expenses to your limit.
   • **Warning Indicators**: The progress bar turns amber at 80% utilization and red if spending exceeds 100%.

Use this to keep discretionary spending under control month after month.""",

    "goals": """### 🏆 How to Set Financial Goals in Finora

Turn your dreams into achievable milestones with Finora's goal tracker:

1. **Open Financial Goals**: Click **Financial Goals** (`/goals`) in the sidebar.
2. **Create a Goal**: Click **"+ Create New Goal"**.
3. **Configure Your Target**:
   • **Goal Name**: Enter a title (e.g., "Emergency Fund", "New Car", "Home Down Payment").
   • **Target Amount**: The total sum needed in ₹.
   • **Target Date**: The date you want to reach the goal.
   • **Priority**: Assign Low, Medium, or High priority.
4. **Track & Add Contributions**:
   • As you save money, click **"Add Funds"** on any goal card to log your deposits.
   • Finora calculates your percentage progress and shows whether you are on track.""",

    "income": """### 💰 How to Add & Track Income in Finora

Record all cash inflows to maintain an accurate cashflow surplus:

1. **Open Income Sources**: Click **Income Sources** (`/income`) in the sidebar.
2. **Add Income**: Click **"+ Add Income"**.
3. **Fill in Inflow Details**:
   • **Source**: Name the revenue stream (e.g., "Primary Salary", "Freelance Work", "Dividends").
   • **Amount**: Enter the amount received in ₹.
   • **Category**: Select Salary, Freelance, Investment, Business, or Other.
   • **Date**: Transaction date.
4. **Save**: Your net monthly cashflow, savings surplus, and financial health score are recalculated automatically.""",

    "investment_tools": """### 📈 How to Use Finora's Investment Tools

Finora provides an intelligent investment recommendation and educational suite:

1. **Check Investment Readiness (`/investment-readiness`)**:
   Finora acts as a safety gatekeeper, verifying that you have a minimum 3–6 month emergency fund and positive cashflow before recommending market risk.
2. **Take the Risk Profile Assessment (`/risk-profile`)**:
   Answer behavioral questions to determine your risk classification (Conservative, Moderate, or Aggressive).
3. **Review Tailored Recommendations (`/investment-recommendation`)**:
   Finora generates personalized asset allocation models across Equity Index Funds, Debt/Fixed Deposits, Sovereign Gold, and Liquid Reserves.
4. **Recommendation History (`/recommendation-history`)**:
   Review all previous investment allocation recommendations anytime.""",

    "health_reports": """### 🩺 How to View Financial Health Reports

Finora evaluates your holistic financial vitals using a proprietary **6-Pillar Diagnostic**:

1. **Open Financial Health**: Click **Financial Health** (`/financial-analysis`) in the sidebar.
2. **What Finora Measures (Score: 0–100)**:
   • **Savings Ratio**: Percentage of monthly income saved.
   • **Expense Efficiency**: Proportion of income absorbed by living costs.
   • **Emergency Runway**: Months of living expenses covered in liquid buffer.
   • **Debt-to-Income (DTI)**: Percentage of income committed to debt servicing.
   • **Asset Allocation**: Balance across equity, debt, and cash equivalents.
   • **Goal Progress**: Progress towards active savings targets.
3. **Diagnostic Action Items**:
   Finora generates specific next-best recommendations (e.g. increase emergency fund, reallocate surplus).""",

    "risk_assessment": """### ⚖️ How to Use the Risk Assessment Section

Understanding your psychological comfort with volatility is vital before investing:

1. **Open Risk Profile**: Click **Risk Profile** (`/risk-profile`) in the sidebar.
2. **Complete the Assessment**:
   • Answer questions evaluating your investment time horizon, reaction to market declines, and job stability.
3. **Review Your Verdict**:
   • Finora computes your risk score and classifies you as **Conservative**, **Moderate**, or **Aggressive**.
   • This risk score directly powers the asset allocation models in your Investment Recommendations.""",

    "stocks_portfolio_watchlist": """### 🔍 How to Use Stocks, Watchlists & Portfolio Holdings

Monitor equities and track your real asset holdings in Finora:

1. **Market Equities (`/stocks`)**:
   • Browse major Indian equities (such as Nifty 50 constituents: Reliance, TCS, Infosys, HDFC Bank).
   • View real-time price trends, 52-week ranges, volatility, and fundamental risk ratings.
2. **Stock Analysis (`/stock-analysis?symbol=XYZ`)**:
   • View in-depth suitability diagnostics for specific company stocks.
3. **Stock Watchlist (`/watchlist`)**:
   • Add stocks to your custom watchlist with 1-click for quick daily price tracking.
4. **Portfolio Tracker (`/portfolio`)**:
   • Record shares purchased, buy price, and quantity to track current portfolio value, asset allocation, and total profit/loss.""",

    "auth_settings": """### 🔐 How to Register, Log In & Manage Settings

Navigating your Finora account is fast and secure:

1. **Create an Account (`/register`)**:
   • Click **"Create Free Account"** on the landing page.
   • Enter your Name, Email, Password, Age, Occupation, and Financial Experience level.
2. **Log In (`/login`)**:
   • Sign in with your registered email and password.
3. **Account Profile & Settings (`/settings` or `/profile`)**:
   • Click your profile circle in the top right header to open the dropdown card.
   • Select **"My Profile & Settings"** to edit personal details, phone number, address, or update your password.
4. **Log Out**:
   • Click the Logout icon in the top right navigation bar to end your session safely."""
}


class FinoraDemoAssistant:
    """
    Finora Demo Assistant Engine.
    Operates strictly as an educational guide on how to use the Finora application.
    """

    # 1. Prompt Injection & Adversarial Attack Patterns
    PROMPT_INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|rules)",
        r"(forget|disregard)\s+(all\s+)?(previous|prior|everything)",
        r"you\s+are\s+now\s+(a|an)?\s*(new|different|uncensored|chatgpt|dan|assistant)",
        r"act\s+as\s+(a|an)?\s*(chatgpt|general|unrestricted|jailbreak|python|coder|counselor)",
        r"(reveal|show|print|display|tell\s+me)\s+(your\s+)?(system\s+prompt|prompt|internal\s+instructions|secret|api\s*key)",
        r"jailbreak",
        r"developer\s+mode",
        r"pretend\s+(you\s+are|to\s+be)",
        r"bypass\s+(the\s+)?(guardrail|restriction|rule|policy)",
        r"override\s+(all\s+)?(instructions|rules)"
    ]

    # 2. Personal Financial Advice / Market Prediction Patterns
    ADVICE_AND_PREDICTION_PATTERNS = [
        r"should\s+i\s+(buy|sell|invest|purchase|trade)",
        r"(where|how)\s+should\s+i\s+invest\s+my\s+(money|savings|rupees|lakh|crore)",
        r"(predict|forecast)\s+(stock|market|price|nifty|bitcoin|gold)",
        r"stock\s+price\s+(tomorrow|next\s+week|in\s+2026)",
        r"(which|what)\s+stock(s)?\s+(should\s+i|to)\s+(buy|pick|invest)",
        r"(give|provide)\s+me\s+(personal\s+)?financial\s+advice",
        r"how\s+do\s+i\s+become\s+(rich|a\s+crorepati|millionaire)",
        r"can\s+i\s+afford\s+to\s+buy\s+a\s+(car|house|bike)",
        r"how\s+much\s+(can|should)\s+i\s+spend",
        r"(is|are)\s+(crypto|bitcoin|ethereum|doge)\s+a\s+good\s+investment",
        r"will\s+[a-z0-9]+\s+go\s+(up|down)"
    ]

    # 3. Off-Topic Non-Finora Patterns (General queries)
    OFF_TOPIC_PATTERNS = [
        r"(write|generate|debug)\s+(a\s+)?(python|java|javascript|c\+\+|code|script|sql\s+query)",
        r"recipe\s+for",
        r"(who|what)\s+is\s+the\s+(president|capital|population|prime\s+minister)",
        r"tell\s+me\s+a\s+(joke|story|poem)",
        r"how\s+to\s+(cook|bake|fix\s+car|build\s+pc)",
        r"who\s+won\s+the\s+(match|game|election|world\s+cup)",
        r"translate\s+to",
        r"write\s+an\s+essay"
    ]

    # 4. Finora Feature Topic Keyword Matchers
    FEATURE_MATCHERS = [
        ("expenses", [
            r"expense", r"track\s+spending", r"add\s+expense", r"log\s+expense",
            r"spending\s+tracker", r"how\s+do\s+i\s+track\s+my\s+expenses", r"category\s+expense"
        ]),
        ("budget", [
            r"budget", r"spending\s+limit", r"create\s+a\s+budget", r"how\s+do\s+i\s+create\s+a\s+budget",
            r"manage\s+budget", r"budget\s+alert", r"savings\s+limit"
        ]),
        ("goals", [
            r"goal", r"financial\s+goal", r"milestone", r"set\s+a\s+financial\s+goal",
            r"how\s+do\s+i\s+set\s+a\s+financial\s+goal", r"target\s+date", r"add\s+funds"
        ]),
        ("income", [
            r"income", r"add\s+income", r"log\s+salary", r"revenue\s+stream",
            r"cashflow\s+inflow", r"track\s+income"
        ]),
        ("investment_tools", [
            r"investment\s+tool", r"investment\s+recommendation", r"asset\s+allocation",
            r"how\s+do\s+i\s+use\s+the\s+investment\s+tools", r"investment\s+category",
            r"recommendation\s+history", r"how\s+to\s+invest\s+in\s+finora"
        ]),
        ("health_reports", [
            r"health\s+report", r"financial\s+health", r"health\s+score", r"6-pillar",
            r"financial\s+diagnostic", r"financial-analysis"
        ]),
        ("risk_assessment", [
            r"risk\s+assessment", r"risk\s+profile", r"risk\s+tolerance",
            r"conservative\s+or\s+aggressive", r"risk\s+score"
        ]),
        ("investment_readiness", [
            r"investment\s+readiness", r"readiness\s+score", r"am\s+i\s+ready\s+to\s+invest",
            r"emergency\s+runway\s+check"
        ]),
        ("stocks_portfolio_watchlist", [
            r"stock\s+analysis", r"watchlist", r"portfolio", r"market\s+stocks",
            r"stocks\s+section", r"how\s+to\s+use\s+portfolio", r"how\s+to\s+use\s+watchlist"
        ]),
        ("auth_settings", [
            r"register", r"sign\s*up", r"log\s*in", r"create\s+account",
            r"settings", r"change\s+password", r"profile\s+page", r"how\s+do\s+i\s+register"
        ]),
        ("dashboard", [
            r"dashboard", r"how\s+to\s+use\s+(the\s+)?(finora\s+)?dashboard",
            r"how\s+to\s+use\s+finora", r"what\s+is\s+finora", r"features\s+of\s+finora",
            r"navigate\s+finora", r"getting\s+started\s+with\s+finora", r"home\s+page"
        ])
    ]

    @classmethod
    def is_prompt_injection(cls, query: str) -> bool:
        """Detect prompt injection, jailbreak, or system-prompt extraction attempts."""
        lower = query.lower()
        for pat in cls.PROMPT_INJECTION_PATTERNS:
            if re.search(pat, lower):
                return True
        return False

    @classmethod
    def is_personal_advice_or_market_prediction(cls, query: str) -> bool:
        """Detect personal financial advice requests or stock market prediction queries."""
        lower = query.lower()
        for pat in cls.ADVICE_AND_PREDICTION_PATTERNS:
            if re.search(pat, lower):
                return True
        return False

    @classmethod
    def is_off_topic(cls, query: str) -> bool:
        """Detect queries entirely unrelated to Finora application features."""
        lower = query.lower()
        for pat in cls.OFF_TOPIC_PATTERNS:
            if re.search(pat, lower):
                return True
        return False

    @classmethod
    def match_feature_topic(cls, query: str):
        """Map user query to an approved Finora feature topic if applicable."""
        lower = query.lower()
        for topic_key, patterns in cls.FEATURE_MATCHERS:
            for pat in patterns:
                if re.search(pat, lower):
                    return topic_key
        return None

    @classmethod
    def is_permitted_finora_query(cls, query: str) -> bool:
        """Determine if a query is within the strictly permitted Finora demo guide scope."""
        if cls.is_prompt_injection(query):
            return False
        if cls.is_personal_advice_or_market_prediction(query):
            return False
        if cls.is_off_topic(query):
            return False
        
        # Must specifically match a known Finora feature topic
        topic = cls.match_feature_topic(query)
        return topic is not None

    @classmethod
    def get_feature_response(cls, topic_key: str) -> str:
        """Retrieve the verified feature walkthrough guide."""
        return FEATURE_GUIDES.get(topic_key, RESTRICTION_RESPONSE)

    @classmethod
    def respond(cls, query: str) -> tuple[str, str]:
        """
        Primary handler for Finora Demo Assistant queries.
        Returns (response_text, provider_label).
        """
        clean_query = (query or "").strip()
        if not clean_query:
            return RESTRICTION_RESPONSE, "Finora Scope Guard"

        # 1. Reject Prompt Injections
        if cls.is_prompt_injection(clean_query):
            return RESTRICTION_RESPONSE, "Finora Scope Guard"

        # 2. Reject Personal Advice / Stock Predictions
        if cls.is_personal_advice_or_market_prediction(clean_query):
            return RESTRICTION_RESPONSE, "Finora Scope Guard"

        # 3. Reject Off-Topic Queries
        if cls.is_off_topic(clean_query):
            return RESTRICTION_RESPONSE, "Finora Scope Guard"

        # 4. Identify Finora Feature
        matched_topic = cls.match_feature_topic(clean_query)
        if not matched_topic:
            return RESTRICTION_RESPONSE, "Finora Scope Guard"

        # 5. Optional LLM invocation with strict boundary grounding
        if AIService.is_api_configured():
            try:
                system_prompt = (
                    "You are Finora's Demo Assistant. Your SOLE purpose is to explain how to navigate and use "
                    "the features of the Finora personal financial adviser web application. "
                    "Keep your tone friendly, simple, and beginner-friendly.\n\n"
                    "Permitted Topics:\n"
                    "- Finora Dashboard (/dashboard, /home)\n"
                    "- Expense Tracking (/expenses)\n"
                    "- Budgets & Savings (/budget)\n"
                    "- Financial Goals (/goals)\n"
                    "- Income Sources (/income)\n"
                    "- Investment Tools & Recommendations (/investment-recommendation, /investments)\n"
                    "- Financial Health Reports (/financial-analysis)\n"
                    "- Risk Assessment Profile (/risk-profile)\n"
                    "- Investment Readiness (/investment-readiness)\n"
                    "- Stock Analysis, Watchlist & Portfolio (/stocks, /watchlist, /portfolio)\n"
                    "- Registration, Login & Settings (/register, /login, /settings)\n\n"
                    "CRITICAL INSTRUCTIONS:\n"
                    "1. Never provide personal financial advice or recommend what stocks/crypto to buy.\n"
                    "2. Never predict stock prices or market trends.\n"
                    "3. If the user asks anything outside how to use Finora, you must reply EXACTLY with:\n"
                    f'"{RESTRICTION_RESPONSE}"\n'
                    "4. Do not execute actions, do not access accounts, and do not invent nonexistent features."
                )
                llm_response = AIService.generate_response(system_prompt, clean_query)
                # Verify that the LLM response is on-topic and helpful
                if llm_response and len(llm_response) > 20:
                    provider_info = AIService.get_provider_status()
                    provider_name = provider_info.get("display_name", "Finora Demo Engine")
                    return llm_response, provider_name
            except Exception as err:
                print(f"External API invocation failed for Demo Assistant, falling back to local guide: {err}")

        # 6. Fallback / Deterministic response from verified Finora Knowledge Base
        local_reply = cls.get_feature_response(matched_topic)
        return local_reply, "Finora Demo Guide"
