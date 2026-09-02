# AI-Powered Personal Financial Manager, Investment and Stock Market Recommendation System

**Academic Project**: Bachelor of Computer Applications (BCA) Final Year Project  
**Technology Stack**: Python 3, Flask, MySQL, HTML5, CSS3, Jinja2  
**Architecture**: 14 Independent Modules + Rule-Based AI Engine + FinAI Conversational Assistant + Stock Market Decision Support  

---

## 📌 1. Project Overview & Core Concept

Most existing financial websites simply list random stocks or show basic calculators. This system is fundamentally different:

> **Core Differentiating Principle:**  
> **"Financial stability must precede investment risk."**  
> The system first analyzes personal cashflow, evaluates financial health (0–100), determines risk tolerance through a 7-factor questionnaire, and tests **Investment Readiness**. Only when a user has a stable runway does the system recommend general investments and evaluate individual stock suitability.

```
                         USER FINANCIAL DATA
                                 ↓
                     FINANCIAL HEALTH ANALYSIS (0-100)
                                 ↓
                       RISK PROFILE ANALYSIS
                  (Conservative / Moderate / Aggressive)
                                 ↓
                     INVESTMENT READINESS GATEWAY
                       [READY vs. NOT READY]
                                 │
             ┌───────────────────┴───────────────────┐
             ▼                                       ▼
  GENERAL INVESTMENTS ENGINE               STOCK MARKET ENGINE
  - Fixed Income & FDs (50%)               - Stock Directory & Quotes
  - Debt & Hybrid Funds (30%)              - AI Volatility & Suitability
  - Sovereign Gold Bonds (10%)             - Watchlist & Virtual Portfolio
  - Bluechip Index Funds (10%)             - Decision: Suitable / Watchlist / High Risk
             │                                       │
             └───────────────────┬───────────────────┘
                                 ▼
                    INTERACTIVE FinAI ASSISTANT
             (Contextual Answers with User's Actual Numbers)
```

---

## 🏛️ 2. The 14 Major Modules

| # | Module Name | Description & Key Logic |
|---|-------------|-------------------------|
| **1** | **User Authentication & Profile** | Werkzeug scrypt hashing, session security, financial & investment experience tracking. |
| **2** | **Personal Finance Management** | Comprehensive Income & Expense CRUD with 9 categories (Food, Rent, Education, Bills, etc.). |
| **3** | **Savings & Budget Management** | Monthly budget caps, spending tracking, over-budget warnings, Savings Rate calculation. |
| **4** | **Financial Goal Management** | **Cumulative contribution logic** (e.g. ₹5,000 + ₹2,000 = ₹7,000, never replaces), progress bars. |
| **5** | **Financial Health Analysis** | 4-factor scoring (Savings Rate, Expense Ratio, Emergency Fund Runway, Discipline) $\rightarrow$ 5 Grades. |
| **6** | **Risk Profile Analysis** | 7-question weighted questionnaire $\rightarrow$ Conservative (7-13), Moderate (14-21), Aggressive (22-28). |
| **7** | **Investment Readiness Gatekeeper** | Decision engine testing if emergency runway and cashflow exist before allowing investments. |
| **8** | **General Investment Engine** | Separate asset allocation for FDs, PPF, Sovereign Gold Bonds, Debt & Hybrid Mutual Funds. |
| **9** | **Stock Market Module** | Listed stock directory (TCS, INFY, RELIANCE, HDFC, ITC, TATAMOTORS, ZOMATO, AAPL, MSFT, NVDA). |
| **10** | **AI Stock Suitability Engine** | Matches company volatility & beta against user risk profile $\rightarrow$ Suitable, Watchlist, Higher Risk, Unsuitable. |
| **11** | **Stock Watchlist** | Custom user ticker watchlist with real-time price changes and instant AI evaluation links. |
| **12** | **Virtual Portfolio Management** | Asset tracking, Book Value, Market Value, Unrealized P&L, Asset Allocation weightage. |
| **13** | **Interactive FinAI Assistant** | Context-aware guidance assistant using user's live numbers (Income, Savings, Health, Risk). |
| **14** | **Admin & Reporting Dashboard** | System metrics, user directory, transaction audits, stock analysis logs, AI query logs. |

