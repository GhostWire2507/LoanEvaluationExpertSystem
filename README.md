# MFS Intelligent Loan Assessment & Management System

A simplified, local-first loan evaluation platform that combines:
- **Flask** for the web app
- **SWI-Prolog rules** for expert reasoning (with Python fallback)
- **SQLite** for persistent local storage
- **Tailwind-based templates** for a clean fintech UI

## 1) What was simplified

This project has been kept to a small, understandable structure:

```text
.
├── app.py                # Routes + auth + dashboards + API
├── config.py             # Centralized runtime settings
├── models.py             # SQLite-backed SQLAlchemy models
├── prolog_engine.py      # Prolog bridge + fallback evaluator
├── rules.pl              # Expert system rules
├── sqlite_schema.sql     # Raw SQLite schema (for local/manual setup)
├── requirements.txt
└── templates/
```

## 2) Quick local setup (MCP Phase 1)

1. Create environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Initialize DB through Flask models:
   ```bash
   python app.py
   ```
   On first run, tables are created and a default admin is seeded.

3. Optional: initialize DB manually via SQLite schema:
   ```bash
   sqlite3 loan_system.db < sqlite_schema.sql
   ```

## 3) Run the app

```bash
python app.py
```

- URL: `http://localhost:5000`
- Default seeded admin (first run only):
  - username: `admin`
  - password: `admin123`

## 4) MCP implementation checklist

### Phase 1: Environment Setup
- [x] SQLite database configuration in `config.py`
- [x] SQLAlchemy and raw SQLite schema (`sqlite_schema.sql`)
- [x] First-run DB bootstrap in `init_db()`

### Phase 2: Backend Core
- [x] HTTP server and route handling (`app.py`)
- [x] Session-based login/logout
- [x] Role-based guards (`login_required`, `admin_required`)
- [x] Prolog evaluation integration + fallback engine

### Phase 3: Frontend Development
- [x] Login/Register views
- [x] User dashboard + apply loan flow
- [x] Admin dashboard, users, analytics pages

### Phase 4: Integration
- [x] Form submission to evaluation engine
- [x] Persisted storage of applications and evaluation history
- [x] Access isolation per user/admin

### Phase 5: Testing (minimum)
Suggested cases:
- High credit + low DTI => approved
- Medium credit + manageable DTI => conditional/approved by rule
- Low credit or poor DTI => rejected
- Non-admin cannot access admin routes
- User cannot read other users' applications

### Phase 6: Optimization
- [x] Reduced duplicated statistics logic via helper function
- [x] Fixed admin analytics aggregation bug
- [ ] Add automated tests (recommended next)

## 5) Security notes

- Passwords are hashed with Werkzeug
- Session secret is configurable via environment variable (`SECRET_KEY`)
- Route-level role checks are enforced for admin endpoints
- SQLAlchemy ORM helps avoid SQL injection by default parameterization

## 6) Core decision model

Key derived metrics:
- **DTI** = `(debt_amount / annual_income) * 100`
- Rule-driven evaluation from `rules.pl`

Decision outcomes:
- `approved`
- `conditional`
- `rejected`

Each application stores:
- decision
- explanation
- confidence
- evaluation timestamp

## 7) Useful commands

```bash
# Syntax validation
python -m py_compile app.py models.py prolog_engine.py config.py

# Start server
python app.py
```

## 8) Future improvements

- Add migration tooling (Alembic)
- Add CSRF protection using Flask-WTF
- Add endpoint/form tests with pytest
- Add admin override workflow with audit log
