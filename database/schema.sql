-- ====================================================================
-- FinAI: AI-Powered Personal Financial Manager & Investment System
-- MASTER DATABASE SCHEMA (MySQL) - PHASE 2 SPECIFICATION
-- Database: financial_manager
-- ====================================================================

CREATE DATABASE IF NOT EXISTS financial_manager;
USE financial_manager;

-- --------------------------------------------------------------------
-- 1. USERS TABLE
-- Core authentication and role-based identity table
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,            -- Stores secure werkzeug hash
    password_hash VARCHAR(255),                 -- Alias column for specification compatibility
    role ENUM('user', 'admin') DEFAULT 'user',  -- RBAC: user vs admin
    age INT DEFAULT 25,
    occupation VARCHAR(100) DEFAULT 'Student / Professional',
    financial_exp VARCHAR(50) DEFAULT 'Beginner',
    investment_exp VARCHAR(50) DEFAULT 'None',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_email (email),
    INDEX idx_user_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 2. FINANCIAL PROFILES TABLE
-- One-to-one financial baseline per user for planning & scoring
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS financial_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    monthly_income DECIMAL(12, 2) DEFAULT 0.00,
    fixed_expenses DECIMAL(12, 2) DEFAULT 0.00,
    variable_expenses DECIMAL(12, 2) DEFAULT 0.00,
    existing_savings DECIMAL(12, 2) DEFAULT 0.00,
    loan_emi DECIMAL(12, 2) DEFAULT 0.00,
    investment_experience VARCHAR(50) DEFAULT 'Beginner',
    employment_status VARCHAR(50) DEFAULT 'Student / Professional',
    monthly_expenses DECIMAL(12, 2) DEFAULT 0.00,
    monthly_savings DECIMAL(12, 2) DEFAULT 0.00,
    risk_tolerance ENUM('low', 'medium', 'high') DEFAULT 'medium',
    investment_horizon VARCHAR(50) DEFAULT 'Medium Term',
    financial_goal VARCHAR(255) DEFAULT 'Wealth Accumulation & Emergency Safety',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 3. EXPENSE CATEGORIES TABLE
-- Predefined normalized categorization of living outlays
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS expense_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Pre-seed predefined expense categories
INSERT IGNORE INTO expense_categories (name, description) VALUES
('Food', 'Groceries, dining, food delivery, and cafeteria expenses'),
('Transport', 'Fuel, public transit, cab fares, and vehicle maintenance'),
('Education', 'Tuition, textbooks, course certifications, and academic materials'),
('Rent', 'Apartment rent, hostel fees, and accommodation charges'),
('Shopping', 'Clothing, electronics, personal purchases, and lifestyle items'),
('Entertainment', 'Movies, streaming subscriptions, outings, and hobbies'),
('Bills', 'Electricity, water, mobile recharge, internet, and utilities'),
('Other', 'Miscellaneous and unclassified daily expenditures');

