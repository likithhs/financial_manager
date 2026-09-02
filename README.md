# FinAI — AI-Powered Personal Financial Assistant & Investment Readiness Platform

**Academic Context**: BCA Final Year Major Project (2026)  
**Architecture**: Modular Flask Blueprints + Service Layer Architecture + MySQL 8.0 + Modern Dark Fintech Glassmorphic UI  

---

## 📌 Project Overview & Core Philosophy

FinAI is an institutional-grade, rule-based AI financial intelligence suite designed on one foundational premise:

> **"Financial stability must precede market risk."**  
> An investor should never take market risks (direct equities, mutual funds, speculative assets) if they lack an emergency runway or positive cashflow.

FinAI enforces this principle through an automated **Investment Readiness Gatekeeper** and a **10-Factor Psychometric Risk Profiler** before unlocking asset allocation and securities analytics.

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
                       CONTEXT-AWARE FinAI ASSISTANT
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
| **FinAI Assistant** | Conversational assistant providing answers derived directly from live database ledger. |
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
Ensure your MySQL server is running, then import the database schema:
```bash
mysql -u root -p < database/schema.sql
```
*(Or open `database/schema.sql` in MySQL Workbench / phpMyAdmin and execute it).*

### 5. Configure Environment
Copy `.env.example` to `.env` and set your local MySQL password:
```ini
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=finai_supersecret_academic_key_2026

# Local MySQL Configuration
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=YOUR_PASSWORD_HERE
DB_NAME=financial_manager
```

### 6. Run Verification Test Suites
Verify that both database schema and service layers pass all tests:
```bash
python test_database_phase2.py
python test_backend_phase3.py
```

### 7. Run the Application
```bash
python app.py
```
Open **`http://127.0.0.1:5000`** in your browser.

- **Default Administrator Account:**
  - **Email:** `admin@financialmanager.com`
  - **Password:** `admin123`
- **User Account:** Click **"Get Started"** on the landing page to register a clean user profile.

---

## 📂 Project Directory Structure

```
financial_manager/
├── ai/                              # Deterministic AI & Psychometric Engines
│   ├── financial_analyzer.py        # 6-Pillar financial health scoring
│   ├── investment_readiness.py      # Investment gatekeeper decision model
│   ├── risk_analyzer.py             # 10-Factor psychometric risk profiler
│   └── stock_recommender.py         # Stock risk vs investor suitability matrix
├── database/                        # Database Schemas & Seeds
│   └── schema.sql                   # Clean MySQL 8.0 schema & seed securities
├── routes/                          # Modular Flask Blueprint Controllers
│   ├── admin_routes.py              # Admin Command Console
│   ├── analysis_routes.py           # Health, risk & readiness endpoints
│   ├── assistant_routes.py          # FinAI conversational endpoint
│   ├── auth_routes.py               # User login, registration & session auth
│   ├── dashboard_routes.py          # Main dashboard views
│   ├── error_handlers.py            # Centralized 400, 403, 404, 500 handlers
│   ├── expense_routes.py            # Outlay tracking
│   ├── income_routes.py             # Inflow tracking
│   ├── main_routes.py               # Public landing page & /health
│   ├── market_routes.py             # Securities & stock explorer
│   └── portfolio_routes.py          # Watchlist & virtual portfolio
├── services/                        # Service Layer & Validation Logic
│   ├── auth_helper.py               # @login_required, @admin_required guards
│   ├── expense_service.py           # Expense CRUD operations
│   ├── goal_service.py              # Goal contribution engine
│   ├── income_service.py            # Income CRUD operations
│   ├── user_service.py              # User management & authentication
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
│   └── ...
├── app.py                           # Application Factory & Blueprint Registration
├── database.py                      # MySQL Connection pooling & query wrappers
└── requirements.txt                 # Python dependencies
```

---

## 📄 License & Academic Declaration
Developed as a Major Project for the **Bachelor of Computer Applications (BCA)**. Strictly for educational and academic demonstration purposes.
