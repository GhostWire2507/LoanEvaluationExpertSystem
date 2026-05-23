Refactor checklist - Prolog-first verification

- [x] Business rules centralized in `rules.pl`.
- [x] `system_config.pl` is authoritative config for Prolog (no duplicate thresholds in Python).
- [x] `prolog_engine.py` is a thin wrapper; heavy decision logic removed.
- [x] Degraded/fallback mode is explicit and requires `PROLOG_DEGRADED=true`.
- [x] JSON storage exists in `storage.py` and is the recommended persistence.
- [x] Templates and README updated with new branding.
- [x] Tests added to `tests/test_evaluation.py` to verify core decision outcomes.

Files checked for duplicated business logic in Python:
- `prolog_engine.py` : contains only transport code and a minimal explicit degraded heuristic (guarded).
- `app.py` : orchestration, validation calls `validate_application()` (which calls Prolog), no duplicate rules.
- `models.py`, `storage.py` : persistence only.

If you want, I can now:
- Wire `app.py` fully to use `storage.py` instead of SQLAlchemy (make JSON the app default).
- Run tests locally (requires SWI-Prolog + pyswip) and report results.
