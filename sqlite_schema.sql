-- SQLite schema for local deployment (MFS Intelligent Loan Assessment & Management System)
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    is_admin INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS loan_applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    loan_amount REAL NOT NULL,
    annual_income REAL NOT NULL,
    credit_score INTEGER NOT NULL,
    debt_amount REAL NOT NULL,
    employment_years INTEGER NOT NULL,
    employment_type TEXT NOT NULL,
    loan_purpose TEXT NOT NULL,
    dti_ratio REAL,
    evaluation_result TEXT,
    evaluation_explanation TEXT,
    evaluation_confidence REAL,
    evaluated_at DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS evaluation_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER NOT NULL,
    credit_score INTEGER NOT NULL,
    dti_ratio REAL NOT NULL,
    result TEXT NOT NULL,
    rule_fired TEXT,
    explanation TEXT,
    evaluated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES loan_applications(id) ON DELETE CASCADE
);

-- Optional seed admin user (replace hash after first run)
-- INSERT INTO users (username, email, password_hash, is_admin)
-- VALUES ('admin', 'admin@loansystem.com', '<paste-werkzeug-hash>', 1);
