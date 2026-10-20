"""
Finora Financial Calculations & Goal Analysis Verification Test Suite
Tests all 8 required criteria from Steps 1-4:
1. Active and In Progress goals.
2. Completed goals.
3. Monthly totals excluding older transactions.
4. Transactions spanning different months and years.
5. Zero income and zero expenses.
6. Emergency fund not configured.
7. Empty historical data for runway.
8. Financial-health score behavior.
"""

import unittest
from datetime import date
from decimal import Decimal

from ai.date_utils import get_calendar_month_range, get_app_current_date
from ai.financial_health import calculate_financial_health
from ai.financial_calculator import FinancialCalculator
from ai.financial_analyzer import evaluate_user_financial_health, get_user_monthly_expense_basis
from services.goal_service import GoalService, is_goal_active, count_active_goals
from services.financial_service import FinancialService
from database import execute_db, query_db, get_db_connection


class TestFinancialCalculations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a temporary test user in the database for integration tests
        cls.test_email = "calc_test_user@finora.test"
        existing = query_db("SELECT id FROM users WHERE email = %s", (cls.test_email,), one=True)
        if existing:
            cls.test_user_id = existing['id']
            cls._clean_user_data(cls.test_user_id)
        else:
            cls.test_user_id = execute_db("""
                INSERT INTO users (name, email, password, password_hash, age, occupation, financial_exp, investment_exp, role)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'user')
            """, ('Calculation Tester', cls.test_email, 'pbkdf2:dummy', 'pbkdf2:dummy', 30, 'Tester', 'Intermediate', 'Moderate'))

    @classmethod
    def tearDownClass(cls):
        # Clean up the temporary test user and cascading data
        if hasattr(cls, 'test_user_id') and cls.test_user_id:
            cls._clean_user_data(cls.test_user_id)
            execute_db("DELETE FROM users WHERE id = %s", (cls.test_user_id,))

    @classmethod
    def _clean_user_data(cls, user_id):
        execute_db("DELETE FROM incomes WHERE user_id = %s", (user_id,))
        execute_db("DELETE FROM income WHERE user_id = %s", (user_id,))
        execute_db("DELETE FROM expenses WHERE user_id = %s", (user_id,))
        execute_db("DELETE FROM financial_goals WHERE user_id = %s", (user_id,))
        execute_db("DELETE FROM budgets WHERE user_id = %s", (user_id,))
        execute_db("DELETE FROM financial_analysis WHERE user_id = %s", (user_id,))
        execute_db("DELETE FROM investment_readiness WHERE user_id = %s", (user_id,))

    def setUp(self):
        self._clean_user_data(self.test_user_id)

    # =========================================================================
    # STEP 1: GOAL STATUS TESTS
    # =========================================================================

    def test_01_active_and_in_progress_goals(self):
        """
        Verify that goals with status 'Active' and 'In Progress' are consistently
        recognized as active qualifying goals when target amount has not been reached.
        Verify that the goal-planning bonus (+5 pts) in health score triggers.
        """
        # Test unit function is_goal_active
        self.assertTrue(is_goal_active('Active', current_amount=5000, target_amount=20000))
        self.assertTrue(is_goal_active('active', current_amount=5000, target_amount=20000))
        self.assertTrue(is_goal_active('In Progress', current_amount=1000, target_amount=10000))
        self.assertTrue(is_goal_active('in progress', current_amount=1000, target_amount=10000))
        self.assertTrue(is_goal_active('in_progress', current_amount=0, target_amount=10000))

        # Goal count helper
        sample_goals = [
            {'status': 'In Progress', 'current_amount': 2000.0, 'target_amount': 10000.0},
            {'status': 'Active', 'current_amount': 5000.0, 'target_amount': 25000.0},
        ]
        self.assertEqual(count_active_goals(sample_goals), 2)

        # Database integration
        g1_id = FinancialService.add_goal(self.test_user_id, 'Emergency Reserve', 50000, 10000, status='In Progress')
        g2_id = FinancialService.add_goal(self.test_user_id, 'Tech Upgrade', 30000, 5000, status='Active')

        user_goals = FinancialService.get_user_goals(self.test_user_id)
        self.assertEqual(len(user_goals), 2)
        active_goals = [g for g in user_goals if g['is_active']]
        self.assertEqual(len(active_goals), 2)

        # Health score goal planning bonus verification
        health_with_goals = calculate_financial_health(
            total_income=50000,
            total_expenses=25000,
            active_goals_count=2,
            emergency_fund=10000,
            emergency_fund_configured=True
        )
        health_without_goals = calculate_financial_health(
            total_income=50000,
            total_expenses=25000,
            active_goals_count=0,
            emergency_fund=10000,
            emergency_fund_configured=True
        )
        # Active goal bonus adds 5 points to discipline score
        self.assertEqual(health_with_goals['score'] - health_without_goals['score'], 5)
        self.assertTrue(any("Active financial planning in place" in f for f in health_with_goals['factors']))

    def test_02_completed_goals_excluded_from_active_count(self):
        """
        Verify that goals with status 'Completed' (or reached target) are excluded
        from active-goal counts, even if current amount or status was manipulated.
        """
        # Explicit status 'Completed'
        self.assertFalse(is_goal_active('Completed', current_amount=5000, target_amount=20000))
        self.assertFalse(is_goal_active('completed', current_amount=0, target_amount=10000))

        # Goal that reached target amount is considered completed even if status says 'In Progress'
        self.assertFalse(is_goal_active('In Progress', current_amount=20000, target_amount=20000))
        self.assertFalse(is_goal_active('Active', current_amount=25000, target_amount=20000))

        # Database integration
        FinancialService.add_goal(self.test_user_id, 'Fully Saved Car', 100000, 100000, status='Completed')
        user_goals = FinancialService.get_user_goals(self.test_user_id)
        self.assertEqual(len(user_goals), 1)
        self.assertTrue(user_goals[0]['is_completed'])
        self.assertFalse(user_goals[0]['is_active'])

        # Financial health evaluation must report active_goals_count = 0
        health = evaluate_user_financial_health(self.test_user_id)
        # Goal planning bonus should NOT trigger when user has only completed goals
        self.assertFalse(any("Active financial planning in place" in f for f in health['factors']))

    def test_03_cancelled_paused_archived_statuses_preserved(self):
        """
        Verify that legitimate inactive statuses ('Cancelled', 'Paused', 'Archived')
        are preserved and excluded from active-goal counts.
        """
        self.assertFalse(is_goal_active('Cancelled', current_amount=1000, target_amount=10000))
        self.assertFalse(is_goal_active('Canceled', current_amount=1000, target_amount=10000))
        self.assertFalse(is_goal_active('Paused', current_amount=1000, target_amount=10000))
        self.assertFalse(is_goal_active('Archived', current_amount=1000, target_amount=10000))

        # Create goal and update status to Paused
        gid = FinancialService.add_goal(self.test_user_id, 'Vacation Goal', 40000, 5000, status='In Progress')
        success = FinancialService.update_goal_status(gid, self.test_user_id, 'Paused')
        self.assertTrue(success)

        user_goals = FinancialService.get_user_goals(self.test_user_id)
        self.assertEqual(user_goals[0]['status'], 'Paused')
        self.assertFalse(user_goals[0]['is_active'])

        # Adding partial funds preserves Paused status when target is not yet reached
        FinancialService.add_funds_to_goal(gid, self.test_user_id, 2000)
        updated_goals = FinancialService.get_user_goals(self.test_user_id)
        self.assertEqual(updated_goals[0]['status'], 'Paused')
        self.assertEqual(updated_goals[0]['current_amount'], 7000.0)

    # =========================================================================
    # STEP 2: MONTHLY INCOME AND EXPENSES TESTS
    # =========================================================================

    def test_04_monthly_totals_excluding_older_transactions(self):
        """
        Verify that monthly cashflow calculations strictly isolate the current calendar
        month and exclude transactions from past months, without mixing lifetime totals.
        """
        today = get_app_current_date()
        current_month_str = today.strftime('%Y-%m')
        
        # Determine previous month safely
        if today.month == 1:
            prev_year, prev_month = today.year - 1, 12
        else:
            prev_year, prev_month = today.year, today.month - 1
        prev_month_str = f"{prev_year:04d}-{prev_month:02d}"

        # Older transactions (previous month)
        FinancialService.add_income(self.test_user_id, 'Old Salary', 60000.00, 'Salary', f"{prev_month_str}-05")
        FinancialService.add_expense(self.test_user_id, 'Old Rent', 20000.00, 'Rent', f"{prev_month_str}-08")

        # Current month transactions
        FinancialService.add_income(self.test_user_id, 'Current Salary', 80000.00, 'Salary', f"{current_month_str}-02")
        FinancialService.add_expense(self.test_user_id, 'Current Rent', 25000.00, 'Rent', f"{current_month_str}-05")

        # Evaluate financial health for current month
        health = evaluate_user_financial_health(self.test_user_id)

        # Monthly metrics MUST reflect ONLY current month
        self.assertEqual(health['total_income'], 80000.00)
        self.assertEqual(health['total_expenses'], 25000.00)
        self.assertEqual(health['savings'], 55000.00)
        self.assertEqual(health['savings_rate'], 68.75)  # (55000 / 80000) * 100
        self.assertEqual(health['expense_ratio'], 31.25)  # (25000 / 80000) * 100

        # Lifetime summary MUST reflect both months
        lifetime = FinancialService.get_lifetime_cashflow_summary(self.test_user_id)
        self.assertEqual(lifetime['total_income'], 140000.00)
        self.assertEqual(lifetime['total_expenses'], 45000.00)
        self.assertEqual(lifetime['savings'], 95000.00)

        # Ensure monthly is NOT equal to lifetime
        self.assertNotEqual(health['total_income'], lifetime['total_income'])

    def test_05_transactions_spanning_different_months_and_years(self):
        """
        Verify calendar month date range boundaries, leap year handling,
        and year transitions (e.g. Dec 31 to Jan 01).
        """
        # Test leap year range
        start, end = get_calendar_month_range('2024-02')
        self.assertEqual(start, date(2024, 2, 1))
        self.assertEqual(end, date(2024, 2, 29))

        # Test non-leap year range
        start, end = get_calendar_month_range('2025-02')
        self.assertEqual(start, date(2025, 2, 1))
        self.assertEqual(end, date(2025, 2, 28))

        # Test year boundary (December to January)
        start_dec, end_dec = get_calendar_month_range('2025-12-15')
        self.assertEqual(start_dec, date(2025, 12, 1))
        self.assertEqual(end_dec, date(2025, 12, 31))

        start_jan, end_jan = get_calendar_month_range('2026-01-05')
        self.assertEqual(start_jan, date(2026, 1, 1))
        self.assertEqual(end_jan, date(2026, 1, 31))

        # Insert transactions right at boundaries in database
        FinancialService.add_income(self.test_user_id, 'Dec Bonus', 50000, 'Bonus', '2025-12-31')
        FinancialService.add_income(self.test_user_id, 'Jan Salary', 70000, 'Salary', '2026-01-01')

        summary_dec = FinancialService.get_monthly_cashflow_summary(self.test_user_id, '2025-12')
        self.assertEqual(summary_dec['income'], 50000.0)

        summary_jan = FinancialService.get_monthly_cashflow_summary(self.test_user_id, '2026-01')
        self.assertEqual(summary_jan['income'], 70000.0)

    def test_06_zero_income_and_zero_expenses(self):
        """
        Verify safe division, zero-division immunity, and realistic factor explanations
        when income and/or expenses are zero.
        """
        # Zero income and zero expenses
        health_empty = calculate_financial_health(
            total_income=0.0,
            total_expenses=0.0,
            emergency_fund=0.0,
            total_budget=0.0
        )
        self.assertEqual(health_empty['total_income'], 0.0)
        self.assertEqual(health_empty['total_expenses'], 0.0)
        self.assertEqual(health_empty['savings'], 0.0)
        self.assertEqual(health_empty['savings_rate'], 0.0)
        self.assertEqual(health_empty['expense_ratio'], 0.0)
        self.assertEqual(health_empty['emergency_fund_ratio'], 0.0)
        self.assertTrue(any("No active recorded income" in f for f in health_empty['factors']))
        self.assertTrue(any("No recorded living expenses or income" in f for f in health_empty['factors']))

        # Zero income with positive expenses (expenses = 15,000)
        health_zero_income = calculate_financial_health(
            total_income=0.0,
            total_expenses=15000.0,
            emergency_fund=0.0
        )
        self.assertEqual(health_zero_income['savings'], -15000.0)
        self.assertEqual(health_zero_income['savings_rate'], 0.0)
        self.assertEqual(health_zero_income['expense_ratio'], 100.0)
        self.assertTrue(any("without active income" in f for f in health_zero_income['factors']))

    # =========================================================================
    # STEP 3 & 4: RUNWAY & EMERGENCY FUND TESTS
    # =========================================================================

    def test_07_emergency_fund_not_configured(self):
        """
        Verify that when an emergency fund has not been configured:
        - The system returns an explicit unconfigured state.
        - General positive savings are NOT treated as an emergency fund (no silent fallback).
        - Emergency runway ratio is 0.0, score gives 0 for safety net, and reports unconfigured.
        """
        # Positive cashflow of ₹40,000, but emergency fund NOT configured
        health = calculate_financial_health(
            total_income=60000.0,
            total_expenses=20000.0,
            emergency_fund=0.0,
            emergency_fund_configured=False
        )
        # General savings is 40,000
        self.assertEqual(health['savings'], 40000.0)
        # But emergency fund must NOT fallback to 40,000!
        self.assertEqual(health['emergency_fund'], 0.0)
        self.assertFalse(health['emergency_fund_configured'])
        self.assertEqual(health['emergency_fund_ratio'], 0.0)
        self.assertEqual(health['emergency_fund_status'], "Not Configured")
        self.assertTrue(any("Emergency fund has not been configured" in f for f in health['factors']))

        # Database integration test: user has goals, but NONE are emergency/safety
        FinancialService.add_goal(self.test_user_id, 'Buying Sports Bike', 120000, 30000)
        db_health = evaluate_user_financial_health(self.test_user_id)
        self.assertFalse(db_health['emergency_fund_configured'])
        self.assertEqual(db_health['emergency_fund_ratio'], 0.0)

    def test_08_empty_historical_data_for_runway(self):
        """
        Verify runway estimation behavior when expense history is empty or limited:
        - Avoid division by zero when expense basis is 0.
        - Label as insufficient data instead of claiming false precision (e.g. arbitrary 6.0 months).
        - Label limited history appropriately when only 1 month exists.
        """
        # User has dedicated emergency fund of 50,000, but 0 recorded expenses
        health = calculate_financial_health(
            total_income=30000.0,
            total_expenses=0.0,
            emergency_fund=50000.0,
            emergency_fund_configured=True,
            monthly_expense_basis=0.0
        )
        self.assertEqual(health['emergency_fund_ratio'], 0.0)
        self.assertEqual(health['emergency_fund_status'], "Insufficient Expense Data")
        self.assertEqual(health['runway_label'], "Insufficient historical expense data to compute runway")
        self.assertTrue(any("expense history is empty" in f for f in health['factors']))

        # Single month of expense data in database -> marked as limited history
        FinancialService.add_expense(self.test_user_id, 'Groceries', 10000.0, 'Food', '2026-10-10')
        basis, has_sufficient_history = get_user_monthly_expense_basis(self.test_user_id, '2026-10-31')
        self.assertEqual(basis, 10000.0)
        self.assertFalse(has_sufficient_history)

        # 3 months of historical expenses -> reliable rolling average
        FinancialService.add_expense(self.test_user_id, 'Past Rent', 12000.0, 'Rent', '2026-09-10')
        FinancialService.add_expense(self.test_user_id, 'Earlier Rent', 14000.0, 'Rent', '2026-08-10')
        basis_multi, has_sufficient_multi = get_user_monthly_expense_basis(self.test_user_id, '2026-10-31')
        self.assertTrue(has_sufficient_multi)
        # Average of (10000 + 12000 + 14000) / 3 = 12000.00
        self.assertEqual(basis_multi, 12000.00)

        # Runway calculation with dedicated emergency fund
        health_with_runway = calculate_financial_health(
            total_income=40000.0,
            total_expenses=10000.0,
            emergency_fund=36000.0,
            emergency_fund_configured=True,
            monthly_expense_basis=basis_multi,
            has_sufficient_expense_history=has_sufficient_multi
        )
        # Runway = 36000 / 12000 = 3.0 months
        self.assertEqual(health_with_runway['emergency_fund_ratio'], 3.0)
        self.assertEqual(health_with_runway['emergency_fund_status'], "Adequate")
        self.assertEqual(health_with_runway['runway_label'], "3.0 months")

    # =========================================================================
    # STEP 5: OVERALL FINANCIAL HEALTH SCORE BEHAVIOR
    # =========================================================================

    def test_09_financial_health_score_behavior(self):
        """
        Verify that score is bounded in [0, 100], and responds accurately
        to savings rate, expense ratio, emergency runway, budget adherence, and goals.
        """
        # Scenario A: Excellent Profile
        # Income: 100,000, Expenses: 30,000 (30% expense ratio, 70% savings rate)
        # Emergency Fund: 180,000 (6 months runway), Budget: 35,000 (spent <= budget), Goals: 2 active
        excellent = calculate_financial_health(
            total_income=100000,
            total_expenses=30000,
            emergency_fund=180000,
            total_budget=35000,
            active_goals_count=2,
            emergency_fund_configured=True,
            monthly_expense_basis=30000
        )
        self.assertGreaterEqual(excellent['score'], 85)
        self.assertEqual(excellent['health_status'], "Excellent")
        self.assertLessEqual(excellent['score'], 100)

        # Scenario B: Poor Profile
        # Income: 20,000, Expenses: 28,000 (negative savings, >100% burn)
        # Emergency Fund: 0 (not configured), Over budget, Goals: 0
        poor = calculate_financial_health(
            total_income=20000,
            total_expenses=28000,
            emergency_fund=0,
            total_budget=20000,
            active_goals_count=0,
            emergency_fund_configured=False,
            monthly_expense_basis=28000
        )
        self.assertLess(poor['score'], 35)
        self.assertEqual(poor['health_status'], "Poor")


def run_tests():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFinancialCalculations)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
