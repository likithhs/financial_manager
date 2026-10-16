"""
Finora Platform - Phase 4 Database Reliability & Transaction Safety Test Suite
Tests:
- Distinguish empty query results vs genuine query failures (DatabaseQueryError)
- Database connection failure handling (DatabaseConnectionError)
- Atomic transaction commit and rollback (no partial writes on failure)
- Goal creation with initial contribution and subsequent contribution history
- Explicit backend selection (MySQL primary, SQLite local/testing)
- SQLite schema completeness across all core and supplementary tables
"""

import os
import unittest
import tempfile
from decimal import Decimal
from config import Config
from database import (
    query_db,
    execute_db,
    transaction_scope,
    init_db,
    get_db_connection,
    DatabaseError,
    DatabaseConnectionError,
    DatabaseQueryError,
    DatabaseTransactionError,
)
from services.goal_service import GoalService
from services.financial_service import FinancialService


class TestDatabaseReliability(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Ensure test user is created in MySQL for live tests."""
        cls.test_email = "test_reliability@finora.local"
        try:
            execute_db("DELETE FROM users WHERE email = %s", (cls.test_email,))
            cls.test_user_id = execute_db("""
                INSERT INTO users (name, email, password, password_hash, role)
                VALUES (%s, %s, %s, %s, %s)
            """, ("Reliability Tester", cls.test_email, "hashed_pwd_placeholder", "hashed_pwd_placeholder", "user"))
        except Exception as e:
            raise RuntimeError(f"Failed to prepare MySQL test environment: {e}")

    @classmethod
    def tearDownClass(cls):
        """Clean up test user data."""
        if hasattr(cls, 'test_user_id') and cls.test_user_id:
            try:
                execute_db("DELETE FROM goal_contributions WHERE user_id = %s", (cls.test_user_id,))
                execute_db("DELETE FROM financial_goals WHERE user_id = %s", (cls.test_user_id,))
                execute_db("DELETE FROM users WHERE id = %s", (cls.test_user_id,))
            except Exception:
                pass

    def setUp(self):
        """Clean up test goals and contributions before each test."""
        execute_db("DELETE FROM goal_contributions WHERE user_id = %s", (self.test_user_id,))
        execute_db("DELETE FROM financial_goals WHERE user_id = %s", (self.test_user_id,))

    # -------------------------------------------------------------
    # 1. Distinguish Empty Results vs Query Failures
    # -------------------------------------------------------------
    def test_empty_results_vs_query_failure(self):
        """Verify valid empty query returns [] or None, while syntax/missing table raises DatabaseQueryError."""
        # Valid query with zero rows returns []
        empty_rows = query_db("SELECT * FROM financial_goals WHERE user_id = %s", (-999999,))
        self.assertEqual(empty_rows, [])

        # Valid query with one=True and zero rows returns None
        empty_one = query_db("SELECT * FROM financial_goals WHERE user_id = %s", (-999999,), one=True)
        self.assertIsNone(empty_one)

        # Invalid query syntax must raise DatabaseQueryError, NOT return []
        with self.assertRaises(DatabaseQueryError):
            query_db("SELECT NON_EXISTENT_SYNTAX FROM financial_goals WHERE user_id = %s", (self.test_user_id,))

        # Missing table must raise DatabaseQueryError, NOT return []
        with self.assertRaises(DatabaseQueryError):
            query_db("SELECT * FROM completely_missing_table_xyz_123")

    # -------------------------------------------------------------
    # 2. Connection Failure Handling
    # -------------------------------------------------------------
    def test_invalid_engine_raises_connection_error(self):
        """Verify unsupported or broken backend specification raises DatabaseConnectionError."""
        with self.assertRaises(DatabaseConnectionError):
            get_db_connection(engine='postgres')

    # -------------------------------------------------------------
    # 3. Atomic Transaction Scope: Commit
    # -------------------------------------------------------------
    def test_transaction_commit_success(self):
        """Verify all operations inside transaction_scope commit successfully together."""
        with transaction_scope() as tx:
            g_id = tx.execute("""
                INSERT INTO financial_goals (user_id, name, goal_name, target_amount, current_amount, current_savings, target_date, priority, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (self.test_user_id, "Tx Test Goal", "Tx Test Goal", 25000, 5000, 5000, "2027-01-01", "High", "In Progress"))

            tx.execute("""
                INSERT INTO goal_contributions (goal_id, user_id, amount, contribution_date, description)
                VALUES (%s, %s, %s, %s, %s)
            """, (g_id, self.test_user_id, 5000, "2026-10-16", "Tx initial deposit"))

        # Both records must now exist in the database
        saved_goal = query_db("SELECT * FROM financial_goals WHERE id = %s", (g_id,), one=True)
        self.assertIsNotNone(saved_goal)
        self.assertEqual(float(saved_goal['current_amount']), 5000.0)

        contribs = query_db("SELECT * FROM goal_contributions WHERE goal_id = %s", (g_id,))
        self.assertEqual(len(contribs), 1)
        self.assertEqual(float(contribs[0]['amount']), 5000.0)

    # -------------------------------------------------------------
    # 4. Atomic Transaction Scope: Rollback on Failure
    # -------------------------------------------------------------
    def test_transaction_rollback_on_failure(self):
        """Verify that on failure, transaction_scope rolls back all operations with no partial writes."""
        goal_name = "Rollback Goal Should Not Exist"

        with self.assertRaises(DatabaseTransactionError):
            with transaction_scope() as tx:
                g_id = tx.execute("""
                    INSERT INTO financial_goals (user_id, name, goal_name, target_amount, current_amount, current_savings, target_date, priority, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (self.test_user_id, goal_name, goal_name, 50000, 10000, 10000, "2027-01-01", "High", "In Progress"))

                # Intentional error causing rollback: insert into non-existent table
                tx.execute("INSERT INTO non_existent_table_cause_rollback (col) VALUES (1)")

        # The goal must NOT have been saved
        orphan = query_db("SELECT * FROM financial_goals WHERE user_id = %s AND name = %s", (self.test_user_id, goal_name), one=True)
        self.assertIsNone(orphan, "Transaction failed to roll back: orphan goal was persisted!")

    # -------------------------------------------------------------
    # 5. Goal Contribution History & Atomic Balance Updates
    # -------------------------------------------------------------
    def test_goal_service_atomic_lifecycle(self):
        """Test GoalService create_goal and add_contribution maintain atomic balance and contribution history."""
        # 1. Create goal with initial deposit
        goal_id = GoalService.create_goal(
            user_id=self.test_user_id,
            name="Emergency Car Repair",
            target_amount=40000.0,
            initial_savings=10000.0,
            target_date_str="2027-05-01",
            priority="High",
            status="In Progress"
        )
        self.assertIsNotNone(goal_id)

        # Check goal record
        goal = query_db("SELECT * FROM financial_goals WHERE id = %s", (goal_id,), one=True)
        self.assertEqual(float(goal['current_amount']), 10000.0)
        self.assertEqual(goal['status'], 'In Progress')

        # Check initial contribution record
        contribs = query_db("SELECT * FROM goal_contributions WHERE goal_id = %s ORDER BY id ASC", (goal_id,))
        self.assertEqual(len(contribs), 1)
        self.assertEqual(float(contribs[0]['amount']), 10000.0)
        self.assertEqual(contribs[0]['description'], "Initial deposit")

        # 2. Add second contribution
        success = GoalService.add_contribution(goal_id, self.test_user_id, 15000.0, "Monthly bonus deposit")
        self.assertTrue(success)

        # Goal balance must now be 25,000
        updated_goal = query_db("SELECT * FROM financial_goals WHERE id = %s", (goal_id,), one=True)
        self.assertEqual(float(updated_goal['current_amount']), 25000.0)
        self.assertEqual(updated_goal['status'], 'In Progress')

        # Contribution records must now be 2
        contribs2 = query_db("SELECT * FROM goal_contributions WHERE goal_id = %s ORDER BY id ASC", (goal_id,))
        self.assertEqual(len(contribs2), 2)
        self.assertEqual(float(contribs2[1]['amount']), 15000.0)

        # 3. Add final contribution reaching target (25,000 + 15,000 = 40,000)
        success_reach = GoalService.add_contribution(goal_id, self.test_user_id, 15000.0, "Final completion deposit")
        self.assertTrue(success_reach)

        final_goal = query_db("SELECT * FROM financial_goals WHERE id = %s", (goal_id,), one=True)
        self.assertEqual(float(final_goal['current_amount']), 40000.0)
        self.assertEqual(final_goal['status'], 'Completed')

    # -------------------------------------------------------------
    # 6. FinancialService Atomic add_funds_to_goal
    # -------------------------------------------------------------
    def test_financial_service_atomic_add_funds(self):
        """Test FinancialService.add_funds_to_goal records contribution and updates balance atomically."""
        g_id = FinancialService.add_goal(
            user_id=self.test_user_id,
            name="Laptop Fund",
            target_amount=60000.0,
            initial_amount=15000.0,
            status="In Progress"
        )
        self.assertIsNotNone(g_id)

        # Initial contribution exists
        contribs = query_db("SELECT * FROM goal_contributions WHERE goal_id = %s", (g_id,))
        self.assertEqual(len(contribs), 1)
        self.assertEqual(float(contribs[0]['amount']), 15000.0)

        # Add funds
        ok = FinancialService.add_funds_to_goal(g_id, self.test_user_id, 10000.0, "Freelance payment")
        self.assertTrue(ok)

        g = query_db("SELECT * FROM financial_goals WHERE id = %s", (g_id,), one=True)
        self.assertEqual(float(g['current_amount']), 25000.0)

        all_c = query_db("SELECT * FROM goal_contributions WHERE goal_id = %s ORDER BY id ASC", (g_id,))
        self.assertEqual(len(all_c), 2)
        self.assertEqual(float(all_c[1]['amount']), 10000.0)

    # -------------------------------------------------------------
    # 7. SQLite Schema Completeness & Compatibility
    # -------------------------------------------------------------
    def test_sqlite_schema_completeness(self):
        """Verify SQLite backend initializes with all 11 required tables and supports operations."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tf:
            test_db_path = tf.name

        try:
            # Override SQLite path
            old_path = Config.SQLITE_PATH
            Config.SQLITE_PATH = test_db_path

            # Initialize schema
            init_db(engine='sqlite')

            conn, db_type = get_db_connection(engine='sqlite')
            self.assertEqual(db_type, 'sqlite')
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = {row[0] for row in cur.fetchall()}

            required_tables = [
                'users',
                'financial_profiles',
                'expense_categories',
                'income',
                'incomes',
                'expenses',
                'budgets',
                'financial_goals',
                'goal_contributions',
                'investment_categories',
                'recommendations',
                'chat_history',
                'watchlist',
                'portfolio',
                'risk_assessments',
                'market_cache',
                'portfolios',
                'portfolio_holdings',
                'stock_watchlist',
                'stocks'
            ]

            for table in required_tables:
                self.assertIn(table, tables, f"Missing table in SQLite schema: {table}")

            # Verify transactional write in SQLite
            cur.execute("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                        ("SQLite User", "sqlite@local.test", "dummy_hash"))
            u_id = cur.lastrowid
            conn.commit()

            cur.execute("SELECT name FROM users WHERE id = ?", (u_id,))
            user_row = cur.fetchone()
            self.assertEqual(user_row[0], "SQLite User")

            conn.close()
        finally:
            Config.SQLITE_PATH = old_path
            try:
                if os.path.exists(test_db_path):
                    os.unlink(test_db_path)
            except Exception:
                pass


if __name__ == '__main__':
    unittest.main()
