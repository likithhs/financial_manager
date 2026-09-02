# FinAI - Database Architecture & Design Specification (Phase 2)

## 1. Database Overview
* **Database Engine:** MySQL 8.0+ (with fallback capability to SQLite for lightweight testing)
* **Database Name:** `financial_manager`
* **Character Set / Collation:** `utf8mb4` / `utf8mb4_unicode_ci`
* **Precision Standard:** All monetary values strictly use `DECIMAL(12, 2)` to eliminate floating-point rounding inaccuracies.
* **Storage Engine:** `InnoDB` (ACID compliance, row-level locking, foreign key referential integrity).

---

## 2. Entity-Relationship (ER) Architecture

```
                                      +------------------+
                                      |      users       |
                                      +------------------+
                                                |
         +------------------+-------------------+-------------------+------------------+
         |                  |                   |                   |                  |
         v                  v                   v                   v                  v
+------------------+ +-------------+ +--------------------+ +----------------+ +---------------+
|financial_profiles| |   income    | |     expenses       | |financial_goals | |risk_assessments
+------------------+ +-------------+ +--------------------+ +----------------+ +---------------+
                                                |                   |                  
                                                v                   v                  
                                     +--------------------+ +------------------+       
                                     | expense_categories | |goal_contributions|       
                                     +--------------------+ +------------------+       

                                      +------------------+
                                      |      users       |
                                      +------------------+
                                                |
         +--------------------------------------+---------------------------------------+
         |                                      |                                       |
         v                                      v                                       v
+------------------+                   +------------------+                    +------------------+
|   chat_history   |                   |    watchlist     |                    |    portfolio     |
+------------------+                   +------------------+                    +------------------+

                                 +-----------------------+
                                 | investment_categories |
                                 +-----------------------+
                                             |
                                             v
                                 +-----------------------+
                                 |    recommendations    |
                                 +-----------------------+
```

---

## 3. Detailed Data Dictionary

### 3.1. `users` Table
Stores authenticated user credentials and role-based access information.
| Field | Type | Attributes | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INT` | `AUTO_INCREMENT`, `PRIMARY KEY` | Unique internal user ID |
| `name` | `VARCHAR(100)` | `NOT NULL` | Full name of the user |
| `email` | `VARCHAR(150)` | `NOT NULL`, `UNIQUE` | Unique email login identifier |
| `password` | `VARCHAR(255)` | `NOT NULL` | Cryptographically salted password hash (Werkzeug scrypt) |
| `password_hash` | `VARCHAR(255)` | `NULL` | Specification-compliant alias column |
| `role` | `ENUM('user','admin')`| `DEFAULT 'user'` | Role-based authorization tier |
| `age` | `INT` | `DEFAULT 25` | Demographic baseline for risk profiling |
| `occupation` | `VARCHAR(100)` | `DEFAULT 'Student / Professional'` | Professional activity |
| `financial_exp`| `VARCHAR(50)` | `DEFAULT 'Beginner'` | Financial knowledge self-assessment |
| `investment_exp`| `VARCHAR(50)` | `DEFAULT 'None'` | Asset class experience |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | Account creation timestamp |
| `updated_at` | `TIMESTAMP` | `ON UPDATE CURRENT_TIMESTAMP` | Last profile update timestamp |

### 3.2. `financial_profiles` Table
One-to-one financial baseline per user.
| Field | Type | Attributes | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INT` | `AUTO_INCREMENT`, `PRIMARY KEY` | Unique profile ID |
| `user_id` | `INT` | `NOT NULL`, `UNIQUE`, `FOREIGN KEY` | References `users(id) ON DELETE CASCADE` |
| `monthly_income` | `DECIMAL(12,2)` | `DEFAULT 0.00` | Net monthly baseline earnings |
| `fixed_expenses` | `DECIMAL(12,2)` | `DEFAULT 0.00` | Committed mandatory outlays (rent, fees, debt) |
| `variable_expenses`| `DECIMAL(12,2)` | `DEFAULT 0.00` | Discretionary lifestyle spending |
| `existing_savings` | `DECIMAL(12,2)` | `DEFAULT 0.00` | Liquid capital buffer |
| `loan_emi` | `DECIMAL(12,2)` | `DEFAULT 0.00` | Active debt repayment commitments |
| `investment_experience`| `VARCHAR(50)` | `DEFAULT 'Beginner'` | Investor maturity tier |
| `risk_tolerance` | `ENUM('low','medium','high')` | `DEFAULT 'medium'` | Initial risk profile |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | Record timestamp |
| `updated_at` | `TIMESTAMP` | `ON UPDATE CURRENT_TIMESTAMP` | Last updated timestamp |

