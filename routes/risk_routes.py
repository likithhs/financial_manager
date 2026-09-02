"""
FinAI Backend Foundation - Risk Assessment Routes Blueprint
Handles user risk tolerance evaluations across structured assessment pillars (/risk-assessment and /risk-profile).
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.auth_helper import login_required, get_current_user_id
from database import query_db
from ai.risk_analyzer import RISK_PILLARS, ALL_QUESTIONS, evaluate_risk_profile, save_user_risk_profile

risk_bp = Blueprint('risk', __name__)


@risk_bp.route('/risk-assessment', methods=['GET', 'POST'])
@risk_bp.route('/risk-profile', methods=['GET', 'POST'])
@login_required
def risk_assessment():
    user_id = get_current_user_id()

    if request.method == 'POST':
        answers_dict = {}
        for q in ALL_QUESTIONS:
            qid = q["id"]
            val = request.form.get(qid, 2)
            try:
                answers_dict[qid] = int(val)
            except ValueError:
                answers_dict[qid] = 2

        evaluated_risk = evaluate_risk_profile(answers_dict)
        save_user_risk_profile(user_id, evaluated_risk)
        flash(f"Risk evaluation complete! Your psychometric classification: {evaluated_risk['risk_level']} Investor ({evaluated_risk['score']} / {evaluated_risk['max_score']} pts).", "success")
        return redirect(url_for('risk.risk_assessment'))

    latest_profile = query_db(
        "SELECT * FROM risk_profiles WHERE user_id = %s ORDER BY id DESC LIMIT 1",
        (user_id,),
        one=True
    )

    return render_template(
        'risk_profile.html',
        pillars=RISK_PILLARS,
        questions=ALL_QUESTIONS,
        profile=latest_profile
    )
