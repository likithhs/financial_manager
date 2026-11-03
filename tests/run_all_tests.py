"""
Finora Master Test Runner
Executes all unit, integration, and security test suites and reports consolidated results.
"""

import unittest
import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.test_auth import AuthTestCase
from tests.test_database import DatabasePersistenceTestCase
from tests.test_proxy_and_security import ProxyAndSecurityTestCase


def run_test_suite():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(AuthTestCase))
    suite.addTests(loader.loadTestsFromTestCase(DatabasePersistenceTestCase))
    suite.addTests(loader.loadTestsFromTestCase(ProxyAndSecurityTestCase))

    print("\n" + "=" * 70)
    print("FINORA VERIFICATION SUITE - AUTHENTICATION, DATABASE & PROXY CHECKS")
    print("=" * 70 + "\n")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    print(f"TOTAL TESTS RUN : {result.testsRun}")
    print(f"SUCCESSES       : {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"FAILURES        : {len(result.failures)}")
    print(f"ERRORS          : {len(result.errors)}")
    print("=" * 70 + "\n")

    return len(result.failures) == 0 and len(result.errors) == 0


if __name__ == '__main__':
    success = run_test_suite()
    sys.exit(0 if success else 1)
