"""
Finora - SQLite Decimal Compatibility & Service Reliability Tests
Verifies SQLite decimal binding, monetary precision, service integrity, and admin initialization.
"""

import os
import unittest
import tempfile
from decimal import Decimal
from datetime import date

# Set environment before loading application
temp_dir = tempfile.mkdtemp()
temp_sqlite = os.path.join(temp_dir, 'test_decimal.db')
os.environ['DB_ENGINE'] = 'sqlite'
os.environ['SQLITE_PATH'] = temp_sqlite
os.environ['TESTING'] = 'True'

from database import init_db, get_db_connection, query_db, execute_db, create_admin_user
from services.goal_service import GoalService
from services.income_service import IncomeService
from services.expense_service import ExpenseService
from werkzeug.security import check_password_hash


class TestSQLiteDecimalCompatibility(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize a fresh SQLite schema for isolated testing."""
        init_db(engine='sqlite')

        # Insert a dedicated test user
        cls.user_id = execute_db("""
            INSERT INTO users (name, email, password, password_hash, role)
            VALUES (?, ?, ?, ?, ?)
        """, ('Decimal Test User', 'decimal_user@finora.test', 'UserPass1234!', 'UserPass1234!', 'user'))

    @classmethod
    def tearDownClass(cls):
        """Clean up temporary test database."""
        try:
            if os.path.exists(temp_sqlite):
                os.remove(temp_sqlite)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
        except Exception:
            pass

    def test_01_goal_service_decimal_creation_and_contributions(self):
        """Verify GoalService handles Decimal target and contribution amounts cleanly on SQLite."""
        target_amount = Decimal("25000.75")
        initial_savings = Decimal("5000.25")

        # Test GoalService.create_goal
        goal_id = GoalService.create_goal(
            user_id=self.user_id,
            name="Emergency Fund",
            target_amount=target_amount,
            initial_savings=initial_savings,
            target_date_str="2027-12-31",
            priority="High",
            description="6-month liquidity reserve"
        )
        self.assertIsNotNone(goal_id)
        self.assertGreater(goal_id, 0)

        # Retrieve goal and verify monetary values
        goals = GoalService.get_user_goals(self.user_id)
        created_goal = next((g for g in goals if g['id'] == goal_id), None)
        self.assertIsNotNone(created_goal)
        self.assertEqual(created_goal['target_amount'], 25000.75)
        self.assertEqual(created_goal['current_amount'], 5000.25)
        self.assertEqual(created_goal['remaining'], 20000.50)
        self.assertTrue(created_goal['is_active'])

        # Test GoalService.add_contribution with Decimal
        contribution_amount = Decimal("7500.50")
        success = GoalService.add_contribution(
            goal_id=goal_id,
            user_id=self.user_id,
            amount=contribution_amount,
            description="Monthly savings allocation"
        )
        self.assertTrue(success)

        # Verify updated progress
        goals_updated = GoalService.get_user_goals(self.user_id)
        updated_goal = next((g for g in goals_updated if g['id'] == goal_id), None)
        self.assertEqual(updated_goal['current_amount'], 12500.75)
        self.assertEqual(updated_goal['remaining'], 12500.00)
        self.assertAlmostEqual(updated_goal['progress_pct'], 50.0, places=1)

    def test_02_income_service_decimal_handling_and_totals(self):
        """Verify IncomeService stores and aggregates Decimal income amounts on SQLite."""
        inc_amount_1 = Decimal("65000.50")
        inc_amount_2 = Decimal("12499.50")

        # Add two income entries with Decimal amounts
        id1 = IncomeService.add_income(
            user_id=self.user_id,
            source="Primary Engineering Salary",
            amount=inc_amount_1,
            category="Salary / Wages",
            date_str="2026-10-01",
            description="Direct deposit"
        )
        id2 = IncomeService.add_income(
            user_id=self.user_id,
            source="Freelance Technical Writing",
            amount=inc_amount_2,
            category="Freelance / Consulting",
            date_str="2026-10-15",
            description="Consulting milestone"
        )

        self.assertIsNotNone(id1)
        self.assertIsNotNone(id2)

        # Verify aggregated total income
        total_income = IncomeService.get_total_income(self.user_id)
        expected_total = Decimal("77500.00")
        self.assertEqual(total_income, expected_total)

        # Verify transaction list retrieval
        incomes = IncomeService.get_user_incomes(self.user_id)
        self.assertGreaterEqual(len(incomes), 2)
        income_sources = [inc['source'] for inc in incomes]
        self.assertIn("Primary Engineering Salary", income_sources)
        self.assertIn("Freelance Technical Writing", income_sources)

    def test_03_expense_service_decimal_handling_and_totals(self):
        """Verify ExpenseService stores and calculates Decimal expense entries on SQLite."""
        exp_amount_1 = Decimal("18500.75")
        exp_amount_2 = Decimal("4250.25")

        id1 = ExpenseService.add_expense(
            user_id=self.user_id,
            title="Apartment Rent",
            amount=exp_amount_1,
            category="Rent",
            date_str="2026-10-02",
            description="Monthly apartment lease"
        )
        id2 = ExpenseService.add_expense(
            user_id=self.user_id,
            title="Supermarket Groceries",
            amount=exp_amount_2,
            category="Food",
            date_str="2026-10-05",
            description="Weekly grocery run"
        )

        self.assertIsNotNone(id1)
        self.assertIsNotNone(id2)

        # Verify aggregated total expenses
        total_expenses = ExpenseService.get_total_expenses(self.user_id)
        expected_total = Decimal("22751.00")
        self.assertEqual(total_expenses, expected_total)

        # Verify user expenses list
        expenses = ExpenseService.get_user_expenses(self.user_id)
        self.assertGreaterEqual(len(expenses), 2)
        titles = [exp['title'] for exp in expenses]
        self.assertIn("Apartment Rent", titles)
        self.assertIn("Supermarket Groceries", titles)

    def test_04_create_admin_user_on_fresh_sqlite(self):
        """Verify create_admin_user initializes schema, enforces 12-char password, and hashes credentials."""
        # 1. Password shorter than 12 chars should fail validation
        with self.assertRaises(ValueError) as ctx:
            create_admin_user("admin@test.local", "shortpass", name="Admin", engine='sqlite')
        self.assertIn("at least 12 characters", str(ctx.exception))

        # 2. Invalid email should fail validation
        with self.assertRaises(ValueError):
            create_admin_user("invalid-email", "SecurePass1234!", name="Admin", engine='sqlite')

        # 3. Valid admin creation
        admin_id, is_new = create_admin_user("finora_admin@test.local", "SuperSecurePass1234!", name="Master Admin", engine='sqlite')
        self.assertTrue(is_new)
        self.assertGreater(admin_id, 0)

        # 4. Verify admin user row in SQLite
        admin_row = query_db("SELECT id, name, email, role, password_hash FROM users WHERE email = ?", ("finora_admin@test.local",), one=True)
        self.assertIsNotNone(admin_row)
        self.assertEqual(admin_row['role'], 'admin')
        self.assertEqual(admin_row['name'], 'Master Admin')
        self.assertTrue(check_password_hash(admin_row['password_hash'], "SuperSecurePass1234!"))

        # 5. Idempotent update: promoting existing user to admin
        updated_id, is_new2 = create_admin_user("finora_admin@test.local", "NewSuperSecurePass5678!", name="Updated Admin", engine='sqlite')
        self.assertFalse(is_new2)
        self.assertEqual(updated_id, admin_id)

        admin_updated = query_db("SELECT password_hash, name FROM users WHERE id = ?", (admin_id,), one=True)
        self.assertEqual(admin_updated['name'], 'Updated Admin')
        self.assertTrue(check_password_hash(admin_updated['password_hash'], "NewSuperSecurePass5678!"))


if __name__ == '__main__':
    unittest.main()
