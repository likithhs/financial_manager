"""
Finora Test Suite - Proxy, Rate Limiting & Production Security Tests
Covers Werkzeug ProxyFix client IP resolution, brute-force rate-limiting defenses,
HTTP 429 error presentation, production SECRET_KEY enforcement, and secure admin provisioning.
"""

import os
import re
import tempfile
import unittest
from unittest.mock import patch

from config import Config, _get_secret_key
from app import create_app
import database
import bootstrap


class ProxyAndSecurityTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')

    def tearDown(self):
        try:
            os.close(self.db_fd)
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
        except Exception:
            pass

    def _get_csrf_token(self, client, url):
        resp = client.get(url)
        match = re.search(r'name="csrf_token" value="([^"]+)"', resp.get_data(as_text=True))
        return match.group(1) if match else None

    # -------------------------------------------------------------
    # 1. ProxyFix Client IP Resolution
    # -------------------------------------------------------------
    def test_proxy_fix_resolves_real_client_ip(self):
        """
        Verify that behind Render's reverse proxy (ProxyFix enabled):
        - X-Forwarded-For header correctly overrides request.remote_addr with the true client IP.
        - X-Forwarded-Proto correctly overrides request.scheme with https.
        """
        class ProxyAppConfig(Config):
            TESTING = True
            DB_ENGINE = 'sqlite'
            SQLITE_PATH = self.db_path
            PROXY_FIX_NUM_PROXIES = 1

        app = create_app(ProxyAppConfig)
        
        # Test custom route inspecting request.remote_addr and scheme
        @app.route('/test-ip-check')
        def test_ip_check():
            from flask import request
            return {
                'client_ip': request.remote_addr,
                'scheme': request.scheme
            }

        client = app.test_client()
        trusted_client_ip = '198.51.100.42'

        # Simulate Render forwarding request with X-Forwarded headers
        resp = client.get('/test-ip-check', headers={
            'X-Forwarded-For': trusted_client_ip,
            'X-Forwarded-Proto': 'https',
            'X-Forwarded-Host': 'finora.onrender.com'
        })

        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['client_ip'], trusted_client_ip)
        self.assertEqual(data['scheme'], 'https')

    # -------------------------------------------------------------
    # 2. Rate Limiting & HTTP 429 Presentation
    # -------------------------------------------------------------
    def test_login_rate_limiting_triggers_friendly_429(self):
        """
        Verify that exceeding the configured login rate limit:
        - Blocks excessive attempts.
        - Returns HTTP 429 status code.
        - Returns a user-friendly error page without crashing the server.
        """
        class RateLimitedConfig(Config):
            TESTING = True
            DB_ENGINE = 'sqlite'
            SQLITE_PATH = self.db_path
            RATELIMIT_ENABLED = True
            RATELIMIT_LOGIN = "3 per minute"  # Strict test limit
            WTF_CSRF_ENABLED = False          # Disabled to focus on rate limiter test

        app = create_app(RateLimitedConfig)
        client = app.test_client()

        with app.app_context():
            database.init_db(engine='sqlite')

        # Send 3 rapid POST attempts (should be accepted or rejected by auth, not rate limiter)
        for i in range(3):
            res = client.post('/login', data={'email': 'rate@finora.test', 'password': 'WrongPassword123!'})
            self.assertIn(res.status_code, (200, 302))

        # 4th request must exceed the rate limit (3 per minute)
        res_blocked = client.post('/login', data={'email': 'rate@finora.test', 'password': 'WrongPassword123!'})
        self.assertEqual(res_blocked.status_code, 429)
        html = res_blocked.get_data(as_text=True)
        self.assertIn("429", html)

    # -------------------------------------------------------------
    # 3. Production Security & Secret Key Enforcement
    # -------------------------------------------------------------
    def test_production_missing_secret_key_raises_runtime_error(self):
        """Verify that in production mode, missing SECRET_KEY strictly raises a descriptive RuntimeError."""
        with patch.dict(os.environ, {'FLASK_ENV': 'production', 'SECRET_KEY': ''}, clear=False):
            with self.assertRaises(RuntimeError) as ctx:
                _get_secret_key()
            self.assertIn("CRITICAL PRODUCTION CONFIGURATION ERROR", str(ctx.exception))

    def test_production_insecure_predictable_secret_key_rejected(self):
        """Verify that in production mode, known insecure default secrets are strictly rejected."""
        with patch.dict(os.environ, {'FLASK_ENV': 'production', 'SECRET_KEY': 'dev_academic_secret_key_financial_manager_2026'}, clear=False):
            with self.assertRaises(RuntimeError) as ctx:
                _get_secret_key()
            self.assertIn("CRITICAL PRODUCTION SECURITY CONFIGURATION ERROR", str(ctx.exception))

    # -------------------------------------------------------------
    # 4. Insecure Administrator Account Prevention in Production
    # -------------------------------------------------------------
    def test_production_skips_insecure_default_admin_creation(self):
        """
        Verify that in production mode (FLASK_ENV=production or RENDER=true):
        If DEFAULT_ADMIN_PASSWORD is not set or matches 'Admin@123456',
        it refuses to create an administrator with that known password.
        """
        class ProdConfig(Config):
            TESTING = True
            DB_ENGINE = 'sqlite'
            SQLITE_PATH = self.db_path

        app = create_app(ProdConfig)
        with app.app_context():
            database.init_db(engine='sqlite')

            with patch.dict(os.environ, {
                'FLASK_ENV': 'production',
                'DEFAULT_ADMIN_EMAIL': 'unsecured_admin@finora.test',
                'DEFAULT_ADMIN_PASSWORD': 'Admin@123456'  # Insecure default
            }):
                bootstrap.ensure_admin_account()

                # Verify user was NOT created
                admin_user = database.query_db("SELECT id FROM users WHERE email = %s", ('unsecured_admin@finora.test',), one=True)
                self.assertIsNone(admin_user, "Insecure admin account was created in production mode!")

    def test_production_creates_admin_when_secure_password_configured(self):
        """
        Verify that in production mode, when a strong password (>=12 chars) is provided via environment,
        the administrator account is successfully provisioned.
        """
        class ProdConfig(Config):
            TESTING = True
            DB_ENGINE = 'sqlite'
            SQLITE_PATH = self.db_path

        app = create_app(ProdConfig)
        with app.app_context():
            database.init_db(engine='sqlite')

            secure_pass = 'StrongProdAdminPassphrase2026!'
            with patch.dict(os.environ, {
                'FLASK_ENV': 'production',
                'DEFAULT_ADMIN_EMAIL': 'secure_admin@finora.test',
                'DEFAULT_ADMIN_PASSWORD': secure_pass
            }):
                bootstrap.ensure_admin_account()

                admin_user = database.query_db("SELECT * FROM users WHERE email = %s", ('secure_admin@finora.test',), one=True)
                self.assertIsNotNone(admin_user)
                self.assertEqual(admin_user['role'], 'admin')


if __name__ == '__main__':
    unittest.main()
