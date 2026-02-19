%=====================================================================
% Loan Evaluation Expert System - Prolog Rules
% This file contains the expert system rules for evaluating loan applications
% based on credit score, debt-to-income ratio, employment, and other factors
%=====================================================================

%=====================================================================
% Helper Rules
%=====================================================================

% Calculate Debt-to-Income ratio
calculate_dti(DebtAmount, AnnualIncome, DTI) :-
    AnnualIncome > 0,
    DTI is (DebtAmount / AnnualIncome) * 100.
calculate_dti(_, _, 0) :-
    AnnualIncome =< 0.

% Categorize credit score
credit_category(Score, high) :- Score >= 750.
credit_category(Score, medium) :- Score >= 650, Score < 750.
credit_category(Score, low) :- Score < 650.

% Categorize DTI ratio
dti_category(DTI, excellent) :- DTI < 15.
dti_category(DTI, good) :- DTI >= 15, DTI < 30.
dti_category(DTI, moderate) :- DTI >= 30, DTI < 43.
dti_category(DTI, poor) :- DTI >= 43.

% Employment stability scoring
employment_stability(Years, stable) :- Years >= 3.
employment_stability(Years, moderate) :- Years >= 1, Years < 3.
employment_stability(Years, unstable) :- Years < 1.

% Loan amount to income ratio
loan_to_income_ratio(LoanAmount, AnnualIncome, Ratio) :-
    AnnualIncome > 0,
    Ratio is (LoanAmount / AnnualIncome) * 100.

%=====================================================================
% Form Validation Rules
%=====================================================================

% Form validation predicates
validate_loan_amount(Amount, valid) :- Amount > 0.
validate_loan_amount(Amount, invalid) :- Amount =< 0.

validate_annual_income(Income, valid) :- Income > 0.
validate_annual_income(Income, invalid) :- Income =< 0.

validate_credit_score(Score, valid) :- Score >= 300, Score =< 850.
validate_credit_score(Score, invalid) :- Score < 300.
validate_credit_score(Score, invalid) :- Score > 850.

validate_employment_years(Years, valid) :- Years >= 0.
validate_employment_years(Years, invalid) :- Years < 0.

validate_loan_purpose(Purpose, valid) :- Purpose \= '', Purpose \= null.

% Comprehensive form validation
validate_application(LoanAmount, AnnualIncome, CreditScore, EmploymentYears, LoanPurpose, ValidationResult) :-
    findall(Error, (
        (validate_loan_amount(LoanAmount, invalid) -> Error = 'Loan amount must be greater than 0.'; fail),
        (validate_annual_income(AnnualIncome, invalid) -> Error = 'Annual income must be greater than 0.'; fail),
        (validate_credit_score(CreditScore, invalid) -> Error = 'Credit score must be between 300 and 850.'; fail),
        (validate_employment_years(EmploymentYears, invalid) -> Error = 'Employment years cannot be negative.'; fail),
        (validate_loan_purpose(LoanPurpose, invalid) -> Error = 'Please specify the loan purpose.'; fail)
    ), Errors),
    (length(Errors, 0) -> ValidationResult = valid ; ValidationResult = errors(Errors)).

%=====================================================================
% User Authentication Rules
%=====================================================================

% User authentication rules
authenticate_user(Username, Password, UserResult) :-
    nonvar(Username),
    nonvar(Password),
    Username \= '',
    Password \= '',
    UserResult = valid.

% User eligibility assessment
check_basic_eligibility(CreditScore, DTI, EmploymentYears, Eligibility) :-
    credit_category(CreditScore, CreditCat),
    dti_category(DTI, DTICat),
    employment_stability(EmploymentYears, EmployCat),
    (CreditCat = low, DTICat = poor -> Eligibility = ineligible ;
     CreditCat = low, DTICat = moderate, EmployCat = unstable -> Eligibility = ineligible ;
     Eligibility = eligible).

%=====================================================================
% Risk Assessment Rules
%=====================================================================

