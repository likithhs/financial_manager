"""
Finora Test Suite - Database Persistence & Multi-Engine Integrity Tests
Covers SQLite Persistence across application restarts, zero data loss on re-initialization,
and strict MySQL engine isolation (no silent fallbacks).
"""

import os
import tempfile
import unittest
from unittest.mock import patch
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from app import create_app
import database
from database import DatabaseConnectionError


class DatabasePersistenceTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')

    def tearDown(self):
        try:
            os.close(self.db_fd)
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
        except Exception:
            pass

    def test_sqlite_persistence_across_app_restarts(self):
        """
        Critical Render Persistence Test:
        Simulates an application deployment/restart cycle.
        Ensures users and financial records written to SQLite remain 100% intact after the app restarts.
        """
        class AppConfig1(Config):
            TESTING = True
            DB_ENGINE = 'sqlite'
            SQLITE_PATH = self.db_path

        # 1. Start App Lifecycle 1
        app1 = create_app(AppConfig1)
        with app1.app_context():
            pwd_hash = generate_password_hash('PersistentUserPass123!')
            user_id = database.execute_db("""
                INSERT INTO users (name, email, password, password_hash, role)
                VALUES (%s, %s, %s, %s, 'user')
            """, ('Persistent Investor', 'persist@finora.test', pwd_hash, pwd_hash))
            self.assertIsNotNone(user_id)

            # Write financial record
            inc_id = database.execute_db("""
                INSERT INTO incomes (user_id, source, amount, category, date)
                VALUES (%s, %s, %s, %s, '2026-11-01')
            """, (user_id, 'Monthly Retainer', 85000.00, 'Salary / Wages'))
            self.assertIsNotNone(inc_id)

        # 2. Simulate complete container restart / redeployment (App 1 terminated)
        del app1

        # 3. Start App Lifecycle 2 with same persistent file
        class AppConfig2(Config):
            TESTING = True
            DB_ENGINE = 'sqlite'
            SQLITE_PATH = self.db_path

        app2 = create_app(AppConfig2)
        with app2.app_context():
            # Query the user in the new app instance
            user = database.query_db("SELECT * FROM users WHERE email = %s", ('persist@finora.test',), one=True)
            self.assertIsNotNone(user, "User record disappeared after application restart!")
            self.assertEqual(user['name'], 'Persistent Investor')
            self.assertTrue(check_password_hash(user['password'], 'PersistentUserPass123!'))

            # Verify associated financial transactions survived
            incomes = database.query_db("SELECT * FROM incomes WHERE user_id = %s", (user['id'],))
            self.assertEqual(len(incomes), 1)
            self.assertEqual(incomes[0]['source'], 'Monthly Retainer')
            self.assertEqual(float(incomes[0]['amount']), 85000.00)

    def test_init_db_does_not_overwrite_existing_records(self):
        """
        Verify that running init_db() on application startup does not drop tables or delete records.
        """
        class AppConfig(Config):
            TESTING = True
            DB_ENGINE = 'sqlite'
            SQLITE_PATH = self.db_path

        app = create_app(AppConfig)
        with app.app_context():
            # Insert initial user
            pwd = generate_password_hash('KeepAlive123456!')
            database.execute_db("""
                INSERT INTO users (name, email, password, password_hash, role)
                VALUES (%s, %s, %s, %s, 'user')
            """, ('Pre-Existing User', 'keepalive@finora.test', pwd, pwd))

            # Run init_db() multiple times (simulating multiple restarts)
            database.init_db(engine='sqlite')
            database.init_db(engine='sqlite')

            # Verify record is still preserved
            user = database.query_db("SELECT * FROM users WHERE email = %s", ('keepalive@finora.test',), one=True)
            self.assertIsNotNone(user, "Record was wiped by init_db()!")
            self.assertEqual(user['email'], 'keepalive@finora.test')

    def test_mysql_engine_no_silent_fallback(self):
        """
        Verify that when DB_ENGINE='mysql' is configured:
        - If connection fails (e.g. unreachable host), it raises DatabaseConnectionError.
        - It NEVER silently falls back to SQLite.
        """
        with patch.object(Config, 'DB_HOST', 'nonexistent_mysql_host_999'):
            with self.assertRaises(DatabaseConnectionError):
                database.get_db_connection(engine='mysql')


if __name__ == '__main__':
    unittest.main()
