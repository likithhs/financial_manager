"""
Finora Test Suite - Authentication & Password Validation Tests
Covers Registration, Login, Session Lifecycle, Password Policy (NIST SP 800-63B),
and Email Normalization.
"""

import os
import re
import tempfile
import unittest
from flask import session
from werkzeug.security import check_password_hash

from config import Config
from app import create_app
import database


class TestAuthConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = True
    DB_ENGINE = 'sqlite'
    RATELIMIT_ENABLED = False  # Disabled for functional auth testing to avoid test interference


class AuthTestCase(unittest.TestCase):
    def setUp(self):
        # Create a unique temporary SQLite database file for isolation
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        TestAuthConfig.SQLITE_PATH = self.db_path

        # Initialize test app
        self.app = create_app(TestAuthConfig)
        self.client = self.app.test_client()

        # Initialize schema inside app context
        with self.app.app_context():
            database.init_db(engine='sqlite')

    def tearDown(self):
        try:
            os.close(self.db_fd)
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
        except Exception:
            pass

    def _get_csrf_token(self, url):
        """Helper to fetch a valid CSRF token from a form page."""
        resp = self.client.get(url)
        html = resp.get_data(as_text=True)
        match = re.search(r'name="csrf_token" value="([^"]+)"', html)
        self.assertIsNotNone(match, f"CSRF token not found on {url}")
        return match.group(1)

    # -------------------------------------------------------------
    # 1. Registration Tests
    # -------------------------------------------------------------
    def test_new_user_registration_success(self):
        """Verify that a new user with valid details and a >=12 character password registers successfully."""
        csrf_token = self._get_csrf_token('/register')
        res = self.client.post('/register', data={
            'csrf_token': csrf_token,
            'name': 'Jane Doe',
            'email': 'jane.doe@example.com',
            'password': 'SecurePassphrase2026!',
            'confirm_password': 'SecurePassphrase2026!',
            'age': '28',
            'occupation': 'Financial Analyst',
            'financial_exp': 'Intermediate',
            'investment_exp': 'Mutual Funds / SIP'
        }, follow_redirects=True)

        self.assertEqual(res.status_code, 200)
        self.assertIn('Registration successful! You can now log in.', res.get_data(as_text=True))

        # Verify user exists in database and password is encrypted (not plaintext)
        with self.app.app_context():
            user = database.query_db("SELECT * FROM users WHERE email = %s", ('jane.doe@example.com',), one=True)
            self.assertIsNotNone(user)
            self.assertEqual(user['name'], 'Jane Doe')
            self.assertNotEqual(user['password'], 'SecurePassphrase2026!')
            self.assertTrue(check_password_hash(user['password'], 'SecurePassphrase2026!'))

    def test_registration_password_shorter_than_12_chars_rejected(self):
        """Verify that passwords shorter than 12 characters are strictly rejected by the backend."""
        csrf_token = self._get_csrf_token('/register')
        res = self.client.post('/register', data={
            'csrf_token': csrf_token,
            'name': 'Short Password User',
            'email': 'short@example.com',
            'password': 'Short123!',  # Only 9 characters
            'confirm_password': 'Short123!'
        }, follow_redirects=True)

        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)
        self.assertIn('Password must be at least 12 characters long', html)

        # Ensure user was NOT created
        with self.app.app_context():
            user = database.query_db("SELECT id FROM users WHERE email = %s", ('short@example.com',), one=True)
            self.assertIsNone(user)

    def test_registration_special_characters_in_password(self):
        """Verify that strong passwords with diverse symbols, unicode, and spaces succeed."""
        csrf_token = self._get_csrf_token('/register')
        complex_password = 'Correct Horse Battery #2026!$%'
        res = self.client.post('/register', data={
            'csrf_token': csrf_token,
            'name': 'Crypto User',
            'email': 'crypto@example.com',
            'password': complex_password,
            'confirm_password': complex_password
        }, follow_redirects=True)

        self.assertEqual(res.status_code, 200)
        self.assertIn('Registration successful', res.get_data(as_text=True))

        with self.app.app_context():
            user = database.query_db("SELECT * FROM users WHERE email = %s", ('crypto@example.com',), one=True)
            self.assertIsNotNone(user)
            self.assertTrue(check_password_hash(user['password'], complex_password))

    def test_duplicate_email_registration_prevention(self):
        """Verify that registering with an existing email displays an informative message and blocks duplicate."""
        csrf_token1 = self._get_csrf_token('/register')
        self.client.post('/register', data={
            'csrf_token': csrf_token1,
            'name': 'Original User',
            'email': 'duplicate@example.com',
            'password': 'Password123456!',
            'confirm_password': 'Password123456!'
        }, follow_redirects=True)

        # Attempt to register again with same email
        csrf_token2 = self._get_csrf_token('/register')
        res = self.client.post('/register', data={
            'csrf_token': csrf_token2,
            'name': 'Imposter User',
            'email': 'duplicate@example.com',
            'password': 'DifferentPassword123!',
            'confirm_password': 'DifferentPassword123!'
        }, follow_redirects=True)

        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)
        self.assertIn('already exists', html.lower())

    def test_email_normalization(self):
        """Verify that email addresses with leading/trailing whitespace and uppercase are normalized."""
        csrf_token = self._get_csrf_token('/register')
        res = self.client.post('/register', data={
            'csrf_token': csrf_token,
            'name': 'Normalized User',
            'email': '   MyEmail.Normalized@Example.COM   ',
            'password': 'Password123456!',
            'confirm_password': 'Password123456!'
        }, follow_redirects=True)

        self.assertEqual(res.status_code, 200)

        # Check in DB that it was stored as lowercase and trimmed
        with self.app.app_context():
            user = database.query_db("SELECT * FROM users WHERE email = %s", ('myemail.normalized@example.com',), one=True)
            self.assertIsNotNone(user)
            self.assertEqual(user['email'], 'myemail.normalized@example.com')

    # -------------------------------------------------------------
    # 2. Login & Session Lifecycle Tests
    # -------------------------------------------------------------
    def test_login_success_and_dashboard_redirect(self):
        """Verify that valid credentials log in, set session variables, and redirect to /home."""
        # 1. Register user
        csrf_reg = self._get_csrf_token('/register')
        self.client.post('/register', data={
            'csrf_token': csrf_reg,
            'name': 'John Investor',
            'email': 'john@example.com',
            'password': 'MyStrongPassword123!',
            'confirm_password': 'MyStrongPassword123!'
        }, follow_redirects=True)

        # 2. Login
        csrf_login = self._get_csrf_token('/login')
        res = self.client.post('/login', data={
            'csrf_token': csrf_login,
            'email': 'john@example.com',
            'password': 'MyStrongPassword123!'
        }, follow_redirects=False)

        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.headers.get('Location'), '/home')

        # 3. Follow redirect and check session
        with self.client:
            home_res = self.client.get('/home')
            self.assertEqual(home_res.status_code, 200)
            self.assertEqual(session.get('user_email'), 'john@example.com')
            self.assertEqual(session.get('user_role'), 'user')
            self.assertIsNotNone(session.get('user_id'))

    def test_login_incorrect_password_fails(self):
        """Verify that an incorrect password fails with a user-friendly error message."""
        csrf_reg = self._get_csrf_token('/register')
        self.client.post('/register', data={
            'csrf_token': csrf_reg,
            'name': 'Alice User',
            'email': 'alice@example.com',
            'password': 'CorrectPassword123!',
            'confirm_password': 'CorrectPassword123!'
        }, follow_redirects=True)

        csrf_login = self._get_csrf_token('/login')
        res = self.client.post('/login', data={
            'csrf_token': csrf_login,
            'email': 'alice@example.com',
            'password': 'WrongPassword999!'
        }, follow_redirects=True)

        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)
        self.assertIn('Invalid email address or password', html)

        # Verify session is not set
        with self.client:
            self.client.get('/login')
            self.assertNotIn('user_id', session)

    def test_login_nonexistent_email_fails(self):
        """Verify that attempting to log in with an unregistered email fails safely."""
        csrf_login = self._get_csrf_token('/login')
        res = self.client.post('/login', data={
            'csrf_token': csrf_login,
            'email': 'ghost@example.com',
            'password': 'SomePassword123!'
        }, follow_redirects=True)

        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)
        self.assertIn('Invalid email address or password', html)

    def test_admin_login_redirects_to_admin_dashboard(self):
        """Verify that an admin user logs in and is redirected to /admin/."""
        with self.app.app_context():
            database.create_admin_user('admin@finora.test', 'AdminPassword123!', name='Master Admin')

        csrf_login = self._get_csrf_token('/login')
        res = self.client.post('/login', data={
            'csrf_token': csrf_login,
            'email': 'admin@finora.test',
            'password': 'AdminPassword123!'
        }, follow_redirects=False)

        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.headers.get('Location'), '/admin/')

    def test_logout_clears_session(self):
        """Verify that logging out clears all session attributes and redirects to login."""
        # Register and login
        csrf_reg = self._get_csrf_token('/register')
        self.client.post('/register', data={
            'csrf_token': csrf_reg,
            'name': 'Logout User',
            'email': 'logout@example.com',
            'password': 'Password123456!',
            'confirm_password': 'Password123456!'
        }, follow_redirects=True)

        csrf_login = self._get_csrf_token('/login')
        self.client.post('/login', data={
            'csrf_token': csrf_login,
            'email': 'logout@example.com',
            'password': 'Password123456!'
        }, follow_redirects=True)

        # Trigger logout
        res = self.client.get('/logout', follow_redirects=False)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.headers.get('Location'), '/login')

        with self.client:
            self.client.get('/login')
            self.assertNotIn('user_id', session)


if __name__ == '__main__':
    unittest.main()
