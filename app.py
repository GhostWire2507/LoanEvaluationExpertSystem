"""
Loan Evaluation Expert System - Main Flask Application
"""
import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from config import Config
from models import db, User, LoanApplication, EvaluationHistory
from prolog_engine import initialize_prolog, evaluate_loan, get_prolog_engine

# Create Flask application
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Initialize Prolog engine
def init_prolog():
    """Initialize Prolog engine with rules"""
    rules_path = os.path.join(os.path.dirname(__file__), 'rules.pl')
    success = initialize_prolog(rules_path)
    if success:
        print("Prolog engine initialized successfully")
    else:
        print("Using fallback Python evaluation (Prolog not available)")
    return success

# Initialize Prolog on startup
with app.app_context():
    init_prolog()


# =====================================================================
# Authentication Decorators
# =====================================================================

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin access for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function


# =====================================================================
# Routes - Authentication
# =====================================================================

@app.route('/')
def index():
    """Home page - redirect to login or dashboard"""
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user and user.is_admin:
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        errors = []
        
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters.')
        
        if not email or '@' not in email:
            errors.append('Please enter a valid email address.')
        
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            errors.append('Username already exists.')
        
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('register.html')
        
        # Create user
        user = User(username=username, email=email)
        user.set_password(password)
        
        # First user becomes admin
        if User.query.count() == 0:
            user.is_admin = True
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            
            flash(f'Welcome back, {user.username}!', 'success')
            
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# =====================================================================
# Routes - User Dashboard
# =====================================================================

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard - view own applications"""
    user = User.query.get(session['user_id'])
    applications = LoanApplication.query.filter_by(user_id=user.id).order_by(LoanApplication.created_at.desc()).all()
    
    # Calculate statistics
    total_applications = len(applications)
    approved = sum(1 for a in applications if a.evaluation_result == 'approved')
    conditional = sum(1 for a in applications if a.evaluation_result == 'conditional')
    rejected = sum(1 for a in applications if a.evaluation_result == 'rejected')
    
    stats = {
        'total': total_applications,
        'approved': approved,
        'conditional': conditional,
        'rejected': rejected
    }
    
    return render_template('dashboard.html', 
                         applications=applications, 
                         stats=stats,
                         user=user)


@app.route('/apply', methods=['GET', 'POST'])
@login_required
def apply_loan():
    """Loan application form"""
    if request.method == 'POST':
        try:
            # Get form data
            loan_amount = float(request.form.get('loan_amount', 0))
            annual_income = float(request.form.get('annual_income', 0))
            credit_score = int(request.form.get('credit_score', 0))
            debt_amount = float(request.form.get('debt_amount', 0))
            employment_years = int(request.form.get('employment_years', 0))
            employment_type = request.form.get('employment_type', 'full_time')
            loan_purpose = request.form.get('loan_purpose', '').strip()
            
            # Validation
            errors = []
            
            if loan_amount <= 0:
                errors.append('Loan amount must be greater than 0.')
            
            if annual_income <= 0:
                errors.append('Annual income must be greater than 0.')
            
            if credit_score < 300 or credit_score > 850:
                errors.append('Credit score must be between 300 and 850.')
            
            if employment_years < 0:
                errors.append('Employment years cannot be negative.')
            
            if not loan_purpose:
                errors.append('Please specify the loan purpose.')
            
            if errors:
                for error in errors:
                    flash(error, 'error')
                return render_template('apply.html')
            
            # Calculate DTI
            dti_ratio = (debt_amount / annual_income) * 100 if annual_income > 0 else 0
            
            # Evaluate loan using expert system
            evaluation = evaluate_loan(credit_score, debt_amount, annual_income, employment_years, loan_amount)
            
            # Create loan application
            application = LoanApplication(
                user_id=session['user_id'],
                loan_amount=loan_amount,
                annual_income=annual_income,
                credit_score=credit_score,
                debt_amount=debt_amount,
                employment_years=employment_years,
                employment_type=employment_type,
                loan_purpose=loan_purpose,
                dti_ratio=dti_ratio,
                evaluation_result=evaluation['result'],
                evaluation_explanation=evaluation['explanation'],
                evaluation_confidence=evaluation['confidence'],
                evaluated_at=datetime.utcnow()
            )
            
            db.session.add(application)
            
            # Add to evaluation history
            history = EvaluationHistory(
                application_id=None,  # Will be set after commit
                credit_score=credit_score,
                dti_ratio=dti_ratio,
                result=evaluation['result'],
                explanation=evaluation['explanation']
            )
            
            db.session.commit()
            
            # Update history with application_id
            history.application_id = application.id
            db.session.add(history)
            db.session.commit()
            
            flash(f'Your loan application has been evaluated: {evaluation["result"].upper()}', 
                  'success' if evaluation['result'] == 'approved' else 'info')
            
            return redirect(url_for('view_application', application_id=application.id))
            
        except ValueError as e:
            flash(f'Invalid input: {str(e)}', 'error')
        except Exception as e:
            flash(f'Error processing application: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('apply.html')


@app.route('/application/<int:application_id>')
@login_required
def view_application(application_id):
    """View a specific loan application"""
    application = LoanApplication.query.get_or_404(application_id)
    
    # Check access - only owner or admin can view
    if application.user_id != session['user_id'] and not session.get('is_admin'):
        flash('You do not have permission to view this application.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get evaluation details
    engine = get_prolog_engine()
    details = engine.get_evaluation_details(
        application.credit_score,
        application.debt_amount,
        application.annual_income,
        application.employment_years,
        application.loan_amount
    )
    
    return render_template('view_application.html', 
                         application=application,
                         details=details)


# =====================================================================
# Routes - Admin Dashboard
# =====================================================================

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard - view all applications"""
    # Get all applications with user info
    applications = LoanApplication.query.join(User).order_by(LoanApplication.created_at.desc()).all()
    
    # Calculate statistics
    total_applications = len(applications)
    approved = sum(1 for a in applications if a.evaluation_result == 'approved')
    conditional = sum(1 for a in applications if a.evaluation_result == 'conditional')
    rejected = sum(1 for a in applications if a.evaluation_result == 'rejected')
    
    # Calculate average confidence
    confidence_values = [a.evaluation_confidence for a in applications if a.evaluation_confidence]
    avg_confidence = sum(confidence_values) / len(confidence_values) if confidence_values else 0
    
    # Get recent evaluations
    recent_history = EvaluationHistory.query.order_by(EvaluationHistory.evaluated_at.desc()).limit(10).all()
    
    stats = {
        'total': total_applications,
        'approved': approved,
        'conditional': conditional,
        'rejected': rejected,
        'avg_confidence': round(avg_confidence, 2)
    }
    
    return render_template('admin_dashboard.html',
                         applications=applications,
                         stats=stats,
                         recent_history=recent_history)


