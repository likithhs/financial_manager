class IntentClassifier:
    """
    Identifies what the user is asking the Financial Adviser.

    This is intentionally rule-based and beginner-friendly.
    It can later be replaced or enhanced with an ML/LLM classifier.
    """

    INTENTS = {
        "financial_health": [
            "financial health",
            "how am i doing financially",
            "am i financially healthy",
            "financial condition",
            "my financial situation",
            "how are my finances",
            "analyze my finances",
            "financial score"
        ],

        "investment": [
            "where should i invest",
            "where can i invest",
            "what should i invest",
            "investment advice",
            "investment option",
            "how should i invest",
            "best investment",
            "invest my money",
            "invest my savings"
        ],

        "investment_affordability": [
            "can i invest",
            "can i afford to invest",
            "how much can i invest",
            "how much should i invest",
            "can i invest this month",
            "money available for investment",
            "spare money"
        ],

        "risk_profile": [
            "risk profile",
            "risk level",
            "how much risk",
            "am i taking too much risk",
            "my investment risk",
            "risk tolerance"
        ],


       "goals": [
    "my goal",
    "my goals",
    "financial goal",
    "goal progress",
    "goal status",
    "reach my goal",
    "reach my",
    "achieve my goal",
    "achieve my",
    "how much should i save",
    "goal planning",
    "goal target",
    "goal deadline",
    "goal amount",
    "how long to reach"
],

        "portfolio": [
            "my portfolio",
            "portfolio analysis",
            "analyze portfolio",
            "portfolio risk",
            "portfolio diversification",
            "diversified",
            "my investments",
            "existing investments"
        ],

        "stocks": [
            "stock",
            "stocks",
            "share",
            "shares",
            "stock recommendation",
            "stock suggestion",
            "should i buy",
            "stock risk"
        ],

        "savings": [
            "how can i save",
            "improve my savings",
            "saving money",
            "savings",
            "save more",
            "reduce my expenses",
            "expense control"
        ],

        "budget": [
            "my budget",
            "budget status",
            "budget analysis",
            "how much have i spent",
            "how much did i spend",
            "budget remaining",
            "over budget"
        ],

        "what_if": [
            "what if",
            "suppose i invest",
            "if i invest",
            "if i save",
            "what happens if",
            "increase my investment",
            "increase my savings"
        ],

        "general": []
    }

    @staticmethod
    def classify(message):
        """
        Return the most likely intent for the user's message.
        """

        msg = message.lower().strip()

        # What-if questions get priority because they can contain
        # words such as investment, savings, or goals.
        if any(phrase in msg for phrase in IntentClassifier.INTENTS["what_if"]):
            return "what_if"

        # More specific intents should be checked before broader ones.
        priority_order = [
            "investment_affordability",
            "portfolio",
            "risk_profile",
            "financial_health",
            "goals",
            "budget",
            "savings",
            "stocks",
            "investment"
        ]

        for intent in priority_order:
            keywords = IntentClassifier.INTENTS[intent]

            if any(keyword in msg for keyword in keywords):
                return intent

        return "general"