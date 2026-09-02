import os
import sqlite3
from config import Config
from werkzeug.security import generate_password_hash

# Try importing mysql.connector
try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    MySQLError = Exception

SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'financial_manager.db')

def get_db_connection():
    """
    Establish database connection.
    Attempts MySQL first. If MySQL fails (e.g. server not running),
    seamlessly falls back to a local SQLite database for zero-config demo.
    """
    if MYSQL_AVAILABLE:
        try:
            conn = mysql.connector.connect(
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                port=Config.DB_PORT,
                autocommit=True,
                use_pure=True
            )
            return conn, 'mysql'
        except MySQLError as err:
            # Fall through to SQLite fallback
            pass

    # SQLite fallback
    os.makedirs(os.path.dirname(SQLITE_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn, 'sqlite'

def query_db(query, args=(), one=False):
    """
    Execute a SELECT query and return list of dictionaries or single dictionary.
    Handles parameter syntax translation (%s for MySQL, ? for SQLite).
    """
    conn, db_type = get_db_connection()
    try:
        if db_type == 'mysql':
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, args)
            rv = cursor.fetchall()
            cursor.close()
            conn.close()
            return (rv[0] if rv else None) if one else rv
        else:
            # SQLite uses '?' instead of '%s'
            sqlite_query = query.replace('%s', '?')
            cursor = conn.cursor()
            cursor.execute(sqlite_query, args)
            rv = cursor.fetchall()
            # Convert sqlite3.Row to dict
            dict_rv = [dict(row) for row in rv]
            cursor.close()
            conn.close()
            return (dict_rv[0] if dict_rv else None) if one else dict_rv
    except Exception as e:
        if 'conn' in locals() and conn:
            conn.close()
        print(f"Database Query Error: {e} | Query: {query}")
        return None if one else []

def execute_db(query, args=()):
    """
    Execute an INSERT, UPDATE, or DELETE query.
    Returns the lastrowid or affected rows count.
    """
    conn, db_type = get_db_connection()
    try:
        if db_type == 'mysql':
            cursor = conn.cursor()
            cursor.execute(query, args)
            last_id = cursor.lastrowid
            affected = cursor.rowcount
            conn.commit()
            cursor.close()
            conn.close()
            return last_id if last_id else affected
        else:
            sqlite_query = query.replace('%s', '?')
            cursor = conn.cursor()
            cursor.execute(sqlite_query, args)
            conn.commit()
            last_id = cursor.lastrowid
            affected = cursor.rowcount
            cursor.close()
            conn.close()
            return last_id if last_id else affected
    except Exception as e:
        if 'conn' in locals() and conn:
            conn.close()
        print(f"Database Execute Error: {e} | Query: {query}")
        return 0

def init_db():
    """
    Initializes the database schema and default seed data.
    Automatically runs on application startup.
    """
    conn, db_type = get_db_connection()
    try:
        if db_type == 'mysql':
            cursor = conn.cursor()
            schema_path = os.path.join(os.path.dirname(__file__), 'database', 'schema.sql')
            if os.path.exists(schema_path):
                with open(schema_path, 'r', encoding='utf-8') as f:
                    sql_content = f.read()
                statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
                for stmt in statements:
                    clean_stmt = '\n'.join([line for line in stmt.split('\n') if not line.strip().startswith('--')]).strip()
                    if clean_stmt:
                        try:
                            cursor.execute(clean_stmt)
                        except Exception as err:
                            # Table or column already exists / benign warning
                            pass
                conn.commit()
            cursor.close()
            conn.close()
        else:
            # Setup SQLite tables if they do not exist
            cursor = conn.cursor()
            cursor.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                age INTEGER DEFAULT 25,
                occupation TEXT DEFAULT 'Student / Professional',
                financial_exp TEXT DEFAULT 'Beginner',
                investment_exp TEXT DEFAULT 'None',
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS incomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                source TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                month_year TEXT NOT NULL,
                total_budget REAL NOT NULL,
                category_budgets TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(user_id, month_year)
            );

            CREATE TABLE IF NOT EXISTS financial_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                target_amount REAL NOT NULL,
                current_amount REAL DEFAULT 0.00,
                target_date TEXT NOT NULL,
                priority TEXT DEFAULT 'Medium',
                description TEXT,
                status TEXT DEFAULT 'In Progress',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS risk_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                score INTEGER NOT NULL,
                risk_level TEXT NOT NULL,
                answers_json TEXT,
                explanation TEXT,
                evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS financial_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                total_income REAL DEFAULT 0.00,
                total_expenses REAL DEFAULT 0.00,
                savings REAL DEFAULT 0.00,
                savings_rate REAL DEFAULT 0.00,
                expense_ratio REAL DEFAULT 0.00,
                emergency_fund_ratio REAL DEFAULT 0.00,
                health_score INTEGER DEFAULT 50,
                health_status TEXT DEFAULT 'Moderate',
                explanation TEXT,
                evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS investment_readiness (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                is_ready INTEGER DEFAULT 0,
                readiness_score INTEGER DEFAULT 0,
                reasons_json TEXT,
                suggestions_json TEXT,
                evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS investment_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                primary_category TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                recommended_allocation_json TEXT,
                rationale TEXT,
                advantages TEXT,
                risks TEXT,
                factors_considered TEXT,
                evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS stocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL UNIQUE,
                company_name TEXT NOT NULL,
                sector TEXT NOT NULL,
                market TEXT DEFAULT 'NSE/BSE/US',
                current_price REAL NOT NULL,
                previous_close REAL NOT NULL,
                pe_ratio REAL DEFAULT 0.00,
                market_cap TEXT DEFAULT 'Large Cap',
                high_52w REAL DEFAULT 0.00,
                low_52w REAL DEFAULT 0.00,
                volatility TEXT DEFAULT 'Moderate',
                risk_rating TEXT DEFAULT 'Moderate',
                description TEXT
            );

            CREATE TABLE IF NOT EXISTS stock_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                company_name TEXT NOT NULL,
                suitability_status TEXT NOT NULL,
                suitability_score INTEGER DEFAULT 50,
                analysis_reasons TEXT,
                user_risk_level TEXT,
                stock_risk_level TEXT,
                evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS stock_watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                company_name TEXT NOT NULL,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(user_id, symbol)
            );

            CREATE TABLE IF NOT EXISTS portfolios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT DEFAULT 'My Investment Portfolio',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS portfolio_holdings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                portfolio_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                company_name TEXT NOT NULL,
                asset_type TEXT DEFAULT 'Equity Stock',
                quantity INTEGER NOT NULL,
                buy_price REAL NOT NULL,
                buy_date TEXT NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS ai_conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                user_message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                context_used_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            ''')
            
            # Check if admin user exists
            cursor.execute("SELECT id FROM users WHERE email = 'admin@financialmanager.com'")
            if not cursor.fetchone():
                admin_hash = generate_password_hash('admin123')
                cursor.execute("""
                    INSERT INTO users (name, email, password_hash, age, occupation, financial_exp, investment_exp, role)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, ('System Administrator', 'admin@financialmanager.com', admin_hash, 35, 'Financial Admin', 'Expert', 'Advanced', 'admin'))

            # Check if default stocks exist
            cursor.execute("SELECT COUNT(*) as count FROM stocks")
            if cursor.fetchone()['count'] == 0:
                stocks_data = [
                    ('TCS', 'Tata Consultancy Services', 'Information Technology', 'NSE', 3850.00, 3810.00, 28.5, 'Large Cap (₹14 Lakh Cr)', 4250.00, 3310.00, 'Low', 'Low', 'Global leader in IT services, digital and business solutions with consistent dividend track record.'),
                    ('INFY', 'Infosys Limited', 'Information Technology', 'NSE', 1540.00, 1560.00, 24.2, 'Large Cap (₹6.4 Lakh Cr)', 1760.00, 1350.00, 'Moderate', 'Moderate', 'Leading provider of next-generation digital services and consulting across 50+ countries.'),
                    ('RELIANCE', 'Reliance Industries Ltd', 'Energy & Telecom', 'NSE', 2920.00, 2895.00, 26.8, 'Large Cap (₹19 Lakh Cr)', 3050.00, 2220.00, 'Moderate', 'Moderate', 'India’s largest conglomerate spanning petrochemicals, refining, retail, and digital telecom services (Jio).'),
                    ('HDFCBANK', 'HDFC Bank Ltd', 'Banking & Finance', 'NSE', 1620.00, 1605.00, 18.9, 'Large Cap (₹12 Lakh Cr)', 1750.00, 1360.00, 'Low', 'Low', 'India’s largest private sector bank known for robust asset quality and extensive branch network.'),
                    ('ITC', 'ITC Limited', 'FMCG & Consumer Goods', 'NSE', 430.00, 428.00, 25.1, 'Large Cap (₹5.3 Lakh Cr)', 499.00, 399.00, 'Low', 'Low', 'Diversified conglomerate with dominant presence in FMCG, hotels, paperboards, packaging, and agri-business.'),
                    ('TATAMOTORS', 'Tata Motors Ltd', 'Automotive', 'NSE', 980.00, 960.00, 16.4, 'Large Cap (₹3.2 Lakh Cr)', 1179.00, 590.00, 'High', 'High', 'Leading global automobile manufacturer of cars, utility vehicles, trucks, buses and Jaguar Land Rover.'),
                    ('ZOMATO', 'Zomato Limited', 'Internet & Food Delivery', 'NSE', 240.00, 235.00, 78.0, 'Large Cap (₹2.1 Lakh Cr)', 298.00, 88.00, 'High', 'High', 'Fast-growing internet consumer platform for food delivery, quick commerce (Blinkit) and dining out.'),
                    ('AAPL', 'Apple Inc.', 'Technology & Consumer Electronics', 'NASDAQ', 225.00, 222.50, 33.2, 'Mega Cap ($3.4 Trillion)', 237.00, 164.00, 'Moderate', 'Moderate', 'Global designer and manufacturer of smartphones, personal computers, tablets, wearables, and services.'),
                    ('MSFT', 'Microsoft Corporation', 'Software & Cloud Computing', 'NASDAQ', 430.00, 425.00, 35.8, 'Mega Cap ($3.2 Trillion)', 468.00, 309.00, 'Low', 'Low', 'World leader in software products, Azure cloud infrastructure, AI solutions, and enterprise productivity.'),
                    ('NVDA', 'NVIDIA Corporation', 'Semiconductors & AI', 'NASDAQ', 125.00, 118.00, 52.4, 'Mega Cap ($3.0 Trillion)', 140.00, 40.00, 'High', 'High', 'Pioneer of GPU-accelerated computing and undisputed market leader in generative AI chips and data center acceleration.')
                ]
                cursor.executemany("""
                    INSERT INTO stocks (symbol, company_name, sector, market, current_price, previous_close, pe_ratio, market_cap, high_52w, low_52w, volatility, risk_rating, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, stocks_data)
            
            conn.commit()
            cursor.close()
            conn.close()
    except Exception as e:
        print(f"init_db error: {e}")
