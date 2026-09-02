from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.auth_routes import login_required
from ai.financial_analyzer import evaluate_user_financial_health
from ai.risk_analyzer import RISK_QUESTIONS, evaluate_risk_profile, save_user_risk_profile
from ai.investment_readiness import evaluate_investment_readiness
from ai.personalized_suggestions import generate_smart_suggestions
from database import query_db

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/financial-analysis', methods=['GET'])
@login_required
def financial_analysis():
    user_id = session['user_id']
    health_data = evaluate_user_financial_health(user_id)
    readiness_data = evaluate_investment_readiness(user_id)
    
    risk_row = query_db("SELECT risk_level, score FROM risk_profiles WHERE user_id = %s ORDER BY id DESC LIMIT 1", (user_id,), one=True)
    risk_level = risk_row['risk_level'] if risk_row else "Not Assessed"

    suggestions = generate_smart_suggestions(health_data, readiness_data, risk_level)

    return render_template(
        'financial_analysis.html',
        health=health_data,
        readiness=readiness_data,
        risk_level=risk_level,
        suggestions=suggestions
    )

@analysis_bp.route('/risk-profile', methods=['GET', 'POST'])
@login_required
def risk_profile():
    user_id = session['user_id']
    
    if request.method == 'POST':
        answers_dict = {}
        for q in RISK_QUESTIONS:
            qid = q["id"]
            val = request.form.get(qid, 2)
            answers_dict[qid] = int(val)

        evaluated_risk = evaluate_risk_profile(answers_dict)
        save_user_risk_profile(user_id, evaluated_risk)
        flash(f"Risk assessment complete! Your profile is categorized as '{evaluated_risk['risk_level']}'.", 'success')
        return redirect(url_for('analysis.risk_profile'))

    # GET: Fetch latest risk evaluation
    latest_profile = query_db("SELECT * FROM risk_profiles WHERE user_id = %s ORDER BY id DESC LIMIT 1", (user_id,), one=True)
    
    return render_template(
        'risk_profile.html',
        pillars=RISK_PILLARS,
        questions=ALL_QUESTIONS,
        profile=latest_profile
    )

@analysis_bp.route('/investment-readiness', methods=['GET'])
@login_required
def investment_readiness():
    user_id = session['user_id']
    readiness_data = evaluate_investment_readiness(user_id)
    return render_template('investment_readiness.html', readiness=readiness_data)
