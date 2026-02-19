"""
Database configuration for the Loan Evaluation Expert System
"""
import os
from datetime import timedelta

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database configuration
SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "loan_system.db")}'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False

# Session configuration
SESSION_TYPE = 'filesystem'
SESSION_PERMANENT = False
SESSION_USE_SIGNER = True
SESSION_KEY_PREFIX = 'loan_system:'
PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

# Secret key for sessions
SECRET_KEY = 'loan-evaluation-expert-system-secret-key-2024'

# Application settings
DEBUG = True
PORT = 5000

# Prolog configuration
PROLOG_EXECUTABLE = 'swipl'  # Path to SWI-Prolog executable
