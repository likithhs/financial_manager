# Finora — AI-Powered Personal Financial Assistant & Investment Readiness Platform

**Academic Context**: BCA Final Year Major Project (2026)  
**Architecture**: Modular Flask Blueprints + Service Layer Architecture + MySQL 8.0 + Modern Dark Fintech Glassmorphic UI  

---

## 📌 Project Overview & Core Philosophy

Finora is an institutional-grade, rule-based AI financial intelligence suite designed on one foundational premise:

> **"Financial stability must precede market risk."**  
> An investor should never take market risks (direct equities, mutual funds, speculative assets) if they lack an emergency runway or positive cashflow.

Finora enforces this principle through an automated **Investment Readiness Gatekeeper** and a **10-Factor Psychometric Risk Profiler** before unlocking asset allocation and securities analytics.

```
                         USER FINANCIAL CASHFLOW
                                   ↓
                   6-PILLAR FINANCIAL HEALTH EVALUATION
                                   ↓
           10-FACTOR PSYCHOMETRIC RISK TOLERANCE PROFILER
               (Capacity • Experience • Emotional Drawdown)
                                   ↓
                     INVESTMENT READINESS GATEWAY
                       [READY vs. NOT READY]
                                   │
              ┌────────────────────┴────────────────────┐
              ▼                                         ▼
   ASSET ALLOCATION ENGINE                     SECURITIES TELEMETRY
   - Fixed Deposits & T-Bills (50%)            - Real-Time Market Tickers
   - Sovereign Gold Bonds (20%)                - Volatility Rating
   - Liquid Debt Funds (20%)                   - Suitability Matrix
   - Large-Cap Index (10%)                     - Virtual Portfolio Tracking
              │                                         │
              └────────────────────┬────────────────────┘
                                   ▼
                       CONTEXT-AWARE Finora ASSISTANT
            (Deterministic Prescriptions Using User's Actual Database Data)
```

---

## 🏛️ Core Platform Capabilities

| Module | Purpose & Logic |
|---|---|
| **Dashboard** | Real-time cashflow telemetry, net savings rate, budget utilization, and recent ledger activity. |
| **Income Sources** | Multi-source recurring income tracking (Salary, Freelance, Investments, Business). |
| **Expense Tracker** | Granular categorized outlay tracking across 9 standard expenditure categories. |
| **Savings & Budget** | Strict monthly budget ceilings with over-budget alerts and real-time utilization progress. |
| **Financial Goals** | Target milestone tracking with **cumulative contribution logic** and deadline monitoring. |
| **Financial Health Diagnostics** | 0–100 Stability Score grading Emergency Runway, Savings Ratio, and Outlay Discipline. |
| **Risk Profile Evaluation** | **10-Factor Psychometric Profiler** across 3 Pillars (Capacity, Experience, Volatility Comfort). |
| **Investment Readiness** | Gatekeeper testing positive monthly cashflow and 3–6 months emergency reserves. |
| **Asset Allocation AI** | Mathematically weighted portfolio distribution customized to evaluated risk capacity. |
| **Market Telemetry** | Curated Indian equity catalog with P/E ratios, volatility ratings, and sector metrics. |
| **Stock Suitability Engine** | Matrix matching stock volatility with user risk profile to prevent excessive capital risk. |
| **Virtual Portfolio** | Position tracking, book value, market value, and unrealized profit/loss calculation. |
| **Finora Assistant** | Conversational assistant providing answers derived directly from live database ledger. |
| **Admin Command Console** | Dedicated operator dashboard for user administration, audit logs, and securities telemetry. |

---

## 🛠️ Technology Stack

- **Backend**: Python 3.10+, Flask 3.0+, Modular Blueprint Architecture (`routes/`, `services/`)
- **Database**: MySQL 8.0 with `mysql-connector-python` (Strict relational integrity, foreign keys, cascade deletes)
- **Frontend**: HTML5, CSS3 Glassmorphism (Dark Fintech Cyan/Blue Theme), Vanilla JavaScript (ScrollSpy, Persistent Scroll Memory)
- **Security**: PBKDF2/scrypt password hashing (`werkzeug.security`), role-based access control (RBAC), SQL parameterization

