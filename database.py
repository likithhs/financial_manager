import os
import sqlite3
import logging
from contextlib import contextmanager
from config import Config
from werkzeug.security import generate_password_hash

logger = logging.getLogger(__name__)

# Try importing mysql.connector
try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    MySQLError = Exception

SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'financial_manager.db')


# =========================================================================
# APPLICATION DATABASE EXCEPTIONS
# =========================================================================

class DatabaseError(Exception):
    """Base exception for all database-related failures."""
    pass


class DatabaseConnectionError(DatabaseError):
    """Raised when a connection to the configured database cannot be established."""
    pass


class DatabaseQueryError(DatabaseError):
    """Raised when a database query or command fails to execute."""
    pass


class DatabaseTransactionError(DatabaseError):
    """Raised when an atomic transaction fails and is rolled back."""
    pass


# =========================================================================
# CONNECTION MANAGEMENT
# =========================================================================

def get_db_connection(engine=None):
    """
    Establish database connection based on explicit configuration.
    If engine is not specified, uses Config.DB_ENGINE ('mysql' by default).
    Does NOT silently switch writes between databases upon connection failure.
    """
    target_engine = (engine or getattr(Config, 'DB_ENGINE', 'mysql') or 'mysql').strip().lower()

    if target_engine == 'sqlite':
        sqlite_path = getattr(Config, 'SQLITE_PATH', SQLITE_DB_PATH)
        dir_name = os.path.dirname(sqlite_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        conn = sqlite3.connect(sqlite_path)
        conn.row_factory = sqlite3.Row
        # Enforce foreign key constraints in SQLite
        conn.execute("PRAGMA foreign_keys = ON")
        return conn, 'sqlite'

    elif target_engine == 'mysql':
        if not MYSQL_AVAILABLE:
            raise DatabaseConnectionError("MySQL driver (mysql-connector-python) is not installed in the Python environment.")
        try:
            conn = mysql.connector.connect(
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                port=Config.DB_PORT,
                autocommit=True,
                use_pure=True,
                connection_timeout=3
            )
            return conn, 'mysql'
        except Exception as err:
            logger.error(f"MySQL connection failed to {Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}: {err}")
            raise DatabaseConnectionError(f"Failed to connect to MySQL database: {err}") from err
    else:
        raise DatabaseConnectionError(f"Unsupported database engine '{target_engine}'. Expected 'mysql' or 'sqlite'.")


# =========================================================================
# QUERY AND EXECUTE HELPERS
# =========================================================================

def query_db(query, args=(), one=False, conn=None):
    """
    Execute a SELECT query and return list of dictionaries or single dictionary.
    Handles parameter syntax translation (%s for MySQL, ? for SQLite).
    Guarantees cursor and connection cleanup via try/finally.
    Raises DatabaseQueryError on query execution failure to distinguish failures from empty results.
    """
    external_conn = conn is not None
    active_conn = conn
    cursor = None

    try:
        if active_conn is None:
            active_conn, db_type = get_db_connection()
        else:
            db_type = 'sqlite' if isinstance(active_conn, sqlite3.Connection) else 'mysql'

        if db_type == 'mysql':
            cursor = active_conn.cursor(dictionary=True)
            cursor.execute(query, args)
            rv = cursor.fetchall()
            return (rv[0] if rv else None) if one else rv
        else:
            sqlite_query = query.replace('%s', '?')
            cursor = active_conn.cursor()
            cursor.execute(sqlite_query, args)
            rv = cursor.fetchall()
            dict_rv = [dict(row) for row in rv]
            return (dict_rv[0] if dict_rv else None) if one else dict_rv

    except DatabaseError:
        raise
    except Exception as e:
        logger.error(f"Database Query Error: {e} | Query: {query}")
        raise DatabaseQueryError(f"Database query failed: {e}") from e
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if not external_conn and active_conn:
            try:
                active_conn.close()
            except Exception:
                pass


def execute_db(query, args=(), conn=None):
    """
    Execute an INSERT, UPDATE, or DELETE query.
    Returns the lastrowid or affected rows count.
    Guarantees cursor and connection cleanup via try/finally.
    Raises DatabaseQueryError on execution failure to distinguish failures from zero affected rows.
    """
    external_conn = conn is not None
    active_conn = conn
    cursor = None

    try:
        if active_conn is None:
            active_conn, db_type = get_db_connection()
        else:
            db_type = 'sqlite' if isinstance(active_conn, sqlite3.Connection) else 'mysql'

        if db_type == 'mysql':
            cursor = active_conn.cursor()
            cursor.execute(query, args)
            last_id = cursor.lastrowid
            affected = cursor.rowcount
            if hasattr(active_conn, 'commit') and not getattr(active_conn, 'in_transaction', False):
                active_conn.commit()
            return last_id if last_id else affected
        else:
            sqlite_query = query.replace('%s', '?')
            cursor = active_conn.cursor()
            cursor.execute(sqlite_query, args)
            last_id = cursor.lastrowid
            affected = cursor.rowcount
            if not getattr(active_conn, 'in_transaction', False):
                active_conn.commit()
            return last_id if last_id else affected

    except DatabaseError:
        raise
    except Exception as e:
        logger.error(f"Database Execute Error: {e} | Query: {query}")
        raise DatabaseQueryError(f"Database execution failed: {e}") from e
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if not external_conn and active_conn:
            try:
                active_conn.close()
            except Exception:
                pass


# =========================================================================
# ATOMIC TRANSACTION CONTEXT MANAGER
# =========================================================================

class TransactionContext:
    """Wrapper around an active database transaction connection and cursor."""
    def __init__(self, conn, db_type):
        self.conn = conn
        self.db_type = db_type
        if db_type == 'mysql':
            self.cursor = conn.cursor(dictionary=True)
        else:
            self.cursor = conn.cursor()

    def execute(self, query, args=()):
        if self.db_type == 'sqlite':
            query = query.replace('%s', '?')
        self.cursor.execute(query, args)
        last_id = self.cursor.lastrowid
        affected = self.cursor.rowcount
        return last_id if last_id else affected

    def query(self, query, args=(), one=False):
        if self.db_type == 'sqlite':
            query = query.replace('%s', '?')
        self.cursor.execute(query, args)
        rv = self.cursor.fetchall()
        if self.db_type == 'sqlite':
            dict_rv = [dict(row) for row in rv]
        else:
            dict_rv = rv
        return (dict_rv[0] if dict_rv else None) if one else dict_rv

    def close(self):
        if hasattr(self, 'cursor') and self.cursor:
            try:
                self.cursor.close()
            except Exception:
                pass


@contextmanager
def transaction_scope(engine=None):
    """
    Atomic transaction context manager.
    Commits if the entire block exits cleanly; rolls back on ANY exception.
    Guarantees connection and cursor cleanup.
    """
    conn, db_type = get_db_connection(engine=engine)
    tx_ctx = None
    try:
        if db_type == 'mysql':
            conn.autocommit = False
        else:
            conn.isolation_level = None
            conn.execute("BEGIN TRANSACTION")

        tx_ctx = TransactionContext(conn, db_type)
        yield tx_ctx

        if db_type == 'mysql':
            conn.commit()
        else:
            conn.execute("COMMIT")
    except Exception as err:
        try:
            if db_type == 'mysql':
                conn.rollback()
            else:
                conn.execute("ROLLBACK")
        except Exception as rb_err:
            logger.warning(f"Rollback error: {rb_err}")
        raise DatabaseTransactionError(f"Transaction failed and was rolled back: {err}") from err
    finally:
        if tx_ctx:
            tx_ctx.close()
        try:
            conn.close()
        except Exception:
            pass


# =========================================================================
# INITIALIZATION AND SCHEMA VALIDATION
# =========================================================================

def init_db(engine=None):
    """
    Initializes the database schema and default seed data.
    Automatically runs on application startup.
    Supports MySQL (via schema.sql) and full SQLite compatibility.
    """
    conn, db_type = get_db_connection(engine=engine)
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
                        except Exception:
                            # Table, index, or column already exists / benign warning
                            pass
                for col_def in [
                    "phone VARCHAR(20) DEFAULT NULL",
                    "address VARCHAR(255) DEFAULT NULL",
                    "age INT DEFAULT 25",
                    "occupation VARCHAR(100) DEFAULT 'Student / Professional'",
                    "financial_exp VARCHAR(50) DEFAULT 'Beginner'",
                    "investment_exp VARCHAR(50) DEFAULT 'None'",
                    "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
                ]:
                    try:
                        cursor.execute(f"ALTER TABLE users ADD COLUMN {col_def}")
                    except Exception:
                        pass
                conn.commit()
            cursor.close()
            conn.close()
        else:
            # Complete SQLite schema covering every application table and foreign key
            cursor = conn.cursor()
            cursor.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT,
                password_hash TEXT NOT NULL,
                age INTEGER DEFAULT 25,
                occupation TEXT DEFAULT 'Student / Professional',
                financial_exp TEXT DEFAULT 'Beginner',
                investment_exp TEXT DEFAULT 'None',
                role TEXT DEFAULT 'user',
                phone TEXT DEFAULT NULL,
                address TEXT DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS financial_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                monthly_income REAL DEFAULT 0.00,
                fixed_expenses REAL DEFAULT 0.00,
                variable_expenses REAL DEFAULT 0.00,
                existing_savings REAL DEFAULT 0.00,
                loan_emi REAL DEFAULT 0.00,
                investment_experience TEXT DEFAULT 'Beginner',
                employment_status TEXT DEFAULT 'Student / Professional',
                monthly_expenses REAL DEFAULT 0.00,
                monthly_savings REAL DEFAULT 0.00,
                risk_tolerance TEXT DEFAULT 'medium',
                investment_horizon TEXT DEFAULT 'Medium Term',
                financial_goal TEXT DEFAULT 'Wealth Accumulation & Emergency Safety',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS expense_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS income (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                source TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
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
                category_id INTEGER,
                title TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (category_id) REFERENCES expense_categories(id) ON DELETE SET NULL
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
                goal_name TEXT,
                target_amount REAL NOT NULL,
                current_amount REAL DEFAULT 0.00,
                current_savings REAL DEFAULT 0.00,
                target_date TEXT NOT NULL,
                priority TEXT DEFAULT 'Medium',
                description TEXT,
                status TEXT DEFAULT 'In Progress',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS goal_contributions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                contribution_date TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (goal_id) REFERENCES financial_goals(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS risk_assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                score INTEGER NOT NULL,
                risk_profile TEXT NOT NULL,
                assessment_data TEXT,
                assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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

            CREATE TABLE IF NOT EXISTS investment_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                risk_level TEXT NOT NULL,
                minimum_information TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL,
                risk_profile TEXT NOT NULL,
                minimum_financial_health INTEGER DEFAULT 50,
                recommendation_text TEXT NOT NULL,
                suitability_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES investment_categories(id) ON DELETE CASCADE
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

            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_id TEXT DEFAULT 'default',
                message TEXT NOT NULL,
                sender TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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

            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                company_name TEXT NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(user_id, symbol)
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

            CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                company_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                average_buy_price REAL NOT NULL,
                purchase_date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
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

            CREATE TABLE IF NOT EXISTS market_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL UNIQUE,
                data_json TEXT NOT NULL,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TEXT NOT NULL
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
            ''')

            # Pre-seed expense categories in SQLite if empty
            cursor.execute("SELECT COUNT(*) as count FROM expense_categories")
            if cursor.fetchone()['count'] == 0:
                categories = [
                    ('Food', 'Groceries, dining, food delivery, and cafeteria expenses'),
                    ('Transport', 'Fuel, public transit, cab fares, and vehicle maintenance'),
                    ('Education', 'Tuition, textbooks, course certifications, and academic materials'),
                    ('Rent', 'Apartment rent, hostel fees, and accommodation charges'),
                    ('Shopping', 'Clothing, electronics, personal purchases, and lifestyle items'),
                    ('Entertainment', 'Movies, streaming subscriptions, outings, and hobbies'),
                    ('Bills', 'Electricity, water, mobile recharge, internet, and utilities'),
                    ('Other', 'Miscellaneous and unclassified daily expenditures')
                ]
                cursor.executemany("INSERT OR IGNORE INTO expense_categories (name, description) VALUES (?, ?)", categories)

            # Ensure compatibility columns exist on existing SQLite databases
            cursor.execute("PRAGMA table_info(users)")
            user_cols = [c[1] for c in cursor.fetchall()]
            for col, col_t in [
                ('password', 'TEXT'),
                ('password_hash', 'TEXT NOT NULL DEFAULT ""'),
                ('phone', 'TEXT'),
                ('address', 'TEXT'),
                ('age', 'INTEGER DEFAULT 25'),
                ('occupation', "TEXT DEFAULT 'Student / Professional'"),
                ('financial_exp', "TEXT DEFAULT 'Beginner'"),
                ('investment_exp', "TEXT DEFAULT 'None'"),
                ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
            ]:
                if col not in user_cols:
                    try:
                        cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {col_t}")
                    except Exception:
                        pass

            cursor.execute("PRAGMA table_info(expenses)")
            expense_cols = [c[1] for c in cursor.fetchall()]
            if 'category_id' not in expense_cols:
                cursor.execute("ALTER TABLE expenses ADD COLUMN category_id INTEGER")

            cursor.execute("PRAGMA table_info(financial_goals)")
            goal_cols = [c[1] for c in cursor.fetchall()]
            if 'goal_name' not in goal_cols:
                cursor.execute("ALTER TABLE financial_goals ADD COLUMN goal_name TEXT")
            if 'current_savings' not in goal_cols:
                cursor.execute("ALTER TABLE financial_goals ADD COLUMN current_savings REAL DEFAULT 0.00")

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

        # Synchronize password and password_hash columns safely to guarantee user access
        try:
            execute_db("""
                UPDATE users 
                SET password_hash = password 
                WHERE (password_hash IS NULL OR password_hash = '') AND password IS NOT NULL AND password != ''
            """)
            execute_db("""
                UPDATE users 
                SET password = password_hash 
                WHERE (password IS NULL OR password = '') AND password_hash IS NOT NULL AND password_hash != ''
            """)
        except Exception as sync_err:
            logger.warning(f"Password column synchronization notice: {sync_err}")

    except Exception as e:
        logger.error(f"init_db error: {e}")
        raise


def create_admin_user(email, password, name="System Administrator"):
    """
    Securely creates or promotes an administrator user account with hashed credentials.
    Enforces modern password policy requirements (minimum 12 characters).
    Returns (user_id, is_new).
    """
    email = (email or '').strip().lower()
    if not email or '@' not in email:
        raise ValueError("A valid administrator email address is required.")
    if not password or len(password) < 12:
        raise ValueError("Administrator password must be at least 12 characters long.")

    password_hash = generate_password_hash(password)

    # Check if user already exists
    existing = query_db("SELECT id, role FROM users WHERE email = %s", (email,), one=True)
    if existing:
        execute_db("""
            UPDATE users 
            SET password = %s, password_hash = %s, role = 'admin', name = %s
            WHERE id = %s
        """, (password_hash, password_hash, name, existing['id']))
        return existing['id'], False
    else:
        user_id = execute_db("""
            INSERT INTO users (name, email, password, password_hash, age, occupation, financial_exp, investment_exp, role)
            VALUES (%s, %s, %s, %s, 35, 'Financial Admin', 'Expert', 'Advanced', 'admin')
        """, (name, email, password_hash, password_hash))
        return user_id, True