---

## 🚀 3. Visual Studio Code Step-by-Step Setup Guide

Follow these exact steps in **Visual Studio Code**:

### Step 1: Open the Project in VS Code
1. Launch **Visual Studio Code**.
2. Click **File ➔ Open Folder...**
3. Select the project directory:  
   `C:\Users\LIKITH H S\.gemini\antigravity\scratch\financial_manager`

### Step 2: Open Integrated Terminal
- Press ``Ctrl + ` `` (Backtick) or click **Terminal ➔ New Terminal**.

### Step 3: Set up Python Virtual Environment
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# (Or Command Prompt: venv\Scripts\activate.bat)
```

### Step 4: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 5: Configure MySQL Database (or use Instant SQLite Auto-Fallback)
The application includes a dual-mode database connector:
- **Default MySQL**:
  1. Open XAMPP / MySQL Workbench and start MySQL service.
  2. Create database: `CREATE DATABASE financial_manager;`
  3. Import schema: Run `database/database.sql` in MySQL.
  4. Ensure `.env` has your DB credentials (`DB_USER=root`, `DB_PASSWORD=`).
- **Instant SQLite Fallback**: If MySQL is not installed or running, the system will automatically create `database/financial_manager.db` and initialize all tables seamlessly!

### Step 6: Seed Test Users and Scenarios
Run the seeding script to populate academic demo users:
```powershell
python database/seed_data.py
```

### Step 7: Run the Flask Web Application
```powershell
python app.py
```
Open your web browser and visit:  
👉 **`http://127.0.0.1:5000`**

---

## 👥 4. Pre-configured Academic Demo Users

| User Scenario | Email | Password | Financial Health | Risk Profile | Investment Verdict |
|---------------|-------|----------|------------------|--------------|-------------------|
| **User 1: Balanced** | `user1@test.com` | `user123` | **Good (82/100)** | **Moderate** | **Ready**: Hybrid & Index Funds, Bluechips |
| **User 2: Unready** | `user2@test.com` | `user123` | **Poor (28/100)** | **Conservative** | **NOT READY**: Restricted until emergency fund built |
| **User 3: Conservative** | `user3@test.com` | `user123` | **Excellent (90/100)** | **Conservative** | **Ready**: FDs, SGB Gold, Debt Funds prioritized |
| **User 4: Aggressive** | `user4@test.com` | `user123` | **Excellent (92/100)** | **Aggressive** | **Ready**: High-growth Mid-caps & Equity |
| **System Admin** | `admin@financialmanager.com` | `admin123` | Admin Account | Full Access | Complete system audit logs & analytics |

---

## 🧮 5. Mathematical Formulas & Algorithmic Design

### A. Savings & Savings Rate
$$\text{Savings} = \text{Total Income} - \text{Total Expenses}$$
$$\text{Savings Rate (\%)} = \left( \frac{\text{Savings}}{\text{Total Income}} \right) \times 100$$

### B. Expense Ratio
$$\text{Expense Ratio (\%)} = \left( \frac{\text{Total Expenses}}{\text{Total Income}} \right) \times 100$$

### C. Emergency Fund Runway
$$\text{Runway (Months)} = \frac{\text{Liquid Emergency Savings}}{\text{Average Monthly Expenses}}$$

