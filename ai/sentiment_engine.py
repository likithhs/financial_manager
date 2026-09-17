"""
FinAI Sentiment & Emotional Intelligence Engine
Analyzes user sentiment, emotional tone, and psychological mindset in personal finance conversations.
Provides empathetic validation and emotional framing for financial advisory dialogues.
"""

import re


class SentimentEngine:
    """
    Detects financial sentiment and emotional states from user language:
    - ANXIETY_STRESS: Worried about bills, debt, loss of money, uncertain future.
    - AMBITION_EXCITEMENT: Motivated, seeking rapid wealth, high growth, big goals.
    - CONFUSION_OVERWHELM: Lost, beginner, jargon overload, seeking simplicity.
    - REGRET_GUILT: Overspent, made a bad investment, remorseful, self-critical.
    - CAUTION_FEAR: Scared of market crashes, wanting guaranteed safety, risk averse.
    - OPTIMISM_STRATEGIC: Constructive, forward-looking, goal-oriented, analytical.
    - NEUTRAL_INQUIRY: Objective question or general inquiry.
    """

    PATTERNS = {
        "ANXIETY_STRESS": [
            r"\b(stressed|stressing|stressful|anxious|anxiety|worried|worrying|worries|scared|terrified|panic|panicking)\b",
            r"\b(drowning in debt|can't sleep|paycheck to paycheck|broke|no money|lost everything|struggling|suffering)\b",
            r"\b(overwhelmed|hopeless|depressed|unstable|behind on bills|can't afford|crisis|emergency)\b",
            r"\b(scared of losing|fear of losing|afraid of losing|hard times|financial mess|burden|headache)\b",
            r"\b(too much debt|credit card debt is killing|pressure|stuck|desperate)\b"
        ],
        "AMBITION_EXCITEMENT": [
            r"\b(excited|pumped|thrilled|big dreams|become rich|wealthy|crorepati|millionaire|billionaire)\b",
            r"\b(retire early|fire movement|financial freedom|financial independence|grow fast|multiply)\b",
            r"\b(double my money|10x|moon|huge returns|aggressive growth|hustle|make big money)\b",
            r"\b(ambitious|skyrocket|maximize returns|top stock|best opportunity)\b"
        ],
        "CONFUSION_OVERWHELM": [
            r"\b(confused|confusing|don't understand|clueless|lost|no idea|where do i start|where to begin)\b",
            r"\b(explain like i'm|explain simply|new to this|beginner|novice|what does this mean|too complicated)\b",
            r"\b(overwhelming|jargon|hard to understand|can you help me understand|what should i do)\b"
        ],
        "REGRET_GUILT": [
            r"\b(regret|guilt|guilty|made a mistake|stupid mistake|bad decision|blew my budget|wasted money)\b",
            r"\b(lost money|lost so much|gambled|impulse buy|overspent|shouldn't have bought|ashamed)\b",
            r"\b(screwed up|messed up|bad trade|buying high selling low)\b"
        ],
        "CAUTION_FEAR": [
            r"\b(safe|safety|guaranteed|zero risk|don't want to lose|fear of crash|market crash|recession)\b",
            r"\b(protect my money|capital preservation|is it safe|too risky|scared of stocks|fixed return)\b",
            r"\b(inflation eating|job security|protect my family|loss aversion)\b"
        ],
        "OPTIMISM_STRATEGIC": [
            r"\b(optimistic|confident|on track|planning ahead|goal oriented|disciplined|improve|progress)\b",
            r"\b(ready to invest|saving more|budget on track|milestone|future is bright|building wealth)\b",
            r"\b(strategy|long term|compounding|smart move|optimizing)\b"
        ]
    }

    EMPATHETIC_OPENINGS = {
        "ANXIETY_STRESS": [
            "I completely hear where you're coming from, and it's 100% valid to feel stressed about this. Money worries can feel heavy, but remember that financial situations can always be turned around with a calm, step-by-step plan.",
            "Take a deep breath. You are taking a proactive step just by talking through this. Even when things feel overwhelming, tackling money one clear step at a time gives you back control.",
            "I understand the anxiety you're experiencing. Financial stress is one of the most common burdens people carry, but you don't have to carry it alone. Let's look at your numbers calmly and find a clear path forward."
        ],
        "AMBITION_EXCITEMENT": [
            "I love your energy and ambition! Having big financial goals and the drive to build wealth is the foundation of true financial independence.",
            "That enthusiasm is powerful! Channeling this motivation into smart, disciplined strategies is how life-changing wealth is built over time.",
            "It's exciting to think big about wealth creation! Let's make sure that ambition is paired with a solid risk-managed blueprint so your money works tirelessly for you."
        ],
        "CONFUSION_OVERWHELM": [
            "Don't worry at all—finance is full of unnecessary jargon, and feeling confused at first is completely normal. I'm here to break everything down in plain, crystal-clear language for you.",
            "You're in the right place! No question is too basic. Personal finance isn't taught in most schools, so learning this step-by-step is an empowering journey.",
            "Let's simplify this together. We'll strip away the complex terms and focus on what actually matters for your money and your peace of mind."
        ],
        "REGRET_GUILT": [
            "First, don't be too hard on yourself. Almost every successful investor and saver has made financial mistakes along the way. What matters most is what we do next.",
            "Past financial missteps are tuition for your future financial wisdom. Give yourself some grace—the fact that you recognize it means you're already ready to pivot in a healthier direction.",
            "Regret is a natural feeling, but dwelling on it won't rebuild your surplus. Let's focus our energy on a practical recovery strategy right now."
        ],
        "CAUTION_FEAR": [
            "Your caution is completely sensible. Protecting your hard-earned capital is the very first rule of wealth management—preserving what you have is just as vital as growing it.",
            "It's smart to respect risk. You don't have to jump into high-volatility assets to make financial progress. There are very safe, stable paths to build security first.",
            "Market volatility can be unsettling, especially if you're working hard for every rupee. Prioritizing peace of mind and liquidity is a legitimate, sound priority."
        ],
        "OPTIMISM_STRATEGIC": [
            "That's a great mindset! Approaching your finances with clarity and discipline puts you in the top tier of proactive planners.",
            "It's great to see you focused on long-term strategy. Consistent, thoughtful decisions compound dramatically over time.",
            "You're asking the right strategic questions! Let's evaluate how this fits into your overall financial architecture."
        ],
        "NEUTRAL_INQUIRY": [
            "I'm glad you asked! Let's explore this thoughtfully based on your personal financial situation.",
            "That's a very practical question. Let's break down the mechanics and see how it applies to your wealth journey.",
            "Great topic! Here is how a certified financial strategist looks at this scenario."
        ]
    }

    @staticmethod
    def analyze_sentiment(text):
        """
        Analyzes the text and returns a dictionary with detected sentiment,
        confidence, and an empathetic opening statement.
        """
        if not text:
            return {
                "sentiment": "NEUTRAL_INQUIRY",
                "score": 0,
                "empathetic_opening": SentimentEngine.EMPATHETIC_OPENINGS["NEUTRAL_INQUIRY"][0]
            }

        text_lower = text.lower()
        scores = {}

        for sentiment, patterns in SentimentEngine.PATTERNS.items():
            count = 0
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                count += len(matches)
            if count > 0:
                scores[sentiment] = count

        if not scores:
            primary_sentiment = "NEUTRAL_INQUIRY"
        else:
            primary_sentiment = max(scores, key=scores.get)

        openings = SentimentEngine.EMPATHETIC_OPENINGS.get(
            primary_sentiment, 
            SentimentEngine.EMPATHETIC_OPENINGS["NEUTRAL_INQUIRY"]
        )
        idx = abs(hash(text)) % len(openings)
        empathetic_opening = openings[idx]

        return {
            "sentiment": primary_sentiment,
            "score": scores.get(primary_sentiment, 0),
            "empathetic_opening": empathetic_opening
        }
