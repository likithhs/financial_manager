from flask import Blueprint, render_template, session
from routes.auth_routes import login_required
from ai.investment_recommender import generate_investment_recommendations
from ai.investment_readiness import evaluate_investment_readiness
from database import query_db

investment_bp = Blueprint('investment', __name__)

@investment_bp.route('/investments', methods=['GET'])
@login_required
def investments():
    user_id = session['user_id']
    readiness = evaluate_investment_readiness(user_id)
    risk_row = query_db("SELECT risk_level FROM risk_profiles WHERE user_id = %s ORDER BY id DESC LIMIT 1", (user_id,), one=True)
    user_risk = risk_row['risk_level'] if risk_row else "Moderate"
    return render_template('investments.html', readiness=readiness, user_risk=user_risk)

@investment_bp.route('/investment-recommendation', methods=['GET'])
@login_required
def investment_recommendation():
    user_id = session['user_id']
    recommendation = generate_investment_recommendations(user_id)
    return render_template('investment_recommendation.html', rec=recommendation)