### D. Financial Health Scoring (Total: 100 Points)
- **Savings Rate Component (35 pts)**: $\ge 35\% \rightarrow 35\text{ pts}$, $20-34\% \rightarrow 28\text{ pts}$, $10-19\% \rightarrow 18\text{ pts}$, $0-9\% \rightarrow 8\text{ pts}$, $<0\% \rightarrow 0\text{ pts}$.
- **Expense Ratio Component (25 pts)**: $\le 50\% \rightarrow 25\text{ pts}$, $51-70\% \rightarrow 20\text{ pts}$, $71-85\% \rightarrow 12\text{ pts}$, $>85\% \rightarrow 4\text{ pts}$.
- **Emergency Runway Component (25 pts)**: $\ge 6\text{ months} \rightarrow 25\text{ pts}$, $3-5\text{ months} \rightarrow 18\text{ pts}$, $1-2\text{ months} \rightarrow 10\text{ pts}$, $<1\text{ month} \rightarrow 2\text{ pts}$.
- **Budget & Goal Discipline (15 pts)**: Active adherence to budget limits and active goal savings.

---

## 🎓 6. Top 25 BCA Viva Voce Questions & Model Answers

### Q1: What is the main objective of this project?
**Answer:** The objective is to build an intelligent, full-stack financial decision-support system that combines personal cashflow tracking, algorithmic financial health evaluation, risk tolerance assessment, and an investment readiness gatekeeper before providing personalized asset allocations and stock suitability analysis.

### Q2: Why is the application not just a standard stock recommendation system?
**Answer:** A standalone stock recommender blindly tells anyone to buy stocks regardless of their financial condition. Our system enforces the rule that **financial stability precedes market risk**. If a user has negative savings or no emergency buffer, the system restricts investment recommendations and guides them on building cash reserves first.

### Q3: Why are the Investments module and Stock Market module kept separate?
**Answer:** General investments encompass broad asset classes (Fixed Deposits, Debt Funds, Hybrid Funds, Sovereign Gold Bonds) intended for capital preservation and core financial planning. Direct stocks represent individual equity ownership with higher volatility and company-specific risk. Keeping them separate prevents beginners from conflating diversified mutual funds with speculative single-stock trading.

### Q4: How is password security implemented?
**Answer:** Passwords are never stored in plain text. We utilize `werkzeug.security.generate_password_hash` with the scrypt/pbkdf2 hashing algorithm and cryptographic salt. Authentication verifies passwords using `check_password_hash`.

### Q5: Explain the cumulative update logic used in Goal Management.
**Answer:** In traditional simple forms, updating a goal amount often overwrites the existing balance. In our system, when a user contributes additional funds (e.g. adding ₹2,000 to an existing ₹5,000 balance), the backend performs cumulative arithmetic ($\text{new} = \text{current} + \text{added} = ₹7,000$), recalculates progress percentage, and checks milestone completion.

### Q6: How does the AI Assistant personalize its answers?
**Answer:** When a user asks a question (such as *"Where should I invest?"*), the assistant queries the database for that specific user's monthly income, expenses, net savings, health score, and risk profile. It then constructs an answer incorporating their actual numbers instead of a generic canned response.

### Q7: What happens if an external Stock API or AI API is offline?
**Answer:** The architecture is designed with modular service layers (`services/stock_service.py` and `services/ai_service.py`). If API keys are absent or the network is unavailable, the application automatically falls back to an offline directory with realistic data and a deterministic rule-based AI engine, ensuring the project never crashes during evaluation.

### Q8: What database relationships exist in the system?
**Answer:** The `users` table acts as the primary entity with a 1-to-Many relationship with `incomes`, `expenses`, `budgets`, `financial_goals`, `risk_profiles`, `stock_watchlist`, `portfolios`, and `ai_conversations`, enforced with Foreign Keys and `ON DELETE CASCADE`.

---

## 🔒 7. AI Ethics & Risk Safety Disclaimers
1. The application clearly displays risk disclaimers across all investment and stock views.
2. The AI assistant never promises guaranteed returns or speculative predictions.
3. The virtual portfolio is for educational simulation and does not execute real-money stock brokerage orders.

---

**Developed for Academic Evaluation & BCA Degree Viva Voce.**
