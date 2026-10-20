"""
Finora Database Viewer CLI Helper
Usage:
    python show_db.py               -> Shows summary of all 26 tables and row counts
    python show_db.py users         -> Shows rows from the 'users' table
    python show_db.py <table_name>  -> Shows rows from any table
"""
import sys
from database import query_db

def main():
    if len(sys.argv) > 1:
        table = sys.argv[1].strip()
        print(f"\n==================== TABLE: {table.upper()} ====================")
        try:
            rows = query_db(f"SELECT * FROM `{table}` LIMIT 50")
            if not rows:
                print(f"Table '{table}' is currently empty (0 rows).")
            else:
                for idx, r in enumerate(rows, 1):
                    # Hide password hashes from console printout for clean viewing
                    clean_row = {k: ('[HASH PROTECTED]' if 'password' in k.lower() else v) for k, v in r.items()}
                    print(f"[{idx}] {clean_row}")
                print(f"\nTotal shown: {len(rows)} row(s)")
        except Exception as e:
            print(f"Error querying table '{table}': {e}")
        print("=" * 60)
        return

    print("\n================== FINANCIAL_MANAGER DATABASE SUMMARY ==================")
    try:
        tables = query_db("SHOW TABLES")
        for t in tables:
            t_name = list(t.values())[0]
            try:
                count = query_db(f"SELECT COUNT(*) as c FROM `{t_name}`", one=True)['c']
                print(f"  • {t_name:28} -> {count} row(s)")
            except Exception:
                print(f"  • {t_name:28}")
        print("\nTip: Run 'python show_db.py <table_name>' (e.g. python show_db.py users) to inspect records.")
        print("=" * 60 + "\n")
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == '__main__':
    main()