% Risk assessment factors
risk_factor(credit_score, high) :- CreditScore >= 750.
risk_factor(credit_score, medium) :- CreditScore >= 650, CreditScore < 750.
risk_factor(credit_score, low) :- CreditScore < 650.

risk_factor(dti, low) :- DTI < 15.
risk_factor(dti, medium) :- DTI >= 15, DTI < 30.
risk_factor(dti, high) :- DTI >= 30, DTI < 43.
risk_factor(dti, very_high) :- DTI >= 43.

risk_factor(employment, stable) :- Years >= 3.
risk_factor(employment, moderate) :- Years >= 1, Years < 3.
risk_factor(employment, unstable) :- Years < 1.

risk_factor(loan_to_income, acceptable) :- LTI < 30.
risk_factor(loan_to_income, high) :- LTI >= 30, LTI < 40.
risk_factor(loan_to_income, excessive) :- LTI >= 40.

% Risk factor weights
credit_score_weight(high, 10).
credit_score_weight(medium, 20).
credit_score_weight(low, 40).

dti_weight(low, 5).
dti_weight(medium, 15).
dti_weight(high, 30).
dti_weight(very_high, 50).

employment_weight(stable, 5).
employment_weight(moderate, 15).
employment_weight(unstable, 25).

lti_weight(acceptable, 5).
lti_weight(high, 20).
lti_weight(excessive, 35).

% Comprehensive risk score calculation
calculate_risk_score(CreditScore, DTI, EmploymentYears, LTI, RiskScore) :-
    risk_factor(credit_score, CreditRisk),
    risk_factor(dti, DTIRisk),
    risk_factor(employment, EmployRisk),
    risk_factor(loan_to_income, LTIRisk),
    
    credit_score_weight(CreditRisk, CreditWeight),
    dti_weight(DTIRisk, DTIWeight),
    employment_weight(EmployRisk, EmployWeight),
    lti_weight(LTIRisk, LTIWeight),
    
    RiskScore is (CreditWeight + DTIWeight + EmployWeight + LTIWeight).

% Risk level classification
risk_level(RiskScore, low) :- RiskScore =< 20.
risk_level(RiskScore, medium) :- RiskScore > 20, RiskScore =< 50.
risk_level(RiskScore, high) :- RiskScore > 50, RiskScore =< 80.
risk_level(RiskScore, very_high) :- RiskScore > 80.

%=====================================================================
% Main Evaluation Rules
%=====================================================================

% Enhanced evaluation rules with risk assessment
evaluate_loan(CreditScore, DTI, EmploymentYears, LoanAmount, AnnualIncome, Result, Explanation, Confidence) :-
    calculate_dti(DebtAmount, AnnualIncome, DTI),
    loan_to_income_ratio(LoanAmount, AnnualIncome, LTI),
    calculate_risk_score(CreditScore, DTI, EmploymentYears, LTI, RiskScore),
    
    (RiskScore =< 20 -> 
        Result = approved,
        Explanation = 'Low risk profile with strong financial indicators. Loan approved.',
        Confidence = 95.0
    ; RiskScore =< 40 ->
        Result = approved,
        Explanation = 'Acceptable risk profile with good financial standing. Loan approved.',
        Confidence = 85.0
    ; RiskScore =< 60 ->
        Result = conditional,
        Explanation = 'Moderate risk profile. Additional documentation or conditions may apply.',
        Confidence = 70.0
    ; RiskScore =< 80 ->
        Result = conditional,
        Explanation = 'Elevated risk profile. Strict conditions and additional verification required.',
        Confidence = 55.0
    ;
        Result = rejected,
        Explanation = 'High risk profile exceeds acceptable lending criteria.',
        Confidence = 90.0
    ).

