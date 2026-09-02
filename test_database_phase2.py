"""
FinAI Phase 2 - Database Architecture & Verification Test
Verifies all 10 Phase 2 requirements against MySQL.
"""

import sys
from decimal import Decimal
from datetime import date
from werkzeug.security import generate_password_hash
from database import get_db_connection, query_db, execute_db

def run_tests():
    print("=" * 60)
    print("FinAI Phase 2 - MySQL Database Verification Test")
    print("=" * 60)

    test_results = {}

    # 1. MySQL Connection Works
    try:
        conn, db_type = get_db_connection()
        assert db_type == 'mysql', f"Expected MySQL, got {db_type}"
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        test_results["1. MySQL connection works"] = ("PASS", f"Connected to MySQL version {version}")
    except Exception as e:
        test_results["1. MySQL connection works"] = ("FAIL", str(e))
        return test_results

    # 2. Database Exists
    try:
        current_db = query_db("SELECT DATABASE() as db", one=True)['db']
        assert current_db == 'financial_manager', f"Expected financial_manager, got {current_db}"
        test_results["2. Database exists"] = ("PASS", f"Active database: {current_db}")
    except Exception as e:
        test_results["2. Database exists"] = ("FAIL", str(e))

    # 3. Required Tables Exist
    required_tables = [
        'users',
        'financial_profiles',
        'income',
        'expense_categories',
        'expenses',
        'financial_goals',
        'goal_contributions',
        'risk_assessments',
        'investment_categories',
        'recommendations',
        'chat_history',
        'watchlist',
        'portfolio',
        'market_cache'
    ]
    try:
        raw_tables = query_db("SHOW TABLES")
        existing_tables = [list(r.values())[0] for r in raw_tables]
        missing = [t for t in required_tables if t not in existing_tables]
        assert not missing, f"Missing required tables: {missing}"
        test_results["3. Required tables exist"] = ("PASS", f"All {len(required_tables)} Phase 2 tables verified")
    except Exception as e:
        test_results["3. Required tables exist"] = ("FAIL", str(e))

    # 4. Tables have the expected relationships (Foreign Keys)
    try:
        fks = query_db("""
            SELECT TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = 'financial_manager' AND REFERENCED_TABLE_NAME IS NOT NULL
        """)
        fk_map = {(r['TABLE_NAME'], r['REFERENCED_TABLE_NAME']) for r in fks}
        assert ('financial_profiles', 'users') in fk_map
        assert ('income', 'users') in fk_map
        assert ('expenses', 'users') in fk_map
        assert ('financial_goals', 'users') in fk_map
        assert ('goal_contributions', 'financial_goals') in fk_map
        assert ('goal_contributions', 'users') in fk_map
        assert ('recommendations', 'investment_categories') in fk_map
        test_results["4. Tables have expected relationships"] = ("PASS", f"Verified {len(fks)} active Foreign Key constraints")
    except Exception as e:
        test_results["4. Tables have expected relationships"] = ("FAIL", str(e))

    # Create temporary test user to verify transactions (cleanly deleted afterwards)
    test_email = "test_phase2_auto@finai.internal"
    test_user_id = None
    try:
        # Cleanup any previous dangling test user
        execute_db("DELETE FROM users WHERE email = %s", (test_email,))

        # 5. Test user can be inserted safely
        pwd_hash = generate_password_hash("TestSecure123!")
        test_user_id = execute_db("""
            INSERT INTO users (name, email, password, password_hash, role)
            VALUES (%s, %s, %s, %s, 'user')
        """, ("Phase2 Test User", test_email, pwd_hash, pwd_hash))
        assert test_user_id > 0, "Failed to insert test user"
        test_results["5. Test user insertion"] = ("PASS", f"Inserted user ID: {test_user_id} with salted hash")

        # 6. Income can be inserted
        inc1_id = execute_db("""
            INSERT INTO income (user_id, amount, source, date, description)
            VALUES (%s, %s, %s, %s, %s)
        """, (test_user_id, Decimal("50000.00"), "Monthly Salary", date.today(), "Base Salary"))
        assert inc1_id > 0
        test_results["6. Income insertion"] = ("PASS", f"Inserted income record ID {inc1_id} for INR 50,000.00")

        # 7. Multiple income records are preserved (Transaction-based)
        inc2_id = execute_db("""
            INSERT INTO income (user_id, amount, source, date, description)
            VALUES (%s, %s, %s, %s, %s)
        """, (test_user_id, Decimal("5000.00"), "Freelance Project", date.today(), "Bonus stipend"))
        assert inc2_id > 0

        # Query total
        user_incomes = query_db("SELECT amount FROM income WHERE user_id = %s", (test_user_id,))
        total_income = sum(Decimal(str(r['amount'])) for r in user_incomes)
        assert len(user_incomes) == 2, f"Expected 2 records, found {len(user_incomes)}"
        assert total_income == Decimal("55000.00"), f"Expected 55000.00, got {total_income}"
        test_results["7. Multiple income records preserved"] = ("PASS", f"Preserved 2 distinct transactions totaling INR {total_income:,.2f}")

        # 8. Expense can be inserted with category
        cat = query_db("SELECT id FROM expense_categories WHERE name = 'Food'", one=True)
        cat_id = cat['id'] if cat else None
        exp_id = execute_db("""
            INSERT INTO expenses (user_id, category_id, title, category, amount, date, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (test_user_id, cat_id, "Grocery shopping", "Food", Decimal("2500.00"), date.today(), "Supermarket"))
        assert exp_id > 0
        test_results["8. Expense insertion"] = ("PASS", f"Inserted expense ID {exp_id} for INR 2,500.00 linked to category {cat_id}")

        # 9. Goal can be created
        goal_id = execute_db("""
            INSERT INTO financial_goals (user_id, name, goal_name, target_amount, current_amount, current_savings, target_date, priority)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (test_user_id, "Emergency Fund", "Emergency Fund", Decimal("100000.00"), Decimal("20000.00"), Decimal("20000.00"), date(2027, 12, 31), "High"))
        assert goal_id > 0
        test_results["9. Goal creation"] = ("PASS", f"Created goal ID {goal_id} with INR 20,000.00 initial savings")

        # 10. Goal contribution can be accumulated correctly
        # User adds INR 5,000 contribution
        contribution_amount = Decimal("5000.00")
        contrib_id = execute_db("""
            INSERT INTO goal_contributions (goal_id, user_id, amount, contribution_date, description)
            VALUES (%s, %s, %s, %s, %s)
        """, (goal_id, test_user_id, contribution_amount, date.today(), "Monthly deposit"))
        assert contrib_id > 0

        # Update accumulated current_amount in goal
        execute_db("""
            UPDATE financial_goals
            SET current_amount = current_amount + %s,
                current_savings = current_savings + %s
            WHERE id = %s AND user_id = %s
        """, (contribution_amount, contribution_amount, goal_id, test_user_id))

        updated_goal = query_db("SELECT current_amount, current_savings FROM financial_goals WHERE id = %s", (goal_id,), one=True)
        assert Decimal(str(updated_goal['current_amount'])) == Decimal("25000.00")
        assert Decimal(str(updated_goal['current_savings'])) == Decimal("25000.00")
        test_results["10. Goal contribution accumulation"] = ("PASS", f"Accumulated INR 20,000 + INR 5,000 = INR 25,000.00 with audit contribution ID {contrib_id}")

    finally:
        # Clean up test data without leaving garbage in database
        if test_user_id:
            execute_db("DELETE FROM users WHERE id = %s", (test_user_id,))
            print(f"[Cleanup] Deleted temporary test user {test_user_id} and all cascading records.")

    return test_results

if __name__ == '__main__':
    results = run_tests()
    print("\n" + "=" * 60)
    print("VERIFICATION RESULTS SUMMARY:")
    print("=" * 60)
    all_passed = True
    for test_name, (status, detail) in results.items():
        print(f"[{status}] {test_name}: {detail}")
        if status != "PASS":
            all_passed = False

    print("=" * 60)
    if all_passed:
        print("ALL 10 DATABASE REQUIREMENTS PASSED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("SOME TESTS FAILED.")
        sys.exit(1)