---

## 🚀 Quickstart Guide for Collaborators

### 1. Clone the Repository
```bash
git clone https://github.com/likithhs/financial_manager.git
cd financial_manager
```

### 2. Create and Activate Virtual Environment
- **Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
- **Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Initialization
### 4. Database Setup & Initialization

Finora supports two explicit database backends selected via `DB_ENGINE`:

#### Option A: MySQL 8.0 (Primary Production Engine)
Ensure your MySQL server is running, then import the database schema:
```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS financial_manager;"
mysql -u root -p financial_manager < database/schema.sql
```
*(Or open `database/schema.sql` in MySQL Workbench / phpMyAdmin and execute it).*

#### Option B: SQLite (Local Development & Test Engine)
To run without a local MySQL server:
```bash
# Set DB_ENGINE=sqlite in .env or environment
export DB_ENGINE=sqlite
# On startup, Finora automatically initializes the complete SQLite schema
python app.py
```

---

### 5. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Generate a cryptographically secure 32-byte secret key and paste it into `.env`:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
> **Security Note:** Never commit `.env` or your `SECRET_KEY` to source control. If you rotate your `SECRET_KEY`, all existing user sessions will be invalidated and users will need to log in again.

**Environment Variables Reference:**
| Variable | Description | Default |
|---|---|---|
| `DB_ENGINE` | Database backend selector (`mysql` or `sqlite`) | `mysql` |
| `MYSQL_HOST` | MySQL database hostname / IP | `127.0.0.1` |
| `MYSQL_PORT` | MySQL connection port | `3306` |
| `MYSQL_USER` | MySQL database user | `root` |
| `MYSQL_PASSWORD` | MySQL user password | *(empty)* |
| `MYSQL_DB` | MySQL database name | `financial_manager` |
| `SQLITE_PATH` | File path for SQLite database | `database/financial_manager.db` |
| `SECRET_KEY` | 32-byte hexadecimal session encryption key | *(required)* |
| `FLASK_ENV` | Runtime environment (`production` or `development`) | `production` |
| `FLASK_DEBUG` | Debug mode toggle (`False` in production) | `False` |
| `GEMINI_API_KEY` | Optional API key for Google Gemini conversational AI | *(optional)* |

Example `.env`:
```ini
FLASK_APP=app.py
FLASK_ENV=production
FLASK_DEBUG=False
FLASK_HOST=127.0.0.1
SECRET_KEY=<your_generated_32_byte_secret_key>

# Database Engine Selection
DB_ENGINE=mysql

# MySQL Settings
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=YOUR_PASSWORD_HERE
MYSQL_DB=financial_manager

# SQLite Settings (Used if DB_ENGINE=sqlite)
SQLITE_PATH=database/financial_manager.db
```

---

### 6. Initialize Administrator Account Securely
Finora does not ship with hardcoded administrator credentials. Create or update your administrator account securely using the interactive CLI command:
```bash
flask init-admin
```
*(Or alternately: `python app.py init-admin`)*

You will be prompted to enter the administrator's email and password (**minimum 12 characters**, conforming to NIST SP 800-63B guidelines) securely with password masking and confirmation.

---

### 7. Run Verification Test Suites
Verify that database schemas, transaction safety, and financial calculations pass all tests:
```bash
python test_database_phase2.py
python test_backend_phase3.py
python test_financial_calculations.py
python test_database_reliability.py
```

---

### 8. Run the Application

**Development Mode (Local Loopback 127.0.0.1):**
```bash
python app.py
```

**Production Deployment (WSGI Server):**
Use Waitress (recommended for Windows/cross-platform) or Gunicorn (Linux):
```bash
# Using Waitress
python wsgi.py
# or
waitress-serve --host=127.0.0.1 --port=5000 wsgi:app

# Using Gunicorn (Linux/macOS)
gunicorn -w 4 -b 127.0.0.1:5000 wsgi:app
```
Open **`http://127.0.0.1:5000`** in your browser.

