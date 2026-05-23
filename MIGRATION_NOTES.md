Migration notes - Prolog-first refactor

What changed
- Moved core decision logic into Prolog (`rules.pl`, `system_config.pl`).
  - All risk/DTI/credit thresholds and evaluation rules are implemented in `rules.pl`.
- `prolog_engine.py` is now a thin Prolog bridge:
  - Prefers Prolog for all evaluations and validations.
  - If Prolog is unavailable, it will raise an error unless `PROLOG_DEGRADED=true` is set.
  - Degraded fallback is explicit and minimal; marked `evaluation_method: 'degraded'`.
- Storage migrated to JSON-first approach:
  - `storage.py` implements a lightweight JSON file storage (data/ folder).
  - `models.py` (SQLAlchemy) retained for compatibility but JSON is the recommended default.
- Configuration duplication: system configuration lives in `system_config.pl` (Prolog). `config.py` remains for Flask runtime settings (secret key, port, etc.).

Why
- Prolog is the single source of truth for business rules, improving maintainability and testability.
- JSON storage simplifies local development and distribution.
- Explicit degraded mode avoids silent divergence of behavior when Prolog is unavailable.

How to run
- With Prolog:
  - Ensure SWI-Prolog is installed and `pyswip` is available in the Python env.
  - Run: `python app.py` (the app will consult `system_config.pl` and `rules.pl`).
- Without Prolog (degraded):
  - Run: `PROLOG_DEGRADED=true python app.py`
  - Degraded mode uses simple heuristics and is intended only for emergency or local testing.

Notes
- Any business-rule changes should be made in `rules.pl`.
- Keep `system_config.pl` as the authoritative runtime configuration for Prolog-driven behavior.
