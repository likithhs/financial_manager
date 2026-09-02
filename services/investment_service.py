from database import query_db
from ai.investment_recommender import generate_investment_recommendations
from ai.investment_readiness import evaluate_investment_readiness

class InvestmentService:
    @staticmethod
    def get_latest_recommendation(user_id):
        return generate_investment_recommendations(user_id)

    @staticmethod
    def get_recommendation_history(user_id):
        inv_history = query_db("""
            SELECT * FROM investment_recommendations 
            WHERE user_id = %s 
            ORDER BY evaluated_at DESC LIMIT 20
        """, (user_id,))
        
        stock_history = query_db("""
            SELECT * FROM stock_analysis 
            WHERE user_id = %s 
            ORDER BY evaluated_at DESC LIMIT 20
        """, (user_id,))

        return {
            "investment_history": inv_history or [],
            "stock_history": stock_history or []
        }