@app.route('/admin/users')
@admin_required
def admin_users():
    """Admin - manage users"""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin_users.html', users=users)


@app.route('/admin/user/<int:user_id>/toggle-admin', methods=['POST'])
@admin_required
def toggle_admin(user_id):
    """Toggle admin status for a user"""
    if user_id == session['user_id']:
        flash('You cannot change your own admin status.', 'error')
        return redirect(url_for('admin_users'))
    
    user = User.query.get_or_404(user_id)
    user.is_admin = not user.is_admin
    db.session.commit()
    
    flash(f'Admin status updated for {user.username}.', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete a user and their applications"""
    if user_id == session['user_id']:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin_users'))
    
    user = User.query.get_or_404(user_id)
    
    # Delete associated applications
    LoanApplication.query.filter_by(user_id=user_id).delete()
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {user.username} has been deleted.', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/application/<int:application_id>')
@admin_required
def admin_view_application(application_id):
    """Admin view a specific application"""
    application = LoanApplication.query.get_or_404(application_id)
    
    # Get evaluation details
    engine = get_prolog_engine()
    details = engine.get_evaluation_details(
        application.credit_score,
        application.debt_amount,
        application.annual_income,
        application.employment_years,
        application.loan_amount
    )
    
    return render_template('admin_view_application.html',
                         application=application,
                         details=details)


@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    """Admin analytics page"""
    # Get evaluation history
    history = EvaluationHistory.query.order_by(EvaluationHistory.evaluated_at.desc()).all()
    
    # Calculate statistics by credit score ranges
    credit_ranges = {
        '750+': {'total': 0, 'approved': 0, 'conditional': 0, 'rejected': 0},
        '650-749': {'total': 0, 'approved': 0, 'conditional': 0, 'rejected': 0},
        '300-649': {'total': 0, 'approved': 0, 'conditional': 0, 'rejected': 0}
    }
    
    for h in history:
        if h.credit_score >= 750:
            range_key = '750+'
        elif h.credit_score >= 650:
            range_key = '650-749'
        else:
            range_key = '300-649'
        
        credit_ranges[range_key]['total'] += 1
        if h.result == credit_ranges[range_key]['approved'] 'approved':
            += 1
        elif h.result == 'conditional':
            credit_ranges[range_key]['conditional'] += 1
        elif h.result == 'rejected':
            credit_ranges[range_key]['rejected'] += 1
    
    return render_template('admin_analytics.html',
                         history=history,
                         credit_ranges=credit_ranges)


# =====================================================================
# API Routes
# =====================================================================

@app.route('/api/evaluate', methods=['POST'])
@login_required
def api_evaluate():
    """API endpoint for loan evaluation"""
    try:
        data = request.get_json()
        
        credit_score = int(data.get('credit_score', 0))
        debt_amount = float(data.get('debt_amount', 0))
        annual_income = float(data.get('annual_income', 0))
        employment_years = int(data.get('employment_years', 0))
        loan_amount = float(data.get('loan_amount', 0))
        
        evaluation = evaluate_loan(credit_score, debt_amount, annual_income, employment_years, loan_amount)
        
        return jsonify({
            'success': True,
            'evaluation': evaluation
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/stats')
@admin_required
def api_stats():
    """API endpoint for statistics"""
    applications = LoanApplication.query.all()
    
    stats = {
        'total': len(applications),
        'approved': sum(1 for a in applications if a.evaluation_result == 'approved'),
        'conditional': sum(1 for a in applications if a.evaluation_result == 'conditional'),
        'rejected': sum(1 for a in applications if a.evaluation_result == 'rejected')
    }
    
    return jsonify(stats)


# =====================================================================
# Error Handlers
# =====================================================================

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('error.html', error='Page not found', code=404), 404


@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    db.session.rollback()
    return render_template('error.html', error='Internal server error', code=500), 500


# =====================================================================
# Database Initialization
# =====================================================================

def init_db():
    """Initialize the database with tables and default data"""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create default admin user if not exists
        if User.query.count() == 0:
            admin = User(
                username='admin',
                email='admin@loansystem.com',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created (username: admin, password: admin123)")
        
        print("Database initialized successfully!")


# =====================================================================
# Main Entry Point
# =====================================================================

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Run application
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=Config.PORT)
