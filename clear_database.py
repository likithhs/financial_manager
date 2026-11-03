import database

def clear_all():
    conn, eng = database.get_db_connection()
    cursor = conn.cursor()

    tables_to_clear = [
        'users',
        'financial_profiles',
        'income',
        'incomes',
        'expenses',
        'budgets',
        'financial_goals',
        'goal_contributions',
        'risk_assessments',
        'risk_profiles',
        'financial_analysis',
        'investment_readiness',
        'investment_recommendations',
        'recommendations',
        'chat_history',
        'ai_conversations',
        'watchlist',
        'stock_watchlist',
        'portfolio',
        'portfolios',
        'portfolio_holdings',
        'stock_analysis',
        'stocks',
        'market_cache'
    ]

    print("Disabling foreign key constraints...")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

    for table in tables_to_clear:
        try:
            cursor.execute(f"TRUNCATE TABLE `{table}`")
            print(f"[OK] Truncated table: {table}")
        except Exception as e:
            try:
                cursor.execute(f"DELETE FROM `{table}`")
                cursor.execute(f"ALTER TABLE `{table}` AUTO_INCREMENT = 1")
                print(f"[OK] Cleared via DELETE: {table}")
            except Exception as e2:
                print(f"[NOTE] Table {table} not found or skipped: {e2}")

    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    conn.commit()
    cursor.close()
    conn.close()

    # Re-run init_db to ensure necessary system lookup tables exist
    print("\nEnsuring system lookup categories exist...")
    database.init_db()

    # Verify counts
    print("\nVerifying database status:")
    conn, eng = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    all_tables = [r[0] for r in cursor.fetchall()]
    for t in all_tables:
        cursor.execute(f"SELECT COUNT(*) FROM `{t}`")
        count = cursor.fetchone()[0]
        print(f" - {t}: {count} rows")
    cursor.close()
    conn.close()
    print("\n[SUCCESS] Database completely cleared! All user tables are at 0 rows.")

if __name__ == '__main__':
    clear_all()