-- --------------------------------------------------------------------
-- 4. INCOME TABLE
-- Transaction-based inflow records (strictly preserves every transaction)
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS income (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    source VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_income_user_date (user_id, date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Maintain plural incomes table for existing route queries
CREATE TABLE IF NOT EXISTS incomes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    source VARCHAR(100) NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    category VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_incomes_user_date (user_id, date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 5. EXPENSES TABLE
-- Transaction-based living expenditure records
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    category_id INT NULL,
    title VARCHAR(100) NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    category VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES expense_categories(id) ON DELETE SET NULL,
    INDEX idx_expenses_user_date (user_id, date),
    INDEX idx_expenses_category (category_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 6. FINANCIAL GOALS TABLE
-- Target savings milestones supporting accumulated contributions
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS financial_goals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    goal_name VARCHAR(100),                      -- Alias for specification compatibility
    target_amount DECIMAL(12, 2) NOT NULL,
    current_amount DECIMAL(12, 2) DEFAULT 0.00,
    current_savings DECIMAL(12, 2) DEFAULT 0.00, -- Alias for specification compatibility
    target_date DATE NOT NULL,
    priority VARCHAR(20) DEFAULT 'Medium',        -- High, Medium, Low
    description TEXT,
    status VARCHAR(20) DEFAULT 'In Progress',    -- In Progress, Completed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_goals_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 7. GOAL CONTRIBUTIONS TABLE
-- Detailed audit history of cumulative deposits made towards goals
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS goal_contributions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    goal_id INT NOT NULL,
    user_id INT NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    contribution_date DATE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (goal_id) REFERENCES financial_goals(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_contributions_goal (goal_id),
    INDEX idx_contributions_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 8. RISK ASSESSMENTS TABLE
-- Question telemetry and calculated risk profile tier
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS risk_assessments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    score INT NOT NULL,
    risk_profile ENUM('Conservative', 'Moderate', 'Aggressive') NOT NULL,
    assessment_data TEXT,
    assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_risk_user_time (user_id, assessed_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Maintain plural risk_profiles table for existing UI modules
CREATE TABLE IF NOT EXISTS risk_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    score INT NOT NULL,
    risk_level VARCHAR(30) NOT NULL,
    answers_json TEXT,
    explanation TEXT,
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_risk_profiles_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 9. INVESTMENT CATEGORIES TABLE
-- Non-speculative asset classes for educational asset allocation
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS investment_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    risk_level VARCHAR(50) NOT NULL,             -- Low Risk, Moderate Risk, High Volatility
    minimum_information TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Pre-seed educational investment categories
INSERT IGNORE INTO investment_categories (name, description, risk_level, minimum_information) VALUES
('Fixed Deposits & PPF', 'Statutory and bank-backed guaranteed return products for emergency liquidity.', 'Low Risk', 'Guaranteed capital preservation, 6.5% - 7.5% return, tax-exempt under Section 80C.'),
('Government Securities', 'Sovereign Treasury Bills and RBI floating rate savings bonds backed by Government of India.', 'Low Risk', 'Zero credit risk, 7.0% - 7.75% yield, semi-annual interest disbursement.'),
('Index Funds (NIFTY 50)', 'Low-cost passive mutual funds replicating the top 50 bluechip corporations in India.', 'Moderate Risk', '11% - 14% historical CAGR, zero fund manager bias, 3-7 year investment horizon.'),
('Diversified Mutual Funds', 'Actively managed equity schemes investing across large-cap and mid-cap sectors.', 'Moderate Risk', '12% - 15% long-term returns, professional fund management, requires 5+ years horizon.'),
('Exchange Traded Funds (ETFs)', 'Exchange-traded index baskets providing instant intraday liquidity on NSE/BSE.', 'Moderate Risk', 'Low expense ratio (<0.20%), tracks benchmarks, requires demat trading account.'),
('Sovereign Gold Bonds (SGB)', 'Denominated in grams of gold issued by Reserve Bank of India with guaranteed interest.', 'Low to Moderate', '2.5% annual payout + market gold appreciation, 8-year maturity, capital gains tax exempt.');

-- --------------------------------------------------------------------
-- 10. RECOMMENDATIONS TABLE
-- Normalized mapping of advice rules by category & risk tier
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    risk_profile VARCHAR(50) NOT NULL,           -- Conservative, Moderate, Aggressive
    minimum_financial_health INT DEFAULT 50,
    recommendation_text TEXT NOT NULL,
    suitability_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES investment_categories(id) ON DELETE CASCADE,
    INDEX idx_rec_cat_risk (category_id, risk_profile)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Maintain investment_recommendations table for existing personalized generator
CREATE TABLE IF NOT EXISTS investment_recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    primary_category VARCHAR(100) NOT NULL,
    risk_level VARCHAR(50) NOT NULL,
    recommended_allocation_json TEXT,
    rationale TEXT,
    advantages TEXT,
    risks TEXT,
    factors_considered TEXT,
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 11. CHAT HISTORY TABLE
-- Standardized FinAI conversational persistence
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS chat_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    session_id VARCHAR(100) DEFAULT 'default',
    message TEXT NOT NULL,
    sender ENUM('user', 'assistant') NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_chat_user_time (user_id, timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Maintain ai_conversations table for current UI chat messages
CREATE TABLE IF NOT EXISTS ai_conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    context_used_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_conv_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 12. WATCHLIST TABLE
-- User-curated stocks and market assets monitored
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS watchlist (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    company_name VARCHAR(150) NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_watchlist (user_id, symbol),
    INDEX idx_watchlist_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Maintain stock_watchlist table for existing route queries
CREATE TABLE IF NOT EXISTS stock_watchlist (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    company_name VARCHAR(150) NOT NULL,
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_stock (user_id, symbol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 13. PORTFOLIO TABLE
-- Virtual investment tracker for academic demonstration
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS portfolio (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    company_name VARCHAR(150) NOT NULL,
    quantity INT NOT NULL,
    average_buy_price DECIMAL(12, 2) NOT NULL,
    purchase_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_portfolio_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Maintain portfolios and portfolio_holdings tables for existing routes
CREATE TABLE IF NOT EXISTS portfolios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100) DEFAULT 'My Investment Portfolio',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS portfolio_holdings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    portfolio_id INT NOT NULL,
    user_id INT NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    company_name VARCHAR(150) NOT NULL,
    asset_type VARCHAR(50) DEFAULT 'Equity Stock',
    quantity INT NOT NULL,
    buy_price DECIMAL(10, 2) NOT NULL,
    buy_date DATE NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 14. MARKET CACHE TABLE
-- Timestamped cache for retrieved quotes with explicit TTL expiration
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS market_cache (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL UNIQUE,
    data_json TEXT NOT NULL,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    INDEX idx_cache_symbol_exp (symbol, expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 15. AUXILIARY EXISTING TABLES (Harmonized)
-- Budgets, Stocks, Analysis, Readiness
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS budgets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    month_year VARCHAR(7) NOT NULL,
    total_budget DECIMAL(12, 2) NOT NULL,
    category_budgets TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_month (user_id, month_year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS financial_analysis (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    total_income DECIMAL(12, 2) DEFAULT 0.00,
    total_expenses DECIMAL(12, 2) DEFAULT 0.00,
    savings DECIMAL(12, 2) DEFAULT 0.00,
    savings_rate DECIMAL(6, 2) DEFAULT 0.00,
    expense_ratio DECIMAL(6, 2) DEFAULT 0.00,
    emergency_fund_ratio DECIMAL(6, 2) DEFAULT 0.00,
    health_score INT DEFAULT 50,
    health_status VARCHAR(30) DEFAULT 'Moderate',
    explanation TEXT,
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS investment_readiness (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    is_ready TINYINT(1) DEFAULT 0,
    readiness_score INT DEFAULT 0,
    reasons_json TEXT,
    suggestions_json TEXT,
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS stocks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL UNIQUE,
    company_name VARCHAR(150) NOT NULL,
    sector VARCHAR(100) NOT NULL,
    market VARCHAR(50) DEFAULT 'NSE/BSE/US',
    current_price DECIMAL(10, 2) NOT NULL,
    previous_close DECIMAL(10, 2) NOT NULL,
    pe_ratio DECIMAL(8, 2) DEFAULT 0.00,
    market_cap VARCHAR(50) DEFAULT 'Large Cap',
    high_52w DECIMAL(10, 2) DEFAULT 0.00,
    low_52w DECIMAL(10, 2) DEFAULT 0.00,
    volatility VARCHAR(30) DEFAULT 'Moderate',
    risk_rating VARCHAR(30) DEFAULT 'Moderate',
    description TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS stock_analysis (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    company_name VARCHAR(150) NOT NULL,
    suitability_status VARCHAR(50) NOT NULL,
    suitability_score INT DEFAULT 50,
    analysis_reasons TEXT,
    user_risk_level VARCHAR(30),
    stock_risk_level VARCHAR(30),
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 16. SEED DATA (Academic Demo Admin & Predefined Stocks)
-- --------------------------------------------------------------------
-- Insert default Admin user if not present (Password: admin123)
INSERT IGNORE INTO users (id, name, email, password, password_hash, role)
VALUES (1, 'System Administrator', 'admin@financialmanager.com', 
        'scrypt:32768:8:1$xP5g6n9v$e16441bf971fce81cfdf7ef7d8b871c53044a2c3bc6689d0b7d7b003a3d54ef028e57813a37b3f46f33bbdf5ff3b6801088c5ef92a177265b4c10c14c382cefb',
        'scrypt:32768:8:1$xP5g6n9v$e16441bf971fce81cfdf7ef7d8b871c53044a2c3bc6689d0b7d7b003a3d54ef028e57813a37b3f46f33bbdf5ff3b6801088c5ef92a177265b4c10c14c382cefb',
        'admin');

-- Pre-seed Stocks
INSERT IGNORE INTO stocks (symbol, company_name, sector, market, current_price, previous_close, pe_ratio, market_cap, high_52w, low_52w, volatility, risk_rating, description) VALUES 
('TCS', 'Tata Consultancy Services', 'Information Technology', 'NSE', 3850.00, 3810.00, 28.5, 'Large Cap (₹14 Lakh Cr)', 4250.00, 3310.00, 'Low', 'Low', 'Global leader in IT services, digital and business solutions with consistent dividend track record.'),
('INFY', 'Infosys Limited', 'Information Technology', 'NSE', 1540.00, 1560.00, 24.2, 'Large Cap (₹6.4 Lakh Cr)', 1760.00, 1350.00, 'Moderate', 'Moderate', 'Leading provider of next-generation digital services and consulting across 50+ countries.'),
('RELIANCE', 'Reliance Industries Ltd', 'Energy & Telecom', 'NSE', 2920.00, 2895.00, 26.8, 'Large Cap (₹19 Lakh Cr)', 3050.00, 2220.00, 'Moderate', 'Moderate', 'India’s largest conglomerate spanning petrochemicals, refining, retail, and digital telecom services (Jio).'),
('HDFCBANK', 'HDFC Bank Ltd', 'Banking & Finance', 'NSE', 1620.00, 1605.00, 18.9, 'Large Cap (₹12 Lakh Cr)', 1750.00, 1360.00, 'Low', 'Low', 'India’s largest private sector bank known for robust asset quality and extensive branch network.'),
('ITC', 'ITC Limited', 'FMCG & Consumer Goods', 'NSE', 430.00, 428.00, 25.1, 'Large Cap (₹5.3 Lakh Cr)', 499.00, 399.00, 'Low', 'Low', 'Diversified conglomerate with dominant presence in FMCG, hotels, paperboards, packaging, and agri-business.'),
('TATAMOTORS', 'Tata Motors Ltd', 'Automotive', 'NSE', 980.00, 960.00, 16.4, 'Large Cap (₹3.2 Lakh Cr)', 1179.00, 590.00, 'High', 'High', 'Leading global automobile manufacturer of cars, utility vehicles, trucks, buses and Jaguar Land Rover.'),
('ZOMATO', 'Zomato Limited', 'Internet & Food Delivery', 'NSE', 240.00, 235.00, 78.0, 'Large Cap (₹2.1 Lakh Cr)', 298.00, 88.00, 'High', 'High', 'Fast-growing internet consumer platform for food delivery, quick commerce (Blinkit) and dining out.'),
('AAPL', 'Apple Inc.', 'Technology & Consumer Electronics', 'NASDAQ', 225.00, 222.50, 33.2, 'Mega Cap ($3.4 Trillion)', 237.00, 164.00, 'Moderate', 'Moderate', 'Global designer and manufacturer of smartphones, personal computers, tablets, wearables, and services.'),
('MSFT', 'Microsoft Corporation', 'Software & Cloud Computing', 'NASDAQ', 430.00, 425.00, 35.8, 'Mega Cap ($3.2 Trillion)', 468.00, 309.00, 'Low', 'Low', 'World leader in software products, Azure cloud infrastructure, AI solutions, and enterprise productivity.'),
('NVDA', 'NVIDIA Corporation', 'Semiconductors & AI', 'NASDAQ', 125.00, 118.00, 52.4, 'Mega Cap ($3.0 Trillion)', 140.00, 40.00, 'High', 'High', 'Pioneer of GPU-accelerated computing and undisputed market leader in generative AI chips and data center acceleration.');
