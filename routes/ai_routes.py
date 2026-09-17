from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from routes.auth_routes import login_required
from ai.financial_assistant import FinAIAssistant
from services.investment_service import InvestmentService
from database import query_db, execute_db

from services.ai_service import AIService

ai_bp = Blueprint('ai', __name__)

QUICK_PROMPTS = [
    "I'm feeling stressed about my finances, how do I start?",
    "I want to become a crorepati, what is the realistic roadmap?",
    "Can I afford to invest with my current cashflow?",
    "I'm scared of losing money in stock market crashes, what should I do?",
    "How do I stop impulse spending and build wealth?",
    "Can you analyze my 6-pillar financial health score?",
    "Explain the difference between index funds and stocks like I'm five",
    "What if I invest ₹5,000 every month for 5 years?"
]

@ai_bp.route('/ai-assistant', methods=['GET', 'POST'])
@login_required
def ai_assistant():
    user_id = session['user_id']

    if request.method == 'POST':
        user_message = request.form.get('message', '').strip()
        if user_message:
            FinAIAssistant.respond(user_id, user_message)
        return redirect(url_for('ai.ai_assistant'))

    # GET: Load all past conversations
    conversations = query_db("""
        SELECT * FROM ai_conversations 
        WHERE user_id = %s 
        ORDER BY created_at ASC
    """, (user_id,))

    provider_status = AIService.get_provider_status()

    return render_template(
        'ai_assistant.html',
        conversations=conversations or [],
        quick_prompts=QUICK_PROMPTS,
        provider_status=provider_status
    )

@ai_bp.route('/ai-assistant/chat', methods=['POST'])
def ai_chat_api():
    """Asynchronous JSON endpoint for interactive chat. Requires active user login."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({
            "status": "auth_required",
            "reply": "FinAI is an exclusive personal wealth advisory system. To analyze your finances, evaluate your sentiment, and provide personalized guidance, you must be logged in.",
            "login_url": url_for('auth.login'),
            "register_url": url_for('auth.register')
        }), 401

    data = request.get_json(silent=True) or request.form
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({"error": "Empty message", "status": "error"}), 400

    reply, provider = FinAIAssistant.respond(user_id, user_message, return_meta=True)
    return jsonify({
        "status": "success",
        "reply": reply,
        "provider": provider
    })

@ai_bp.route('/ai-assistant/clear', methods=['POST'])
@login_required
def clear_chat():
    user_id = session['user_id']
    execute_db("DELETE FROM ai_conversations WHERE user_id = %s", (user_id,))
    flash('Conversation history cleared.', 'info')
    return redirect(url_for('ai.ai_assistant'))

@ai_bp.route('/recommendation-history', methods=['GET'])
@login_required
def recommendation_history():
    user_id = session['user_id']
    history = InvestmentService.get_recommendation_history(user_id)
    return render_template('recommendation_history.html', history=history)