- **Administrator:** Log in with the administrator email and password provisioned in Step 6.
- **Regular Users:** Click **"Get Started"** on the landing page to register a new user profile.

---

## 📂 Project Directory Structure

```
financial_manager/
├── ai/                              # Deterministic AI & Psychometric Engines
│   ├── date_utils.py                # Calendar month boundary & date helpers
│   ├── financial_analyzer.py        # 6-Pillar financial health scoring
│   ├── financial_assistant.py       # Conversational AI assistant
│   ├── investment_readiness.py      # Investment gatekeeper decision model
│   ├── investment_recommender.py    # Asset allocation model
│   ├── risk_analyzer.py             # 10-Factor psychometric risk profiler
│   └── stock_recommender.py         # Stock risk vs investor suitability matrix
├── database/                        # Database Schemas & Seeds
│   ├── schema.sql                   # Clean MySQL 8.0 schema & seed securities
│   └── seed_data.py                 # Multi-persona realistic test data
├── routes/                          # Modular Flask Blueprint Controllers
│   ├── admin_routes.py              # Admin Command Console & audit logs
│   ├── ai_routes.py                 # Finora conversational endpoint & Gemini integration
│   ├── analysis_routes.py           # Health, risk & readiness endpoints
│   ├── api_routes.py                # RESTful JSON API endpoints
│   ├── auth_routes.py               # User login, registration, settings & sessions
│   ├── budget_routes.py             # Monthly budget ceilings & category limits
│   ├── dashboard_routes.py          # Main dashboard views & summary telemetry
│   ├── error_handlers.py            # Centralized 400, 401, 403, 404, 500 handlers
│   ├── financial_routes.py          # Transactional income & expense management
│   ├── goal_routes.py               # Financial goals & cumulative contributions
│   ├── investment_routes.py         # Asset allocation & investment recommendations
│   ├── main_routes.py               # Public landing page & /health endpoint
│   ├── portfolio_routes.py          # Watchlist & virtual portfolio tracking
│   └── stock_routes.py              # Curated Indian stock explorer & suitability
├── services/                        # Service Layer & Validation Logic
│   ├── auth_helper.py               # Canonical @login_required, @admin_required guards
│   ├── expense_service.py           # Transactional expense CRUD operations
│   ├── financial_service.py         # Financial calculations, runway & cashflow
│   ├── goal_service.py              # Atomic goal creation & contribution engine
│   ├── income_service.py            # Transactional income logging
│   ├── portfolio_service.py         # Portfolio holding management
│   ├── user_service.py              # User management & password hash synchronization
│   └── validators.py                # Safe monetary & email validation
├── static/
│   ├── css/
│   │   └── style.css                # Dark fintech design system & animations
│   └── js/
│       └── landing.js               # Landing ScrollSpy & micro-interactions
├── templates/                       # Jinja2 Modular HTML Templates
│   ├── admin/                       # Admin Command Console templates
│   ├── base.html                    # Base layout with role-aware sidebar
│   ├── dashboard.html               # Main telemetry cockpit
│   ├── index.html                   # High-conversion public landing page
│   ├── investment_readiness.html    # Gatekeeper diagnostic dashboard
│   ├── risk_profile.html            # 10-Factor psychometric assessment
│   ├── settings.html                # Account settings & profile management
│   └── profile.html                 # Extends canonical settings.html
├── app.py                           # Application Factory & Blueprint Registration
├── config.py                        # Centralized configuration & environment loader
├── database.py                      # Multi-engine DB layer, transactions & cleanup
└── requirements.txt                 # Python dependencies
```

---

## 📄 License & Academic Declaration
Developed as a Major Project for the **Bachelor of Computer Applications (BCA)**. Strictly for educational and academic demonstration purposes.