### 3.3. `expense_categories` Table
Predefined master list of expenditure categories.
| Field | Type | Attributes | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INT` | `AUTO_INCREMENT`, `PRIMARY KEY` | Unique category ID |
| `name` | `VARCHAR(50)` | `NOT NULL`, `UNIQUE` | Category name (e.g. Food, Rent, Transport) |
| `description` | `VARCHAR(255)` | `NULL` | Scope explanation |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | Creation timestamp |

*Default Seed Data:* `Food`, `Transport`, `Education`, `Rent`, `Shopping`, `Entertainment`, `Bills`, `Other`.

### 3.4. `income` Table
Transaction-based ledger for cash inflows (preserves all transaction history; never overwrites).
| Field | Type | Attributes | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INT` | `AUTO_INCREMENT`, `PRIMARY KEY` | Unique income transaction ID |
| `user_id` | `INT` | `NOT NULL`, `FOREIGN KEY` | References `users(id) ON DELETE CASCADE` |
| `amount` | `DECIMAL(12,2)` | `NOT NULL` | Received capital amount |
| `source` | `VARCHAR(100)` | `NOT NULL` | Employer / Payer / Source |
| `date` | `DATE` | `NOT NULL` | Transaction receipt date |
| `description` | `TEXT` | `NULL` | Notes and remarks |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | Ledger creation timestamp |

### 3.5. `expenses` Table
Transaction-based ledger for living expenses.
| Field | Type | Attributes | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INT` | `AUTO_INCREMENT`, `PRIMARY KEY` | Unique expense ID |
| `user_id` | `INT` | `NOT NULL`, `FOREIGN KEY` | References `users(id) ON DELETE CASCADE` |
| `category_id` | `INT` | `NULL`, `FOREIGN KEY` | References `expense_categories(id) ON DELETE SET NULL` |
| `title` | `VARCHAR(100)` | `NOT NULL` | Expense description / Payee |
| `amount` | `DECIMAL(12,2)` | `NOT NULL` | Spent amount |
| `category` | `VARCHAR(50)` | `NOT NULL` | Category label |
| `date` | `DATE` | `NOT NULL` | Expense date |
| `description` | `TEXT` | `NULL` | Payment method / receipt notes |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | Entry timestamp |
| `updated_at` | `TIMESTAMP` | `ON UPDATE CURRENT_TIMESTAMP` | Update timestamp |

### 3.6. `financial_goals` & `goal_contributions` Tables
Supports target capital milestones and cumulative savings tracking.

#### `financial_goals`
| Field | Type | Attributes | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INT` | `AUTO_INCREMENT`, `PRIMARY KEY` | Unique goal ID |
| `user_id` | `INT` | `NOT NULL`, `FOREIGN KEY` | References `users(id) ON DELETE CASCADE` |
| `name` / `goal_name`| `VARCHAR(100)` | `NOT NULL` | Milestone label (e.g. Emergency Fund, Laptop) |
| `target_amount` | `DECIMAL(12,2)` | `NOT NULL` | Total capital required |
| `current_amount` | `DECIMAL(12,2)` | `DEFAULT 0.00` | Accumulated capital to date |
| `current_savings`| `DECIMAL(12,2)` | `DEFAULT 0.00` | Specification alias |
| `target_date` | `DATE` | `NOT NULL` | Target milestone completion date |
| `priority` | `VARCHAR(20)` | `DEFAULT 'Medium'` | Priority level (High, Medium, Low) |
| `status` | `VARCHAR(20)` | `DEFAULT 'In Progress'`| Status (In Progress, Completed) |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | Creation timestamp |
| `updated_at` | `TIMESTAMP` | `ON UPDATE CURRENT_TIMESTAMP` | Update timestamp |

#### `goal_contributions`
| Field | Type | Attributes | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INT` | `AUTO_INCREMENT`, `PRIMARY KEY` | Unique deposit ID |
| `goal_id` | `INT` | `NOT NULL`, `FOREIGN KEY` | References `financial_goals(id) ON DELETE CASCADE` |
| `user_id` | `INT` | `NOT NULL`, `FOREIGN KEY` | References `users(id) ON DELETE CASCADE` |
| `amount` | `DECIMAL(12,2)` | `NOT NULL` | Added deposit amount |
| `contribution_date` | `DATE` | `NOT NULL` | Deposit date |
| `description` | `TEXT` | `NULL` | Transaction remarks |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | Timestamp |

### 3.7. `risk_assessments` Table
Stores telemetry from user risk assessments and tracks volatility comfort.
| Field | Type | Attributes | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INT` | `AUTO_INCREMENT`, `PRIMARY KEY` | Unique evaluation ID |
| `user_id` | `INT` | `NOT NULL`, `FOREIGN KEY` | References `users(id) ON DELETE CASCADE` |
| `score` | `INT` | `NOT NULL` | Numerical score (0–100) |
| `risk_profile` | `ENUM(...)` | `NOT NULL` | Conservative, Moderate, Aggressive |
| `assessment_data`| `TEXT` | `NULL` | JSON structure of answers given |
| `assessed_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | Assessment timestamp |

### 3.8. `investment_categories` & `recommendations` Tables
Educational asset class definitions and rule-based recommendation mapping.

#### `investment_categories`
| Field | Type | Attributes | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INT` | `AUTO_INCREMENT`, `PRIMARY KEY` | Category ID |
| `name` | `VARCHAR(100)` | `NOT NULL`, `UNIQUE` | Asset class name |
| `description` | `TEXT` | `NULL` | Asset explanation |
| `risk_level` | `VARCHAR(50)` | `NOT NULL` | Volatility rating |
| `minimum_information` | `TEXT` | `NULL` | Benchmark horizons & statutory context |

