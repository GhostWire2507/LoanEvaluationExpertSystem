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
        Initialize the Prolog engine with the rules file
        
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
                # Load the rules file
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
    
    def _evaluate_fallback(
        self, 
        credit_score: int, 
        debt_amount: float, 
        annual_income: float, 
        employment_years: int, 
        loan_amount: float
    ) -> Dict[str, Any]:
        """
        Fallback Python-based evaluation when Prolog is not available
        """
        # Calculate DTI
        dti = (debt_amount / annual_income) * 100 if annual_income > 0 else 100
        
        # Determine credit category
        if credit_score >= 750:
            credit_cat = 'high'
        elif credit_score >= 650:
            credit_cat = 'medium'
        else:
            credit_cat = 'low'
        
        # Determine DTI category
        if dti < 15:
            dti_cat = 'excellent'
        elif dti < 30:
            dti_cat = 'good'
        elif dti < 43:
            dti_cat = 'moderate'
        else:
            dti_cat = 'poor'
        
        # Loan to income ratio
        lti = (loan_amount / annual_income) * 100 if annual_income > 0 else 100
        
        # Evaluation logic (same as Prolog rules)
        if credit_cat == 'high' and dti_cat in ['excellent', 'good'] and employment_years >= 3:
            if dti_cat == 'excellent':
                result = 'approved'
                explanation = 'Excellent credit score combined with low debt-to-income ratio and stable employment indicates very low risk. Loan is approved.'
                confidence = 95.0
            else:
                if lti < 30:
                    result = 'approved'
                    explanation = 'Strong credit history and manageable debt levels. The loan amount is reasonable relative to income. Approved.'
                    confidence = 90.0
                else:
                    result = 'conditional'
                    explanation = 'Good credit score but loan amount is high relative to income. Approved with conditions.'
                    confidence = 75.0
        elif credit_cat == 'high' and dti_cat == 'moderate':
            result = 'conditional'
            explanation = 'Good credit score but debt-to-income ratio is slightly elevated. Loan approved with conditions such as additional documentation or co-signer.'
            confidence = 75.0
        elif credit_cat == 'medium' and dti_cat in ['excellent', 'good']:
            if dti_cat == 'excellent' and employment_years >= 3:
                result = 'approved'
                explanation = 'Good credit history with excellent debt management. Stable employment supports the loan approval.'
                confidence = 85.0
            elif dti_cat == 'good' and lti < 25:
                result = 'approved'
                explanation = 'Acceptable credit score with manageable debt levels. Loan approved.'
                confidence = 80.0
            else:
                result = 'conditional'
                explanation = 'Average credit score with reasonable debt levels. Additional documentation may be required.'
                confidence = 70.0
        elif credit_cat == 'medium' and dti_cat == 'moderate':
            result = 'conditional'
            explanation = 'Average credit score combined with elevated debt levels requires additional review. Consider reducing loan amount or improving debt situation.'
            confidence = 65.0
        elif credit_cat == 'medium' and dti_cat == 'poor':
            result = 'rejected'
            explanation = 'Debt-to-income ratio is too high relative to credit history. Recommend improving debt management before reapplying.'
            confidence = 80.0
        elif credit_cat == 'low':
            if dti_cat == 'excellent' and employment_years >= 3:
                result = 'conditional'
                explanation = 'Despite low credit score, excellent debt management and stable employment may compensate. Additional documentation required.'
                confidence = 55.0
            else:
                result = 'rejected'
                if dti_cat == 'good':
                    explanation = 'Credit history concerns outweigh positive debt levels. Recommend improving credit score before applying.'
                    confidence = 75.0
                else:
                    explanation = 'Low credit score combined with high debt levels presents unacceptable risk. Application rejected.'
                    confidence = 90.0
        elif lti > 40:
            result = 'rejected'
            explanation = 'Loan amount exceeds reasonable limits relative to income. Consider applying for a smaller loan amount.'
            confidence = 85.0
        elif employment_years < 1:
            result = 'conditional'
            explanation = 'Limited employment history requires additional verification. Co-signer may be required.'
            confidence = 60.0
        else:
            result = 'rejected'
            explanation = 'Application does not meet minimum requirements for loan approval.'
            confidence = 50.0
        
        return {
            'result': result,
            'explanation': explanation,
            'confidence': confidence,
            'dti_ratio': round(dti, 2),
            'credit_category': credit_cat,
            'dti_category': dti_cat,
            'evaluation_method': 'fallback'
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
    
    def is_initialized(self) -> bool:
        """Check if Prolog engine is initialized"""
        return self._initialized


# Singleton instance
_prolog_engine = None

def get_prolog_engine() -> PrologEngine:
    """Get the singleton Prolog engine instance"""
    global _prolog_engine
    if _prolog_engine is None:
        _prolog_engine = PrologEngine()
    return _prolog_engine


def initialize_prolog(rules_path: str) -> bool:
    """
    Initialize the Prolog engine with rules from the given path
    
    Args:
        rules_path: Path to the Prolog rules file
        
    Returns:
        True if initialization successful
    """
    engine = get_prolog_engine()
    return engine.initialize(rules_path)


def evaluate_loan(
    credit_score: int, 
    debt_amount: float, 
    annual_income: float, 
    employment_years: int, 
    loan_amount: float
) -> Dict[str, Any]:
    """
    Evaluate a loan application
    
    Args:
        credit_score: Applicant's credit score
        debt_amount: Total debt amount
        annual_income: Annual gross income
        employment_years: Years of employment
        loan_amount: Requested loan amount
        
    Returns:
        Dictionary with evaluation results
    """
    engine = get_prolog_engine()
    return engine.evaluate_loan(credit_score, debt_amount, annual_income, employment_years, loan_amount)
