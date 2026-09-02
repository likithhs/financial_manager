from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from routes.auth_routes import login_required
from ai.financial_assistant import FinAIAssistant
from services.investment_service import InvestmentService
from database import query_db, execute_db

ai_bp = Blueprint('ai', __name__)

QUICK_PROMPTS = [
    "Where should I invest?",
    "Should I invest in stocks?",
    "What is my risk profile?",
    "Why did you recommend this investment?",
    "Why is my investment readiness low?",
    "How can I improve my savings?",
    "What is the difference between mutual funds and stocks?",
    "Tell me about TCS",
    "What is a Systematic Investment Plan (SIP)?"
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

    return render_template(
        'ai_assistant.html',
        conversations=conversations or [],
        quick_prompts=QUICK_PROMPTS
    )

@ai_bp.route('/ai-assistant/chat', methods=['POST'])
@login_required
def ai_chat_api():
    """Optional JSON endpoint for asynchronous calls if supported."""
    user_id = session['user_id']
    data = request.get_json(silent=True) or request.form
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    reply = FinAIAssistant.respond(user_id, user_message)
    return jsonify({"reply": reply})

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
