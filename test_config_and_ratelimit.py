"""
Finora - Configuration, Rate Limiting, and Admin Initialization Tests
Verifies SECRET_KEY validation in prod vs dev, dynamic RATELIMIT_DEFAULT enforcement,
and flask init-admin CLI command.
"""

import os
import unittest
from flask import Flask
from click.testing import CliRunner


class TestConfigAndRateLimit(unittest.TestCase):
    def test_01_secret_key_development_generates_ephemeral_key(self):
        """In development mode, missing SECRET_KEY generates an ephemeral key without crashing."""
        from config import _get_secret_key

        old_env = os.environ.copy()
        try:
            os.environ['FLASK_ENV'] = 'development'
            os.environ.pop('SECRET_KEY', None)
            os.environ.pop('TESTING', None)

            key = _get_secret_key()
            self.assertIsNotNone(key)
            self.assertGreaterEqual(len(key), 32)
        finally:
            os.environ.clear()
            os.environ.update(old_env)

    def test_02_secret_key_production_fails_when_missing(self):
        """In production mode, missing SECRET_KEY raises a critical RuntimeError."""
        from config import _get_secret_key

        old_env = os.environ.copy()
        try:
            os.environ['FLASK_ENV'] = 'production'
            os.environ.pop('SECRET_KEY', None)
            os.environ.pop('TESTING', None)

            with self.assertRaises(RuntimeError) as ctx:
                _get_secret_key()
            self.assertIn("CRITICAL PRODUCTION CONFIGURATION ERROR", str(ctx.exception))
        finally:
            os.environ.clear()
            os.environ.update(old_env)

    def test_03_secret_key_production_rejects_predictable_keys(self):
        """In production mode, predictable or placeholder keys are rejected."""
        from config import _get_secret_key

        predictable_keys = [
            'dev_academic_secret_key_financial_manager_2026',
            'your_generated_cryptographically_secure_32_byte_secret_key_here',
            'generate_with_python_secrets_token_hex_32',
            'changeme',
            'short',
        ]

        old_env = os.environ.copy()
        try:
            os.environ['FLASK_ENV'] = 'production'
            os.environ.pop('TESTING', None)

            for bad_key in predictable_keys:
                os.environ['SECRET_KEY'] = bad_key
                with self.assertRaises(RuntimeError) as ctx:
                    _get_secret_key()
                self.assertIn("CRITICAL PRODUCTION SECURITY CONFIGURATION ERROR", str(ctx.exception))
        finally:
            os.environ.clear()
            os.environ.update(old_env)

    def test_04_rate_limit_default_from_config_is_respected(self):
        """Verify that RATELIMIT_DEFAULT from environment/config is enforced on routes."""
        from flask_limiter import Limiter
        from flask_limiter.util import get_remote_address

        test_app = Flask("rate_limit_test")
        test_app.config['TESTING'] = True
        test_app.config['RATELIMIT_DEFAULT'] = '3 per minute'
        test_app.config['RATELIMIT_STORAGE_URI'] = 'memory://'
        test_app.config['RATELIMIT_STRATEGY'] = 'fixed-window'

        lim = Limiter(key_func=get_remote_address)
        lim.init_app(test_app)

        @test_app.route('/browse')
        def browse():
            return "ok", 200

        client = test_app.test_client()

        # Requests 1, 2, 3 should succeed (normal page navigation)
        self.assertEqual(client.get('/browse').status_code, 200)
        self.assertEqual(client.get('/browse').status_code, 200)
        self.assertEqual(client.get('/browse').status_code, 200)

        # 4th request must breach the configured limit (429 Too Many Requests)
        self.assertEqual(client.get('/browse').status_code, 429)

    def test_05_flask_init_admin_cli_command(self):
        """Verify flask init-admin CLI command creates administrator account."""
        from app import app

        cmd = app.cli.commands['init-admin']
        runner = CliRunner()
        result = runner.invoke(cmd, [
            '--email', 'cli_admin@finora.test',
            '--password', 'VeryStrongAdminPass2026!',
            '--name', 'CLI Master Admin'
        ])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("SUCCESS:", result.output)
        self.assertIn("cli_admin@finora.test", result.output)


if __name__ == '__main__':
    unittest.main()
