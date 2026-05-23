# MFS Intelligent Loan Assessment & Management System

A simplified, local-first loan evaluation platform that follows a Prolog-first design:
- **Flask** for HTTP routing and UI rendering (thin Python layer)
- **SWI-Prolog** as the primary expert-logic engine (rules live in `rules.pl`)
- **JSON file storage** for lightweight persistence (see `storage.py`)
- **Tailwind-based templates** for a minimal UI

## 1) What was simplified

This project has been kept to a small, understandable structure:

```text
.
├── app.py                # Routes + auth + dashboards + API
├── config.py             # Centralized runtime settings
├── models.py             # Optional SQLAlchemy models (kept for compatibility)
├── storage.py            # JSON-based lightweight storage (primary persistence)
├── prolog_engine.py      # Prolog bridge (Prolog-first; degraded fallback optional)
├── rules.pl              # Expert system rules (single source of truth)
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

2. Initialize and run the app (uses JSON storage by default):
   ```bash
   python app.py
   ```
   On first run the `data/` folder is created and seeded as needed.

3. Optional compatibility: if you still want to use SQLite/SQLAlchemy, `models.py` and
   `init_db()` are retained for backward compatibility but JSON storage is the recommended
   lightweight default.

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
- [x] JSON-based storage implemented in `storage.py`
- [x] Prolog-first evaluation model in `rules.pl` and `system_config.pl`
- [x] `prolog_engine.py` is a thin Prolog bridge; a clear degraded fallback exists behind `PROLOG_DEGRADED`.

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
PROLOG_DEGRADED=true python app.py  # run in degraded mode if Prolog isn't installed
```

## 8) Future improvements

- Add migration tooling (Alembic)
- Add CSRF protection using Flask-WTF
- Add endpoint/form tests with pytest
- Add admin override workflow with audit log