% Rule 1: High credit score with excellent DTI - APPROVED
evaluate_loan(CreditScore, DTI, EmploymentYears, LoanAmount, AnnualIncome, Result, Explanation, Confidence) :-
    credit_category(CreditScore, high),
    dti_category(DTI, excellent),
    employment_stability(EmploymentYears, stable),
    !,
    Result = approved,
    Explanation = 'Excellent credit score combined with low debt-to-income ratio and stable employment indicates very low risk. Loan is approved.',
    Confidence = 95.0.

% Rule 2: High credit score with good DTI - CONDITIONAL if LTI is high
evaluate_loan(CreditScore, DTI, EmploymentYears, LoanAmount, AnnualIncome, Result, Explanation, Confidence) :-
    credit_category(CreditScore, high),
    dti_category(DTI, good),
    loan_to_income_ratio(LoanAmount, AnnualIncome, LTI),
    LTI >= 30,
    !,
    Result = conditional,
    Explanation = 'Good credit score but loan amount is high relative to income. Approved with conditions.',
    Confidence = 75.0.

% Rule 3: High credit score with good DTI and reasonable LTI - APPROVED
evaluate_loan(CreditScore, DTI, EmploymentYears, LoanAmount, AnnualIncome, Result, Explanation, Confidence) :-
    credit_category(CreditScore, high),
    dti_category(DTI, good),
    loan_to_income_ratio(LoanAmount, AnnualIncome, LTI),
    LTI < 30,
    !,
    Result = approved,
    Explanation = 'Strong credit history and manageable debt levels. The loan amount is reasonable relative to income. Approved.',
    Confidence = 90.0.

% Rule 4: High credit score with moderate DTI - CONDITIONAL
evaluate_loan(CreditScore, DTI, EmploymentYears, LoanAmount, AnnualIncome, Result, Explanation, Confidence) :-
    credit_category(CreditScore, high),
    dti_category(DTI, moderate),
    !,
    Result = conditional,
    Explanation = 'Good credit score but debt-to-income ratio is slightly elevated. Loan approved with conditions such as additional documentation or co-signer.',
    Confidence = 75.0.

% Rule 5: Medium credit score with excellent DTI and stable employment - APPROVED
evaluate_loan(CreditScore, DTI, EmploymentYears, LoanAmount, AnnualIncome, Result, Explanation, Confidence) :-
    credit_category(CreditScore, medium),
    dti_category(DTI, excellent),
    employment_stability(EmploymentYears, stable),
    !,
    Result = approved,
    Explanation = 'Good credit history with excellent debt management. Stable employment supports the loan approval.',
    Confidence = 85.0.

% Rule 6: Medium credit score with good DTI and low LTI - APPROVED
evaluate_loan(CreditScore, DTI, EmploymentYears, LoanAmount, AnnualIncome, Result, Explanation, Confidence) :-
    credit_category(CreditScore, medium),
    dti_category(DTI, good),
    loan_to_income_ratio(LoanAmount, AnnualIncome, LTI),
    LTI < 25,
    !,
    Result = approved,
    Explanation = 'Acceptable credit score with manageable debt levels. Loan approved.',
    Confidence = 80.0.

% Rule 7: Medium credit score with good DTI but higher LTI - CONDITIONAL
evaluate_loan(CreditScore, DTI, EmploymentYears, LoanAmount, AnnualIncome, Result, Explanation, Confidence) :-
    credit_category(CreditScore, medium),
    dti_category(DTI, good),
    loan_to_income_ratio(LoanAmount, AnnualIncome, LTI),
    LTI >= 25,
    !,
    Result = conditional,
    Explanation = 'Average credit score with reasonable debt levels. Additional documentation may be required.',
    Confidence = 70.0.

% Rule 8: Medium credit score with moderate DTI - CONDITIONAL
evaluate_loan(CreditScore, DTI, EmploymentYears, LoanAmount, AnnualIncome, Result, Explanation, Confidence) :-
    credit_category(CreditScore, medium),
    dti_category(DTI, moderate),
    !,
    Result = conditional,
    Explanation = 'Average credit score combined with elevated debt levels requires additional review. Consider reducing loan amount or improving debt situation.',
    Confidence = 65.0.

