"""
Prolog Engine Wrapper for Loan Evaluation Expert System
This module provides the interface between Python and SWI-Prolog
"""
import os
import re
from typing import Dict, Any, Optional, Tuple

class PrologEngine:
    """
    Wrapper class for SWI-Prolog to evaluate loan applications
    """
    
    def __init__(self, prolog_executable: str = 'C:\\Program Files\\swipl\\bin\\swipl.exe'):
        """
        Initialize the Prolog engine
        
        Args:
            prolog_executable: Path to SWI-Prolog executable
        """
        self.prolog_executable = prolog_executable
        self.prolog = None
        self.rules_file = None
        self._initialized = False
        
    def initialize(self, rules_path: str) -> bool:
        """
        Initialize the Prolog engine with the rules file and system configuration
        
        Args:
            rules_path: Path to the Prolog rules file
            
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Set environment variables for SWI-Prolog
            import os
            os.environ['SWI_HOME'] = 'C:\\Program Files\\swipl'
            os.environ['SWIPL'] = self.prolog_executable
            
            # Try to import pyswip
            from pyswip import Prolog
            
            self.rules_file = rules_path
            
            # Initialize Prolog with error handling
            try:
                self.prolog = Prolog()
                
                # Load system configuration first
                config_path = os.path.join(os.path.dirname(rules_path), 'system_config.pl')
                if os.path.exists(config_path):
                    self.prolog.consult(config_path)
                    print(f"System configuration loaded from: {config_path}")
                
                # Load the main rules file
                self.prolog.consult(rules_path)
                
                self._initialized = True
                print(f"Prolog engine initialized with rules from: {rules_path}")
                return True
            except Exception as prolog_error:
                print(f"Error initializing Prolog engine: {prolog_error}")
                print("This may be due to SWI-Prolog not being installed or incompatible version.")
                print("Using fallback evaluation instead.")
                self._initialized = False
                return False
            
        except ImportError:
            print("Warning: pyswip not installed. Using fallback evaluation.")
            self._initialized = False
            return False
        except Exception as e:
            print(f"Error importing pyswip: {e}")
            print("Using fallback evaluation instead.")
            self._initialized = False
            return False
    
    def evaluate_loan(
        self, 
        credit_score: int, 
        debt_amount: float, 
        annual_income: float, 
        employment_years: int, 
        loan_amount: float
    ) -> Dict[str, Any]:
        """
        Evaluate a loan application using the Prolog expert system
        
        Args:
            credit_score: Applicant's credit score
            debt_amount: Total monthly/annual debt payments
            annual_income: Annual gross income
            employment_years: Years of employment
            loan_amount: Requested loan amount
            
        Returns:
            Dictionary with evaluation results
        """
        if self._initialized and self.prolog:
            return self._evaluate_with_prolog(
                credit_score, debt_amount, annual_income, 
                employment_years, loan_amount
            )
        else:
            # Fallback to Python-based evaluation
            return self._evaluate_fallback(
                credit_score, debt_amount, annual_income,
                employment_years, loan_amount
            )
    
    def _evaluate_with_prolog(
        self, 
        credit_score: int, 
        debt_amount: float, 
        annual_income: float, 
        employment_years: int, 
        loan_amount: float
    ) -> Dict[str, Any]:
        """
        Evaluate using Prolog engine
        """
        try:
            # Calculate DTI
            dti = (debt_amount / annual_income) * 100 if annual_income > 0 else 0
            
            # Query Prolog
            query = f"evaluate({credit_score}, {debt_amount}, {annual_income}, {employment_years}, {loan_amount}, Result, Explanation, Confidence)"
            
            result_list = list(self.prolog.query(query))
            
            if result_list:
                result = result_list[0]
                return {
                    'result': result.get('Result', 'rejected'),
                    'explanation': result.get('Explanation', 'No explanation available'),
                    'confidence': float(result.get('Confidence', 50.0)),
                    'dti_ratio': round(dti, 2),
                    'credit_category': self._get_credit_category(credit_score),
                    'dti_category': self._get_dti_category(dti),
                    'evaluation_method': 'prolog'
                }
            else:
                return self._evaluate_fallback(
                    credit_score, debt_amount, annual_income,
                    employment_years, loan_amount
                )
                
        except Exception as e:
            print(f"Prolog evaluation error: {e}")
            return self._evaluate_fallback(
                credit_score, debt_amount, annual_income,
                employment_years, loan_amount
            )
    
    def validate_application(
        self, 
        loan_amount: float, 
        annual_income: float, 
        credit_score: int, 
        employment_years: int, 
        loan_purpose: str
    ) -> Dict[str, Any]:
        """
        Validate loan application using Prolog rules
        
        Args:
            loan_amount: Requested loan amount
            annual_income: Annual income
            credit_score: Credit score
            employment_years: Years of employment
            loan_purpose: Purpose of the loan
            
        Returns:
            Dictionary with validation result and any errors
        """
        if not self._initialized:
            # Fallback validation
            errors = []
            if loan_amount <= 0:
                errors.append('Loan amount must be greater than 0.')
            if annual_income <= 0:
                errors.append('Annual income must be greater than 0.')
            if credit_score < 300 or credit_score > 850:
                errors.append('Credit score must be between 300 and 850.')
            if employment_years < 0:
                errors.append('Employment years cannot be negative.')
            if not loan_purpose or loan_purpose.strip() == '':
                errors.append('Please specify the loan purpose.')
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'validation_method': 'fallback'
            }
        
        try:
            # Use Prolog for validation
            query = f"validate_application({loan_amount}, {annual_income}, {credit_score}, {employment_years}, '{loan_purpose}', Result)."
            solutions = list(self.prolog.query(query))
            
            if solutions:
                result = solutions[0]['Result']
                if result == 'valid':
                    return {
                        'valid': True,
                        'errors': [],
                        'validation_method': 'prolog'
                    }
                elif isinstance(result, str) and result.startswith('errors('):
                    # Extract errors from Prolog result
                    error_list = result[6:-1].split(',') if len(result) > 7 else []
                    cleaned_errors = [err.strip().strip("'") for err in error_list if err.strip()]
                    return {
                        'valid': False,
                        'errors': cleaned_errors,
                        'validation_method': 'prolog'
                    }
            
            # Fallback if Prolog query fails
            return {
                'valid': False,
                'errors': ['Validation system error'],
                'validation_method': 'fallback'
            }
            
        except Exception as e:
            print(f"Error in Prolog validation: {e}")
            return self._validate_fallback(loan_amount, annual_income, credit_score, employment_years, loan_purpose)
    
    def _validate_fallback(
        self, 
        loan_amount: float, 
        annual_income: float, 
        credit_score: int, 
        employment_years: int, 
        loan_purpose: str
    ) -> Dict[str, Any]:
        """Fallback validation method"""
        errors = []
        if loan_amount <= 0:
            errors.append('Loan amount must be greater than 0.')
        if annual_income <= 0:
            errors.append('Annual income must be greater than 0.')
        if credit_score < 300 or credit_score > 850:
            errors.append('Credit score must be between 300 and 850.')
        if employment_years < 0:
            errors.append('Employment years cannot be negative.')
        if not loan_purpose or loan_purpose.strip() == '':
            errors.append('Please specify the loan purpose.')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'validation_method': 'fallback'
        }
    
    def _get_credit_category(self, score: int) -> str:
        """Get credit category from score"""
        if score >= 750:
            return 'high'
        elif score >= 650:
            return 'medium'
        else:
            return 'low'
    
    def _get_dti_category(self, dti: float) -> str:
        """Get DTI category from ratio"""
        if dti < 15:
            return 'excellent'
        elif dti < 30:
            return 'good'
        elif dti < 43:
            return 'moderate'
        else:
            return 'poor'
    
    def get_evaluation_details(
        self, 
        credit_score: int, 
        debt_amount: float, 
        annual_income: float, 
        employment_years: int, 
        loan_amount: float
    ) -> Dict[str, Any]:
        """
        Get detailed evaluation information
        """
        dti = (debt_amount / annual_income) * 100 if annual_income > 0 else 0
        lti = (loan_amount / annual_income) * 100 if annual_income > 0 else 0
        
        return {
            'credit_score': credit_score,
            'credit_category': self._get_credit_category(credit_score),
            'debt_amount': debt_amount,
            'annual_income': annual_income,
            'dti_ratio': round(dti, 2),
            'dti_category': self._get_dti_category(dti),
            'loan_amount': loan_amount,
            'loan_to_income_ratio': round(lti, 2),
            'employment_years': employment_years,
            'employment_stability': 'stable' if employment_years >= 3 else ('moderate' if employment_years >= 1 else 'unstable')
        }
    
    def get_system_config(self, category: str, key: str) -> Any:
        """Get system configuration value from Prolog"""
        if not self._initialized:
            return None
        
        try:
            query = f"get_config({category}, {key}, Value)."
            solutions = list(self.prolog.query(query))
            
            if solutions:
                return solutions[0].get('Value')
            return None
        except Exception as e:
            print(f"Error getting config from Prolog: {e}")
            return None
    
    def validate_system_config(self, category: str, key: str, value: Any) -> bool:
        """Validate configuration value using Prolog rules"""
        if not self._initialized:
            return True  # Fallback to valid
        
        try:
            query = f"validate_config({category}, {key}, {value})."
            solutions = list(self.prolog.query(query))
            return len(solutions) > 0
        except Exception as e:
            print(f"Error validating config with Prolog: {e}")
            return True
    
    def get_business_limits(self) -> Dict[str, Any]:
        """Get business limits from Prolog configuration"""
        if not self._initialized:
            return self._get_fallback_limits()
        
        try:
            limits = {}
            config_keys = ['min_loan_amount', 'max_loan_amount', 'min_credit_score', 'max_credit_score']
            
            for key in config_keys:
                query = f"get_config(business_config, {key}, Value)."
                solutions = list(self.prolog.query(query))
                if solutions:
                    limits[key] = solutions[0].get('Value')
                else:
                    limits[key] = self._get_fallback_limit(key)
            
            return limits
        except Exception as e:
            print(f"Error getting business limits from Prolog: {e}")
            return self._get_fallback_limits()
    
    def _get_fallback_limits(self) -> Dict[str, Any]:
        """Fallback business limits"""
        return {
            'min_loan_amount': 100,
            'max_loan_amount': 1000000,
            'min_credit_score': 300,
            'max_credit_score': 850
        }
    
    def _get_fallback_limit(self, key: str) -> Any:
        """Get fallback limit value"""
        fallback_limits = self._get_fallback_limits()
        return fallback_limits.get(key)


# Singleton instance
_prolog_engine = None

def get_prolog_engine() -> PrologEngine:
    """Get the singleton Prolog engine instance"""
    global _prolog_engine
    if _prolog_engine is None:
        _prolog_engine = PrologEngine()
def initialize_prolog(rules_path: str) -> bool:
    """Initialize the global Prolog engine"""
    global _prolog_engine
    if _prolog_engine is None:
        _prolog_engine = PrologEngine()
    return _prolog_engine.initialize(rules_path)

def evaluate_loan(
    credit_score: int, 
    debt_amount: float, 
    annual_income: float, 
    employment_years: int, 
    loan_amount: float
) -> Dict[str, Any]:
    """Evaluate loan application using Prolog"""
    global _prolog_engine
    if _prolog_engine is None:
        _prolog_engine = PrologEngine()
        _prolog_engine.initialize('')
    return _prolog_engine.evaluate_loan(
        credit_score, debt_amount, annual_income, employment_years, loan_amount
    )

def validate_application(
    loan_amount: float, 
    annual_income: float, 
    credit_score: int, 
    employment_years: int, 
    loan_purpose: str
) -> Dict[str, Any]:
    """Validate loan application using Prolog"""
    global _prolog_engine
    if _prolog_engine is None:
        _prolog_engine = PrologEngine()
        _prolog_engine.initialize('')
    return _prolog_engine.validate_application(
        loan_amount, annual_income, credit_score, employment_years, loan_purpose
    )

def get_system_config(category: str, key: str) -> Any:
    """Get system configuration value from Prolog"""
    global _prolog_engine
    if _prolog_engine is None:
        _prolog_engine = PrologEngine()
        _prolog_engine.initialize('')
    return _prolog_engine.get_system_config(category, key)

def validate_system_config(category: str, key: str, value: Any) -> bool:
    """Validate configuration value using Prolog rules"""
    global _prolog_engine
    if _prolog_engine is None:
        _prolog_engine = PrologEngine()
        _prolog_engine.initialize('')
    return _prolog_engine.validate_system_config(category, key, value)

def get_business_limits() -> Dict[str, Any]:
    """Get business limits from Prolog configuration"""
    global _prolog_engine
    if _prolog_engine is None:
        _prolog_engine = PrologEngine()
        _prolog_engine.initialize('')
    return _prolog_engine.get_business_limits()
