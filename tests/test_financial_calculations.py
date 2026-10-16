import os
import sys

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from test_financial_calculations import TestFinancialCalculations, run_tests

if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