% Rule 9: Medium credit score with poor DTI - REJECTED
evaluate_loan(CreditScore, DTI, EmploymentYears, LoanAmount, AnnualIncome, Result, Explanation, Confidence) :-
    credit_category(CreditScore, medium),
    dti_category(DTI, poor),
    !,
    Result = rejected,
    Explanation = 'Debt-to-income ratio is too high relative to credit history. Recommend improving debt management before reapplying.',
    Confidence = 80.0.

% Rule 10: Low credit score with excellent DTI and stable employment - CONDITIONAL
evaluate_loan(CreditScore, DTI, EmploymentYears, LoanAmount, AnnualIncome, Result, Explanation, Confidence) :-
    credit_category(CreditScore, low),
    dti_category(DTI, excellent),
    employment_stability(EmploymentYears, stable),
    !,
    Result = conditional,
    Explanation = 'Despite low credit score, excellent debt management and stable employment may compensate. Additional documentation required.',
    Confidence = 55.0.

% Rule 11: Low credit score with good DTI - REJECTED
evaluate_loan(CreditScore, DTI, EmploymentYears, LoanAmount, AnnualIncome, Result, Explanation, Confidence) :-
    credit_category(CreditScore, low),
    dti_category(DTI, good),
    !,
    Result = rejected,
    Explanation = 'Credit history concerns outweigh positive debt levels. Recommend improving credit score before applying.',
    Confidence = 75.0.

% Rule 12: Low credit score with moderate DTI - REJECTED
evaluate_loan(CreditScore, DTI, EmploymentYears, LoanAmount, AnnualIncome, Result, Explanation, Confidence) :-
    credit_category(CreditScore, low),
    dti_category(DTI, moderate),
    !,
    Result = rejected,
    Explanation = 'Low credit score combined with moderate debt levels presents significant risk. Application rejected.',
    Confidence = 85.0.

% Rule 13: Low credit score with poor DTI - REJECTED
evaluate_loan(CreditScore, DTI, EmploymentYears, LoanAmount, AnnualIncome, Result, Explanation, Confidence) :-
    credit_category(CreditScore, low),
    dti_category(DTI, poor),
    !,
    Result = rejected,
    Explanation = 'Low credit score combined with high debt levels presents unacceptable risk. Application rejected.',
    Confidence = 90.0.

% Rule 14: Very high LTI for any credit profile - REJECTED
evaluate_loan(CreditScore, DTI, EmploymentYears, LoanAmount, AnnualIncome, Result, Explanation, Confidence) :-
    loan_to_income_ratio(LoanAmount, AnnualIncome, LTI),
    LTI > 40,
    !,
    Result = rejected,
    Explanation = 'Loan amount exceeds reasonable limits relative to income. Consider applying for a smaller loan amount.',
    Confidence = 85.0.

% Rule 15: New employment (less than 1 year) - CONDITIONAL
evaluate_loan(CreditScore, DTI, EmploymentYears, LoanAmount, AnnualIncome, Result, Explanation, Confidence) :-
    EmploymentYears < 1,
    credit_category(CreditScore, CreditCat),
    CreditCat \= high,
    !,
    Result = conditional,
    Explanation = 'Limited employment history requires additional verification. Co-signer may be required.',
    Confidence = 60.0.

% Rule 16: New employment with poor credit - REJECTED
evaluate_loan(CreditScore, DTI, EmploymentYears, LoanAmount, AnnualIncome, Result, Explanation, Confidence) :-
    EmploymentYears < 1,
    credit_category(CreditScore, low),
    !,
    Result = rejected,
    Explanation = 'Combination of limited employment history and low credit score presents unacceptable risk.',
    Confidence = 80.0.

