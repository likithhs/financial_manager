"""
Seed script to populate sample test users, transactions, goals, and risk profiles
for Viva demonstration and academic evaluation.
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import get_db_connection, execute_db, query_db, init_db
from werkzeug.security import generate_password_hash
from ai.financial_analyzer import evaluate_user_financial_health
from ai.risk_analyzer import evaluate_risk_profile, save_user_risk_profile
from ai.investment_readiness import evaluate_investment_readiness
from services.financial_service import FinancialService
from services.portfolio_service import PortfolioService

def seed_academic_scenarios():
    print("Initializing database tables...")
    init_db()

    pwd_hash = generate_password_hash('user123')

    # -------------------------------------------------------------
    # USER 1: Good Financial Health + Moderate Risk
    # -------------------------------------------------------------
    u1 = query_db("SELECT id FROM users WHERE email = 'user1@test.com'", one=True)
    if not u1:
        u1_id = execute_db("""
            INSERT INTO users (name, email, password_hash, age, occupation, financial_exp, investment_exp, role)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'user')
        """, ('Rahul Sharma (User 1 - Balanced)', 'user1@test.com', pwd_hash, 26, 'Software Developer', 'Intermediate', 'Mutual Funds / SIP'))
    else:
        u1_id = u1['id']

    # Financial data for User 1
    FinancialService.add_income(u1_id, 'Software Engineer Salary', 65000.00, 'Salary / Wages', '2026-08-01', 'Monthly direct credit')
    FinancialService.add_income(u1_id, 'Freelance Web Consulting', 10000.00, 'Freelance / Consulting', '2026-08-10', 'Part-time project')
    FinancialService.add_expense(u1_id, 'Apartment Rent', 18000.00, 'Rent & Housing', '2026-08-02', 'Monthly rent')
    FinancialService.add_expense(u1_id, 'Groceries & Provisions', 7500.00, 'Food & Dining', '2026-08-05', 'Supermarket')
    FinancialService.add_expense(u1_id, 'Electricity & Broadband', 3200.00, 'Bills & Utilities', '2026-08-08', 'Monthly utility bills')
    FinancialService.add_expense(u1_id, 'Fuel & Metro Pass', 2800.00, 'Transport & Fuel', '2026-08-12', 'Commute')
    FinancialService.set_budget(u1_id, '2026-08', 35000.00)
    FinancialService.add_goal(u1_id, 'Emergency Fund (6 Months)', 180000.00, 75000.00, '2027-04-01', 'High', 'Liquid safety deposit')
    FinancialService.add_goal(u1_id, 'New MacBook Pro', 140000.00, 45000.00, '2026-12-31', 'Medium', 'Tech upgrade')
    
    # Moderate risk profile
    save_user_risk_profile(u1_id, evaluate_risk_profile({'q1': 3, 'q2': 3, 'q3': 3, 'q4': 3, 'q5': 3, 'q6': 3, 'q7': 3}))
    evaluate_user_financial_health(u1_id)
    evaluate_investment_readiness(u1_id)
    PortfolioService.add_holding(u1_id, 'TCS', 'Tata Consultancy Services', 'Equity Stock', 10, 3600.00, '2026-05-10', 'Core holding')
    PortfolioService.add_holding(u1_id, 'HDFCBANK', 'HDFC Bank Ltd', 'Equity Stock', 20, 1580.00, '2026-06-15', 'Banking leader')

    # -------------------------------------------------------------
    # USER 2: Poor Financial Health (NOT READY)
    # -------------------------------------------------------------
    u2 = query_db("SELECT id FROM users WHERE email = 'user2@test.com'", one=True)
    if not u2:
        u2_id = execute_db("""
            INSERT INTO users (name, email, password_hash, age, occupation, financial_exp, investment_exp, role)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'user')
        """, ('Amit Verma (User 2 - Unready)', 'user2@test.com', pwd_hash, 22, 'Junior Trainee', 'Beginner', 'None'))
    else:
        u2_id = u2['id']

    FinancialService.add_income(u2_id, 'Internship Stipend', 22000.00, 'Salary / Wages', '2026-08-01')
    FinancialService.add_expense(u2_id, 'Room Rent', 11000.00, 'Rent & Housing', '2026-08-03')
    FinancialService.add_expense(u2_id, 'Food & Eating Out', 7000.00, 'Food & Dining', '2026-08-06')
    FinancialService.add_expense(u2_id, 'Mobile EMI & Shopping', 5500.00, 'Shopping & Discretionary', '2026-08-10')
    FinancialService.set_budget(u2_id, '2026-08', 20000.00)
    save_user_risk_profile(u2_id, evaluate_risk_profile({'q1': 1, 'q2': 1, 'q3': 1, 'q4': 1, 'q5': 1, 'q6': 1, 'q7': 1}))
    evaluate_user_financial_health(u2_id)
    evaluate_investment_readiness(u2_id)

    # -------------------------------------------------------------
    # USER 3: Conservative Investor + High Health
    # -------------------------------------------------------------
    u3 = query_db("SELECT id FROM users WHERE email = 'user3@test.com'", one=True)
    if not u3:
        u3_id = execute_db("""
            INSERT INTO users (name, email, password_hash, age, occupation, financial_exp, investment_exp, role)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'user')
        """, ('Priya Nair (User 3 - Conservative)', 'user3@test.com', pwd_hash, 34, 'Government Officer', 'Advanced', 'Fixed Deposits / Gold'))
    else:
        u3_id = u3['id']

    FinancialService.add_income(u3_id, 'Government Service Salary', 85000.00, 'Salary / Wages', '2026-08-01')
    FinancialService.add_expense(u3_id, 'Household Living Expenses', 25000.00, 'Bills & Utilities', '2026-08-04')
    FinancialService.add_expense(u3_id, 'Child School Fees', 10000.00, 'Education & Courses', '2026-08-07')
    FinancialService.set_budget(u3_id, '2026-08', 40000.00)
    FinancialService.add_goal(u3_id, 'Emergency Fund', 300000.00, 250000.00, '2027-01-01', 'High')
    save_user_risk_profile(u3_id, evaluate_risk_profile({'q1': 2, 'q2': 1, 'q3': 2, 'q4': 1, 'q5': 3, 'q6': 1, 'q7': 2}))
    evaluate_user_financial_health(u3_id)
    evaluate_investment_readiness(u3_id)

    # -------------------------------------------------------------
    # USER 4: Aggressive Growth Investor
    # -------------------------------------------------------------
    u4 = query_db("SELECT id FROM users WHERE email = 'user4@test.com'", one=True)
    if not u4:
        u4_id = execute_db("""
            INSERT INTO users (name, email, password_hash, age, occupation, financial_exp, investment_exp, role)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'user')
        """, ('Vikram Rao (User 4 - Aggressive)', 'user4@test.com', pwd_hash, 29, 'Tech Lead', 'Advanced', 'Direct Stocks / Equity'))
    else:
        u4_id = u4['id']

    FinancialService.add_income(u4_id, 'Senior Engineer Salary', 120000.00, 'Salary / Wages', '2026-08-01')
    FinancialService.add_expense(u4_id, 'Condo Rent & Utilities', 35000.00, 'Rent & Housing', '2026-08-03')
    FinancialService.add_expense(u4_id, 'Lifestyle & Travel', 12000.00, 'Shopping & Discretionary', '2026-08-09')
    FinancialService.set_budget(u4_id, '2026-08', 55000.00)
    FinancialService.add_goal(u4_id, 'Emergency Fund', 300000.00, 280000.00, '2027-01-01', 'High')
    save_user_risk_profile(u4_id, evaluate_risk_profile({'q1': 4, 'q2': 4, 'q3': 4, 'q4': 4, 'q5': 4, 'q6': 4, 'q7': 4}))
    evaluate_user_financial_health(u4_id)
    evaluate_investment_readiness(u4_id)

    print("\n✅ Successfully seeded 4 Academic Demonstration Users & Admin Account:")
    print("----------------------------------------------------------------------")
    print("1. Balanced User (Rahul):      user1@test.com   | Pass: user123 (Good Health, Moderate Risk)")
    print("2. Unready User (Amit):        user2@test.com   | Pass: user123 (Poor Health, NOT READY)")
    print("3. Conservative User (Priya):  user3@test.com   | Pass: user123 (Excellent Health, Conservative Risk)")
    print("4. Aggressive User (Vikram):   user4@test.com   | Pass: user123 (Excellent Health, Aggressive Risk)")
    print("5. System Admin:               admin@financialmanager.com | Pass: admin123")
    print("----------------------------------------------------------------------")

if __name__ == '__main__':
    seed_academic_scenarios()
