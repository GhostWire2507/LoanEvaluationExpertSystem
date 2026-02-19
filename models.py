"""
Database models for the Loan Evaluation Expert System
"""
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication and loan applications"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    loan_applications = db.relationship('LoanApplication', backref='user', lazy=True)
    
    def set_password(self, password):
        """Hash and set the password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify the password"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class LoanApplication(db.Model):
    """Loan application model storing all loan requests"""
    __tablename__ = 'loan_applications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Loan parameters
    loan_amount = db.Column(db.Float, nullable=False)
    annual_income = db.Column(db.Float, nullable=False)
    credit_score = db.Column(db.Integer, nullable=False)
    debt_amount = db.Column(db.Float, nullable=False)
    employment_years = db.Column(db.Integer, nullable=False)
    employment_type = db.Column(db.String(50), nullable=False)  # full_time, part_time, self_employed
    loan_purpose = db.Column(db.String(100), nullable=False)
    
    # Calculated fields
    dti_ratio = db.Column(db.Float, nullable=True)  # Debt-to-Income ratio
    
    # Evaluation results
    evaluation_result = db.Column(db.String(20), nullable=True)  # approved, conditional, rejected
    evaluation_explanation = db.Column(db.Text, nullable=True)
    evaluation_confidence = db.Column(db.Float, nullable=True)
    evaluated_at = db.Column(db.DateTime, nullable=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert loan application to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'loan_amount': self.loan_amount,
            'annual_income': self.annual_income,
            'credit_score': self.credit_score,
            'debt_amount': self.debt_amount,
            'employment_years': self.employment_years,
            'employment_type': self.employment_type,
            'loan_purpose': self.loan_purpose,
            'dti_ratio': self.dti_ratio,
            'evaluation_result': self.evaluation_result,
            'evaluation_explanation': self.evaluation_explanation,
            'evaluation_confidence': self.evaluation_confidence,
            'evaluated_at': self.evaluated_at.isoformat() if self.evaluated_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class EvaluationHistory(db.Model):
    """History of all loan evaluations for analytics"""
    __tablename__ = 'evaluation_history'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('loan_applications.id'), nullable=False)
    credit_score = db.Column(db.Integer, nullable=False)
    dti_ratio = db.Column(db.Float, nullable=False)
    result = db.Column(db.String(20), nullable=False)
    rule_fired = db.Column(db.String(100), nullable=True)
    explanation = db.Column(db.Text, nullable=True)
    evaluated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert evaluation history to dictionary"""
        return {
            'id': self.id,
            'application_id': self.application_id,
            'credit_score': self.credit_score,
            'dti_ratio': self.dti_ratio,
            'result': self.result,
            'rule_fired': self.rule_fired,
            'explanation': self.explanation,
            'evaluated_at': self.evaluated_at.isoformat() if self.evaluated_at else None
        }