% Rule 17: Catch-all for edge cases - REJECTED
evaluate_loan(CreditScore, DTI, EmploymentYears, LoanAmount, AnnualIncome, Result, Explanation, Confidence) :-
    loan_to_income_ratio(LoanAmount, AnnualIncome, LTI),
    LTI >= 45,
    !,
    Result = rejected,
    Explanation = 'Loan amount is excessive relative to income and presents unacceptable risk.',
    Confidence = 95.0.

% Rule 18: Final fallback rule - REJECTED
evaluate_loan(_, _, _, _, _, Result, Explanation, Confidence) :-
    Result = rejected,
    Explanation = 'Application does not meet minimum requirements for loan approval.',
    Confidence = 50.0.

%=====================================================================
% Query Interface
%=====================================================================

% Main evaluation predicate that can be called from Python
evaluate(CreditScore, DebtAmount, AnnualIncome, EmploymentYears, LoanAmount, Result, Explanation, Confidence) :-
    calculate_dti(DebtAmount, AnnualIncome, DTI),
    evaluate_loan(CreditScore, DTI, EmploymentYears, LoanAmount, AnnualIncome, Result, Explanation, Confidence).

% Get evaluation details
evaluation_details(CreditScore, DebtAmount, AnnualIncome, EmploymentYears, LoanAmount, Details) :-
    calculate_dti(DebtAmount, AnnualIncome, DTI),
    credit_category(CreditScore, CreditCat),
    dti_category(DTI, DtiCat),
    employment_stability(EmploymentYears, EmpStability),
    loan_to_income_ratio(LoanAmount, AnnualIncome, LTI),
    Details = [credit_category=CreditCat, dti_category=DtiCat, employment_stability=EmpStability, loan_to_income=LTI, dti=DTI].

% Additional business logic predicates
get_evaluation_summary(Result, Confidence, Summary) :-
    Result = approved,
    Confidence >= 80,
    Summary = 'Strong approval with high confidence.'.
    
get_evaluation_summary(Result, Confidence, Summary) :-
    Result = approved,
    Confidence < 80,
    Summary = 'Approved with moderate confidence.'.
    
get_evaluation_summary(Result, Confidence, Summary) :-
    Result = conditional,
    Confidence >= 65,
    Summary = 'Conditional approval - additional requirements may apply.'.
    
get_evaluation_summary(Result, Confidence, Summary) :-
    Result = conditional,
    Confidence < 65,
    Summary = 'Conditional approval with significant conditions.'.
    
get_evaluation_summary(Result, Confidence, Summary) :-
    Result = rejected,
    Summary = 'Application does not meet approval criteria.'.

% Recommendation system
recommendation(Result, RiskScore, Recommendation) :-
    Result = approved,
    RiskScore =< 30,
    Recommendation = 'Proceed with standard loan processing.'.
    
recommendation(Result, RiskScore, Recommendation) :-
    Result = conditional,
    RiskScore > 30,
    Recommendation = 'Consider requiring additional collateral or co-signer.'.
    
recommendation(Result, RiskScore, Recommendation) :-
    Result = rejected,
    Recommendation = 'Suggest credit improvement and reapplication after 6 months.'.

%=====================================================================
% Analytics Queries
%=====================================================================

% Count evaluations by result
count_results([], 0, 0, 0).
count_results([Result|Rest], Approved, Conditional, Rejected) :-
    count_results(Rest, Approved1, Conditional1, Rejected1),
    (Result = approved -> Approved is Approved1 + 1, Conditional = Conditional1, Rejected = Rejected1
    ; Result = conditional -> Conditional is Conditional1 + 1, Approved = Approved1, Rejected = Rejected1
    ; Result = rejected -> Rejected is Rejected1 + 1, Approved = Approved1, Conditional = Conditional1
    ; Approved = Approved1, Conditional = Conditional1, Rejected = Rejected1).

% Calculate approval rate
approval_rate(Results, Rate) :-
    count_results(Results, Approved, _, Total),
    Total > 0,
    Rate is (Approved / Total) * 100.

% Export main evaluation predicate
:- dynamic evaluation_result/7.
:- dynamic validation_result/2.