#### `recommendations`
| Field | Type | Attributes | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INT` | `AUTO_INCREMENT`, `PRIMARY KEY` | Recommendation rule ID |
| `category_id` | `INT` | `NOT NULL`, `FOREIGN KEY` | References `investment_categories(id) ON DELETE CASCADE` |
| `risk_profile` | `VARCHAR(50)` | `NOT NULL` | Conservative, Moderate, Aggressive |
| `minimum_financial_health`| `INT` | `DEFAULT 50` | Required health score threshold |
| `recommendation_text` | `TEXT` | `NOT NULL` | Prescriptive advisory guidance |
| `suitability_notes` | `TEXT` | `NULL` | Educational context |

### 3.9. `chat_history` Table
Stores FinAI conversational messages between the user and the assistant.
| Field | Type | Attributes | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INT` | `AUTO_INCREMENT`, `PRIMARY KEY` | Unique message ID |
| `user_id` | `INT` | `NOT NULL`, `FOREIGN KEY` | References `users(id) ON DELETE CASCADE` |
| `session_id` | `VARCHAR(100)` | `DEFAULT 'default'` | Conversation session identifier |
| `message` | `TEXT` | `NOT NULL` | Message body (Never stores passwords or keys) |
| `sender` | `ENUM('user','assistant')` | `NOT NULL` | Sender role |
| `timestamp` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | Message timestamp |

### 3.10. `watchlist` Table
Stocks and market securities monitored by the user.
| Field | Type | Attributes | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INT` | `AUTO_INCREMENT`, `PRIMARY KEY` | Watchlist entry ID |
| `user_id` | `INT` | `NOT NULL`, `FOREIGN KEY` | References `users(id) ON DELETE CASCADE` |
| `symbol` | `VARCHAR(20)` | `NOT NULL` | Ticker symbol (e.g. TCS, INFY) |
| `company_name` | `VARCHAR(150)` | `NOT NULL` | Company name |
| `added_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | Added timestamp |
| `UNIQUE(user_id, symbol)` | Constraint | Guarantees no duplicate ticker per user |

### 3.11. `portfolio` Table
Academic virtual holdings tracking without live money/trading.
| Field | Type | Attributes | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INT` | `AUTO_INCREMENT`, `PRIMARY KEY` | Unique holding ID |
| `user_id` | `INT` | `NOT NULL`, `FOREIGN KEY` | References `users(id) ON DELETE CASCADE` |
| `symbol` | `VARCHAR(20)` | `NOT NULL` | Ticker symbol |
| `company_name` | `VARCHAR(150)` | `NOT NULL` | Company name |
| `quantity` | `INT` | `NOT NULL` | Holding share count |
| `average_buy_price` | `DECIMAL(12,2)`| `NOT NULL` | Purchase price per unit |
| `purchase_date` | `DATE` | `NOT NULL` | Date purchased |

### 3.12. `market_cache` Table
Temporarily caches third-party market quote responses with explicit TTL expiration.
| Field | Type | Attributes | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INT` | `AUTO_INCREMENT`, `PRIMARY KEY` | Unique cache record ID |
| `symbol` | `VARCHAR(20)` | `NOT NULL`, `UNIQUE` | Market asset symbol |
| `data_json` | `TEXT` | `NOT NULL` | Serialized price and quote payload |
| `fetched_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | Timestamp when quote was fetched |
| `expires_at` | `TIMESTAMP` | `NOT NULL` | Absolute expiry cutoff (prevents stale data) |

---

## 4. User Data Isolation & Security Architecture

1. **Strict User Ownership Isolation:**
   - Every financial table (`financial_profiles`, `income`, `expenses`, `financial_goals`, `goal_contributions`, `risk_assessments`, `chat_history`, `watchlist`, `portfolio`) contains a mandatory `user_id` foreign key referencing `users(id)`.
   - All backend SQL queries filter by `WHERE user_id = %s`, preventing User A from accessing or mutating User B's financial data under any circumstance.
   - Cascading deletes (`ON DELETE CASCADE`) ensure complete GDPR-compliant purge of all related financial records when a user account is deleted.

2. **Cryptographic Hashing:**
   - Plaintext passwords are never stored. Passwords are encrypted using Werkzeug's `generate_password_hash` (`scrypt` algorithm) and verified via `check_password_hash`.

3. **Parameterized SQL Queries:**
   - All database execution methods (`query_db` and `execute_db`) utilize parameterized query placeholders (`%s`), preventing SQL injection attacks.

---

## 5. How to Initialize the Database

### Option 1: Automatic Initialization via Flask
Whenever the Flask application starts or when running `from database import init_db; init_db()`, the application connects to MySQL using the `.env` credentials and automatically applies `database/schema.sql`.

### Option 2: Direct MySQL CLI
```bash
mysql -u root -p < database/schema.sql
```
