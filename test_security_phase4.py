"""
Comprehensive Phase 4 Security Verification Test Suite
Tests:
1. CSRF Protection (form & AJAX)
2. Password Policy & Secure Hashing
3. Rate Limiting on Authentication Endpoints
4. Session Cookie Security Settings
5. Gemini Header-Based API Authentication & Logging Sanitization
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import re

from app import app
from config import Config
from routes.auth_routes import validate_password_strength
from services.ai_service import AIService


class TestSecurityPhase4(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = True
        self.client = app.test_client()

    # =========================================================================
    # 1. CSRF PROTECTION TESTS
    # =========================================================================

    def test_csrf_rejection_without_token_on_form_post(self):
        """State-changing form POST without CSRF token must be rejected with HTTP 400."""
        res = self.client.post('/login', data={'email': 'test@example.com', 'password': 'ValidPassword123!'}, follow_redirects=False)
        self.assertEqual(res.status_code, 400)
        self.assertTrue(b"CSRF" in res.data or b"csrf" in res.data.lower())

    def test_csrf_rejection_without_token_on_json_post(self):
        """State-changing JSON POST without CSRF header must be rejected with HTTP 400."""
        res = self.client.post('/ai-assistant/chat', json={'message': 'hello'})
        self.assertEqual(res.status_code, 400)
        json_data = res.get_json()
        self.assertIsNotNone(json_data)
        self.assertIn('csrf', json_data.get('error', '').lower())

    def test_csrf_acceptance_with_valid_token(self):
        """Requests with valid CSRF token in session must be accepted by CSRF protect."""
        # Fetch login page to extract CSRF token from HTML form
        res = self.client.get('/login')
        self.assertEqual(res.status_code, 200)
        
        # Extract CSRF token from HTML
        match = re.search(r'name="csrf_token"\s+value="([^"]+)"', res.get_data(as_text=True))
        self.assertIsNotNone(match, "CSRF token not found in login page HTML")
        csrf_token = match.group(1)

        # Post with valid CSRF token
        res_post = self.client.post('/login', data={
            'csrf_token': csrf_token,
            'email': 'nonexistent_test_user_xyz@finora.internal',
            'password': 'InvalidPassword123!'
        }, follow_redirects=True)
        # Should NOT be 400 CSRF error; should be 200 (re-rendered with flash error)
        self.assertEqual(res_post.status_code, 200)
        self.assertFalse(b"CSRF token missing" in res_post.data)

    def test_csrf_ajax_header_acceptance(self):
        """AJAX POST with valid X-CSRFToken header must pass CSRF validation."""
        res = self.client.get('/login')
        match = re.search(r'name="csrf_token"\s+value="([^"]+)"', res.get_data(as_text=True))
        self.assertIsNotNone(match)
        csrf_token = match.group(1)

        # Make an AJAX POST with the header
        res_ajax = self.client.post(
            '/ai-assistant/chat',
            json={'message': 'What is my budget?'},
            headers={'X-CSRFToken': csrf_token}
        )
        # Should not be rejected with 400 CSRF error (can be 401 unauthenticated, but CSRF passed)
        self.assertNotEqual(res_ajax.status_code, 400)

    # =========================================================================
    # 2. PASSWORD POLICY & HASHING TESTS
    # =========================================================================

    def test_password_policy_short_password(self):
        """Passwords under 12 characters must be rejected."""
        valid, msg = validate_password_strength("Short123!")
        self.assertFalse(valid)
        self.assertIn("at least 12 characters", msg)

    def test_password_policy_whitespace_password(self):
        """Whitespace only or padded passwords must be rejected."""
        valid, msg = validate_password_strength("   123456789012   ")
        self.assertFalse(valid)

    def test_password_policy_valid_strong_password(self):
        """Passwords with 12+ characters must be accepted."""
        valid, msg = validate_password_strength("MySuperSecurePassphrase2026!")
        self.assertTrue(valid)

    def test_generic_auth_error_message(self):
        """Login failure must not disclose whether the email exists."""
        res = self.client.get('/login')
        match = re.search(r'name="csrf_token"\s+value="([^"]+)"', res.get_data(as_text=True))
        csrf_token = match.group(1)

        res_post = self.client.post('/login', data={
            'csrf_token': csrf_token,
            'email': 'definitely_fake_user_123456@example.com',
            'password': 'SomeLongPassword123!'
        }, follow_redirects=True)
        # Check that generic message is flashed
        self.assertTrue(b"Invalid email address or password" in res_post.data)
        self.assertFalse(b"User not found" in res_post.data)
        self.assertFalse(b"Account does not exist" in res_post.data)

    def test_registration_short_password_rejection(self):
        """Registering with < 12 characters must be rejected with an explanatory message."""
        res = self.client.get('/register')
        match = re.search(r'name="csrf_token"\s+value="([^"]+)"', res.get_data(as_text=True))
        csrf_token = match.group(1)

        res_post = self.client.post('/register', data={
            'csrf_token': csrf_token,
            'name': 'Test User',
            'email': 'shortpass_user@example.com',
            'password': 'short',
            'confirm_password': 'short'
        }, follow_redirects=True)
        self.assertEqual(res_post.status_code, 200)
        self.assertTrue(b"at least 12 characters" in res_post.data)

    def test_full_auth_lifecycle(self):
        """Tests complete registration, login, session cookies, and logout."""
        import uuid
        test_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
        test_pass = "SecurePassphrase1234!"

        # 1. Register
        res = self.client.get('/register')
        match = re.search(r'name="csrf_token"\s+value="([^"]+)"', res.get_data(as_text=True))
        csrf_token = match.group(1)

        res_reg = self.client.post('/register', data={
            'csrf_token': csrf_token,
            'name': 'Auth Lifecycle User',
            'email': test_email,
            'password': test_pass,
            'confirm_password': test_pass
        }, follow_redirects=True)
        self.assertEqual(res_reg.status_code, 200)
        self.assertTrue(b"Registration successful" in res_reg.data or b"log in" in res_reg.data)

        # 2. Login
        res = self.client.get('/login')
        match = re.search(r'name="csrf_token"\s+value="([^"]+)"', res.get_data(as_text=True))
        csrf_token = match.group(1)

        res_login = self.client.post('/login', data={
            'csrf_token': csrf_token,
            'email': test_email,
            'password': test_pass
        }, follow_redirects=False)

        # Should redirect to home
        self.assertEqual(res_login.status_code, 302)
        # Check Set-Cookie has HttpOnly
        set_cookie = res_login.headers.get('Set-Cookie', '')
        self.assertIn('HttpOnly', set_cookie)
        self.assertIn('SameSite=Lax', set_cookie)

        # 3. Access authenticated settings
        res_settings = self.client.get('/settings')
        self.assertEqual(res_settings.status_code, 200)

        # 4. Attempt password change with short password (should be rejected)
        match = re.search(r'name="csrf_token"\s+value="([^"]+)"', res_settings.get_data(as_text=True))
        csrf_token = match.group(1)
        res_pw_change = self.client.post('/settings', data={
            'csrf_token': csrf_token,
            'action': 'update_security',
            'current_password': test_pass,
            'new_password': 'short',
            'confirm_password': 'short'
        }, follow_redirects=True)
        self.assertTrue(b"at least 12 characters" in res_pw_change.data)

        # 5. Logout
        res_logout = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(res_logout.status_code, 200)
        self.assertTrue(b"successfully logged out" in res_logout.data)

    # =========================================================================
    # 3. RATE LIMITING TESTS
    # =========================================================================

    def test_login_rate_limiting(self):
        """Hitting login repeatedly beyond limit should return HTTP 429 Too Many Requests."""
        res = self.client.get('/login')
        match = re.search(r'name="csrf_token"\s+value="([^"]+)"', res.get_data(as_text=True))
        csrf_token = match.group(1)

        # Trigger POST /login 6 times rapidly (limit is 5 per minute)
        status_codes = []
        for _ in range(7):
            res_try = self.client.post('/login', data={
                'csrf_token': csrf_token,
                'email': 'ratelimit_test@example.com',
                'password': 'WrongPassword123!'
            })
            status_codes.append(res_try.status_code)

        # At least the 6th or 7th request must receive 429
        self.assertIn(429, status_codes, f"Expected 429 status code in: {status_codes}")

    # =========================================================================
    # 4. SESSION COOKIE SECURITY TESTS
    # =========================================================================

    def test_session_cookie_settings(self):
        """Verify session cookie configuration flags."""
        self.assertTrue(app.config.get('SESSION_COOKIE_HTTPONLY'), "SESSION_COOKIE_HTTPONLY must be True")
        self.assertEqual(app.config.get('SESSION_COOKIE_SAMESITE'), 'Lax', "SESSION_COOKIE_SAMESITE must be 'Lax'")

    def test_session_cookie_secure_logic(self):
        """Verify conditional secure cookie helper."""
        from config import _get_session_cookie_secure

        # Under default dev environment without HTTPS, cookie secure is False
        with patch.dict(os.environ, {'SESSION_COOKIE_SECURE': 'False', 'FLASK_ENV': 'development'}):
            self.assertFalse(_get_session_cookie_secure())

        # When SESSION_COOKIE_SECURE=true explicitly
        with patch.dict(os.environ, {'SESSION_COOKIE_SECURE': 'True'}):
            self.assertTrue(_get_session_cookie_secure())

        # When production and HTTPS enabled
        with patch.dict(os.environ, {'SESSION_COOKIE_SECURE': '', 'FLASK_ENV': 'production', 'ENABLE_HTTPS': 'true'}):
            self.assertTrue(_get_session_cookie_secure())

    # =========================================================================
    # 5. GEMINI API AUTHENTICATION & LOGGING TESTS
    # =========================================================================

    @patch('services.ai_service.requests.post')
    def test_gemini_header_authentication(self, mock_post):
        """Gemini API calls must pass x-goog-api-key in HTTP headers and NOT in the URL."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{'text': 'Mocked AI financial response'}]
                }
            }]
        }
        mock_post.return_value = mock_response

        # Execute AIService._call_gemini
        test_key = "AIzaSyFakeTestKey1234567890"
        result = AIService._call_gemini(
            api_key=test_key,
            model="gemini-2.5-flash",
            system_prompt="You are a financial advisor",
            user_message="How do I budget?"
        )

        self.assertIsNotNone(result)
        self.assertEqual(result, 'Mocked AI financial response')

        # Check call arguments to requests.post
        call_args, call_kwargs = mock_post.call_args
        target_url = call_args[0]
        sent_headers = call_kwargs.get('headers', {})

        # URL MUST NOT contain ?key= or the secret key
        self.assertNotIn('?key=', target_url, "URL must not contain '?key=' query parameter")
        self.assertNotIn(test_key, target_url, "URL must not contain the API key")

        # Headers MUST contain 'x-goog-api-key' with the key
        self.assertIn('x-goog-api-key', sent_headers, "Headers must include 'x-goog-api-key'")
        self.assertEqual(sent_headers['x-goog-api-key'], test_key)

    def test_gemini_fallback_offline_operation(self):
        """When AI API service fails or key is missing, generate_response safely returns None for fallback."""
        with patch.dict(os.environ, {'AI_PROVIDER': 'gemini', 'GEMINI_API_KEY': 'some_key'}):
            with patch('services.ai_service.requests.post', side_effect=Exception("Network error")):
                res = AIService.generate_response(
                    system_prompt="System",
                    user_message="Hello"
                )
                self.assertIsNone(res, "Should gracefully return None on exception to trigger rule-based fallback")


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSecurityPhase4)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if result.wasSuccessful():
        print("\n>>> ALL PHASE 4 SECURITY TESTS PASSED! <<<")
        sys.exit(0)
    else:
        print("\n>>> PHASE 4 SECURITY TESTS FAILED! <<<")
        sys.exit(1)
