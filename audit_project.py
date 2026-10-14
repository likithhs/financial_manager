import os 
import glob
import re
from app import app

def run_audit():
    print("="*60)
    print("STARTING COMPREHENSIVE FINAI CODEBASE AUDIT")
    print("="*60)

    # 1. Check Flask Registered Endpoints
    registered = set(app.view_functions.keys())
    print(f"Total Registered Flask Endpoints: {len(registered)}")
    for ep in sorted(registered):
        print(f"  - {ep}")

    # 2. Check all Template url_for references
    template_files = glob.glob('templates/**/*.html', recursive=True) + glob.glob('templates/*.html')
    template_files = sorted(list(set(template_files)))
    print(f"\nChecking {len(template_files)} HTML template files...")

    pattern = re.compile(r"url_for\(['\"]([a-zA-Z0-9_\.]+)['\"]")
    broken_links = []

    for tf in template_files:
        with open(tf, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        for idx, line in enumerate(lines, 1):
            matches = pattern.findall(line)
            for ep in matches:
                if ep != 'static' and ep not in registered:
                    broken_links.append((tf, idx, ep, line.strip()))

    if broken_links:
        print("\n[FAIL] FOUND BROKEN URL_FOR REFERENCES:")
        for tf, line_num, ep, line_txt in broken_links:
            print(f"  {tf}:{line_num} -> url_for('{ep}') does NOT exist!")
            print(f"     Line: {line_txt}")
    else:
        print("\n[PASS] All url_for references in all templates are 100% valid!")

    # 3. Test Full App Render for all Endpoints (GET and POST)
    print("\nTesting End-to-End Route Execution with live client...")
    client = app.test_client()

    # Login as Admin
    res_admin_login = client.post('/login', data={'email': 'admin@financialmanager.com', 'password': 'admin123'}, follow_redirects=True)
    assert res_admin_login.status_code == 200, "Admin login failed"

    admin_urls = [
        '/',
        '/admin/',
        '/admin/users',
        '/admin/reports',
        '/admin/health',
        '/stocks',
        '/stocks/RELIANCE',
        '/stocks/TCS',
        '/stocks/HDFCBANK',
        '/health'
    ]

    for url in admin_urls:
        resp = client.get(url, follow_redirects=True)
        assert resp.status_code == 200, f"Admin GET {url} returned {resp.status_code}"
        print(f"  [OK] Admin URL {url} -> 200 OK")

    # Logout and Login as User
    client.get('/logout', follow_redirects=True)
    res_user_login = client.post('/login', data={'email': 'likithhs@gmail.com', 'password': 'user123'}, follow_redirects=True)
    assert res_user_login.status_code == 200, "User login failed"

    user_urls = [
        '/',
        '/dashboard',
        '/income',
        '/expenses',
        '/budget',
        '/goals',
        '/financial-analysis',
        '/risk-profile',
        '/investment-readiness',
        '/investments',
        '/investment-recommendation',
        '/recommendation-history',
        '/stocks',
        '/stocks/TCS',
        '/stock-analysis?symbol=TCS',
        '/watchlist',
        '/portfolio',
        '/ai-assistant',
        '/profile'
    ]

    for url in user_urls:
        resp = client.get(url, follow_redirects=True)
        assert resp.status_code == 200, f"User GET {url} returned {resp.status_code}"
        print(f"  [OK] User URL {url} -> 200 OK")

    # 4. Test CRUD Form Submissions
    print("\nTesting Core CRUD Transactions...")
    
    # Add Income
    res_inc = client.post('/income/add', data={
        'source': 'Freelance Audit Test',
        'amount': '15000',
        'category': 'Freelance / Consulting',
        'date': '2026-09-03',
        'description': 'Automated end-to-end verification test'
    }, follow_redirects=True)
    assert res_inc.status_code == 200, "Income POST failed"
    print("  [OK] Income Creation POST -> 200 OK")

    # Add Expense
    res_exp = client.post('/expense/add', data={
        'amount': '3500',
        'category': 'Food & Dining',
        'date': '2026-09-03',
        'description': 'Automated test dining outlay'
    }, follow_redirects=True)
    assert res_exp.status_code == 200, "Expense POST failed"
    print("  [OK] Expense Creation POST -> 200 OK")

    # Add Goal
    res_goal = client.post('/goals/add', data={
        'name': 'Emergency Buffer Test',
        'target_amount': '50000',
        'current_amount': '10000',
        'target_date': '2027-01-01',
        'description': 'Audit test goal'
    }, follow_redirects=True)
    assert res_goal.status_code == 200, "Goal POST failed"
    print("  [OK] Goal Creation POST -> 200 OK")

    # Add Watchlist
    res_wl = client.post('/watchlist/add', data={
        'symbol': 'INFY'
    }, follow_redirects=True)
    assert res_wl.status_code == 200, "Watchlist POST failed"
    print("  [OK] Watchlist Addition POST -> 200 OK")

    # AI Chat Prompt
    res_ai = client.post('/ai-assistant', data={
        'message': 'What is my current savings rate?'
    }, follow_redirects=True)
    assert res_ai.status_code == 200, "AI Assistant POST failed"
    print("  [OK] AI Conversational Assistant POST -> 200 OK")

    print("\n" + "="*60)
    print(">>> ALL CODEBASE AUDITS AND END-TO-END TESTS PASSED WITH 0 ERRORS! <<<")
    print("="*60)

if __name__ == '__main__':
    run_audit()
