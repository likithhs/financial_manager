from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from routes.auth_routes import login_required
from ai.demo_assistant import FinoraDemoAssistant, RESTRICTION_RESPONSE
from services.investment_service import InvestmentService
from database import query_db, execute_db

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/ai-assistant', methods=['GET', 'POST'])
def ai_assistant():
    """
    Direct navigation to /ai-assistant:
    - If authenticated: chatbot is hidden; redirect to /home.
    - If unauthenticated: redirect to the public dashboard demo widget.
    """
    if 'user_id' in session:
        flash('The Finora Demo Assistant is only available for unauthenticated visitors on the public landing page.', 'info')
        return redirect(url_for('main.home'))
    return redirect(url_for('main.index') + '#ai')


@ai_bp.route('/ai-assistant/chat', methods=['POST'])
def ai_chat_api():
    """
    Public Dashboard Demo Assistant Endpoint.
    Strictly accepts requests ONLY from unauthenticated visitors on the public dashboard.
    Rejects authenticated requests with HTTP 403 Forbidden.
    """
    # 1. Enforce that authenticated users cannot access the chatbot backend endpoint
    if session.get('user_id'):
        return jsonify({
            "status": "forbidden",
            "error": "Access Denied: The Finora Demo Assistant is strictly available on the public dashboard for unauthenticated visitors. Authenticated sessions are not permitted to access this endpoint."
        }), 403

    # 2. Extract and sanitize input
    data = request.get_json(silent=True) or request.form
    user_message = data.get('message', '').strip() if data else ''

    if not user_message:
        return jsonify({
            "status": "error",
            "error": "Empty message"
        }), 400

    # 3. Generate response via Finora Demo Assistant
    reply, provider = FinoraDemoAssistant.respond(user_message)

    return jsonify({
        "status": "success",
        "reply": reply,
        "provider": provider
    }), 200


@ai_bp.route('/ai-assistant/clear', methods=['POST'])
@login_required
def clear_chat():
    user_id = session['user_id']
    execute_db("DELETE FROM ai_conversations WHERE user_id = %s", (user_id,))
    flash('Conversation history cleared.', 'info')
    return redirect(url_for('main.home'))


@ai_bp.route('/recommendation-history', methods=['GET'])
@login_required
def recommendation_history():
    user_id = session['user_id']
    history = InvestmentService.get_recommendation_history(user_id)
    return render_template('recommendation_history.html', history=history)
