"""Application configuration for the Loan Evaluation Expert System."""

import os
from datetime import timedelta


class Config:
    """Single place for runtime configuration."""

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Database (local SQLite file).
    SQLALCHEMY_DATABASE_URI = (
        f"sqlite:///{os.path.join(BASE_DIR, 'loan_system.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Session and security.
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "change-this-in-production",
    )
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

    # App runtime.
    DEBUG = os.getenv("FLASK_DEBUG", "true").lower() == "true"
    PORT = int(os.getenv("PORT", "5000"))

    # Prolog runtime.
    PROLOG_EXECUTABLE = os.getenv("PROLOG_EXECUTABLE", "swipl")
