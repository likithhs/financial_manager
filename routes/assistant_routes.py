"""
FinAI Backend Foundation - Assistant Routes Blueprint
Handles FinAI conversational guidance routes (/assistant and /ai-assistant).
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from services.auth_helper import login_required, get_current_user_id
from ai.financial_assistant import FinAIAssistant
from database import query_db, execute_db

assistant_bp = Blueprint('assistant', __name__)

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


@assistant_bp.route('/assistant', methods=['GET', 'POST'])
@assistant_bp.route('/ai-assistant', methods=['GET', 'POST'])
@login_required
def assistant():
    user_id = get_current_user_id()

    if request.method == 'POST':
        user_message = request.form.get('message', '').strip()
        if user_message:
            FinAIAssistant.respond(user_id, user_message)
        return redirect(url_for('assistant.assistant'))

    # Load conversations
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


@assistant_bp.route('/assistant/clear', methods=['POST'])
@assistant_bp.route('/ai-assistant/clear', methods=['POST'])
@login_required
def clear_chat():
    user_id = get_current_user_id()
    execute_db("DELETE FROM ai_conversations WHERE user_id = %s", (user_id,))
    flash('Conversation history cleared.', 'info')
    return redirect(url_for('assistant.assistant'))
