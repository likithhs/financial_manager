"""
FinAI Phase 3 - Flask Backend Foundation Verification Test Suite
Tests all 7 required criteria from Section 19 of the Phase 3 Specification.
"""

import sys
from app import app
from database import get_db_connection


def run_phase3_tests():
    print("=" * 65)
    print("FinAI Phase 3 - Flask Backend Foundation Test Suite")
    print("=" * 65)

    results = {}
    client = app.test_client()

    # Test 1: Application starts without errors
    try:
        assert app is not None
        assert app.name == 'app'
        results["Test 1: Flask application initialization"] = ("PASS", "Flask app factory created app cleanly")
    except Exception as e:
        results["Test 1: Flask application initialization"] = ("FAIL", str(e))

    # Test 2: Open / (Home page loads 200 OK)
    try:
        res = client.get('/')
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        assert b"FinAI" in res.data, "Expected FinAI in page output"
        results["Test 2: Root route (/) loads home page"] = ("PASS", f"HTTP {res.status_code} OK (HTML returned)")
    except Exception as e:
        results["Test 2: Root route (/) loads home page"] = ("FAIL", str(e))

    # Test 3: Open /health (Health check returns status ok)
    try:
        res = client.get('/health')
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        json_data = res.get_json()
        assert json_data.get('status') == 'ok', f"Expected status ok, got {json_data}"
        assert json_data.get('database') == 'connected', "Database ping failed in health check"
        results["Test 3: Health check (/health) returns status ok"] = ("PASS", f"Status: {json_data['status']}, Database: {json_data['database']}")
    except Exception as e:
        results["Test 3: Health check (/health) returns status ok"] = ("FAIL", str(e))

    # Test 4: Verify Database Connection
    try:
        conn, db_type = get_db_connection()
        assert db_type == 'mysql', f"Expected MySQL, got {db_type}"
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        val = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        assert val == 1
        results["Test 4: Centralized MySQL database connection"] = ("PASS", "Connected to MySQL via get_db_connection()")
    except Exception as e:
        results["Test 4: Centralized MySQL database connection"] = ("FAIL", str(e))

    # Test 5: Verify all registered blueprints/routes
    try:
        registered_blueprints = set(app.blueprints.keys())
        expected_blueprints = {
            'main', 'auth', 'dashboard_bp', 'profile', 'income', 'expense',
            'goal', 'risk', 'market', 'assistant', 'investment', 'admin', 'api'
        }
        missing_bps = expected_blueprints - registered_blueprints
        assert not missing_bps, f"Missing blueprints: {missing_bps}"

        # Test API health
        api_res = client.get('/api/health')
        assert api_res.status_code == 200
        assert api_res.get_json()['status'] == 'ok'

        results["Test 5: Modular blueprints registration"] = ("PASS", f"Verified all {len(expected_blueprints)} required blueprints registered")
    except Exception as e:
        results["Test 5: Modular blueprints registration"] = ("FAIL", str(e))

    # Test 6: Verify unknown URL returns 404 properly (HTML and API)
    try:
        # Unknown HTML route
        res_404_html = client.get('/nonexistent-page-test-404')
        assert res_404_html.status_code == 404, f"Expected 404, got {res_404_html.status_code}"
        assert b"404" in res_404_html.data

        # Unknown API route
        res_404_api = client.get('/api/nonexistent-endpoint')
        assert res_404_api.status_code == 404
        assert res_404_api.get_json().get('error') == 'Not Found'

        results["Test 6: Centralized error handling for 404"] = ("PASS", "Both HTML view and JSON API handle 404 cleanly")
    except Exception as e:
        results["Test 6: Centralized error handling for 404"] = ("FAIL", str(e))

    # Test 7: Verify no syntax or import errors
    try:
        # Import all services and validators
        import services.validators
        import services.auth_helper
        import services.user_service
        import services.income_service
        import services.expense_service
        import services.goal_service
        import services.investment_service
        import services.financial_service
        import routes.error_handlers
        results["Test 7: Clean import and syntax validation"] = ("PASS", "All services and blueprints imported cleanly without errors")
    except Exception as e:
        results["Test 7: Clean import and syntax validation"] = ("FAIL", str(e))

    return results


if __name__ == '__main__':
    test_results = run_phase3_tests()
    print("\n" + "=" * 65)
    print("PHASE 3 TEST RESULTS SUMMARY:")
    print("=" * 65)
    all_passed = True
    for test_name, (status, detail) in test_results.items():
        print(f"[{status}] {test_name}: {detail}")
        if status != "PASS":
            all_passed = False

    print("=" * 65)
    if all_passed:
        print("ALL 7 PHASE 3 TESTS PASSED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("SOME TESTS FAILED.")
        sys.exit(1)
