import unittest
import re
import sqlite3
from app import app
from database import query_db, execute_db
from werkzeug.security import generate_password_hash, check_password_hash

class TestUserAccountsLogin(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = True
        self.client = app.test_client()

    def _get_csrf_token(self):
        res = self.client.get('/login')
        m = re.search(r'name="csrf_token"\s+value="([^"]+)"', res.get_data(as_text=True))
        self.assertIsNotNone(m, "CSRF token must be present on /login")
        return m.group(1)

    def test_user_records_exist_and_conform_to_schema(self):
        """Verify both Pragnya and Mangesh user accounts exist and have valid fields."""
        u2 = query_db("SELECT * FROM users WHERE email = %s", ('pragnya@gmail.com',), one=True)
        self.assertIsNotNone(u2, "User 2 (pragnya@gmail.com) must exist")
        self.assertEqual(u2['role'], 'user')
        self.assertTrue(len(u2['password_hash']) > 30, "User 2 password_hash must be a valid complete hash")
        self.assertIn('$', u2['password_hash'], "User 2 password_hash must contain '$' delimiters")

        u3 = query_db("SELECT * FROM users WHERE email = %s", ('mangesh@gmail.com',), one=True)
        self.assertIsNotNone(u3, "User 3 (mangesh@gmail.com) must exist")
        self.assertEqual(u3['role'], 'user')
        self.assertTrue(len(u3['password_hash']) > 30, "User 3 password_hash must be a valid complete hash")
        self.assertIn('$', u3['password_hash'], "User 3 password_hash must contain '$' delimiters")

    def test_invalid_credentials_handling_no_500(self):
        """Invalid passwords for both accounts must never raise a 500 internal server error."""
        for email in ['pragnya@gmail.com', 'mangesh@gmail.com', 'admin@financialmanager.com']:
            csrf_token = self._get_csrf_token()
            res = self.client.post('/login', data={
                'csrf_token': csrf_token,
                'email': email,
                'password': 'DefinitelyIncorrectPassword123!'
            }, follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertFalse(b"An unexpected server fault occurred" in res.data, f"500 fault triggered on {email}")
            self.assertTrue(b"Invalid email address or password" in res.data, f"Expected flash warning on {email}")

    def test_malformed_hash_in_db_fails_gracefully_no_500(self):
        """A user account with a malformed/truncated hash must fail gracefully without 500 error."""
        # Create a temporary user with truncated/corrupt hash
        test_email = "malformed_hash_test@example.com"
        execute_db("DELETE FROM users WHERE email = %s", (test_email,))
        execute_db("""
            INSERT INTO users (name, email, password_hash, password, role)
            VALUES (%s, %s, %s, %s, 'user')
        """, ("Malformed Tester", test_email, "scrypt:32768:8:1", "scrypt:32768:8:1"))

        try:
            csrf_token = self._get_csrf_token()
            res = self.client.post('/login', data={
                'csrf_token': csrf_token,
                'email': test_email,
                'password': 'AnyPassword123!'
            }, follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertFalse(b"An unexpected server fault occurred" in res.data)
            self.assertTrue(b"Invalid email address or password" in res.data)
        finally:
            execute_db("DELETE FROM users WHERE email = %s", (test_email,))

    def test_authenticated_sessions_and_context_injection(self):
        """Test both user 2 and user 3 sessions load /home, /dashboard, /settings with 200 OK."""
        for uid, name, email in [(2, 'Pragnya', 'pragnya@gmail.com'), (3, 'mangesh', 'mangesh@gmail.com')]:
            with self.client.session_transaction() as sess:
                sess['user_id'] = uid
                sess['user_name'] = name
                sess['user_email'] = email
                sess['user_role'] = 'user'

            # Test Home
            res_home = self.client.get('/home')
            self.assertEqual(res_home.status_code, 200)
            self.assertIn(name.encode(), res_home.data)

            # Test Dashboard
            res_dash = self.client.get('/dashboard')
            self.assertEqual(res_dash.status_code, 200)

            # Test Settings
            res_set = self.client.get('/settings')
            self.assertEqual(res_set.status_code, 200)
            self.assertIn(email.encode(), res_set.data)

if __name__ == '__main__':
    unittest.main()
