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
% Main Evaluation Rules
%=====================================================================

% Rule 1: High credit score with excellent DTI - APPROVED
evaluate_loan(CreditScore, DTI, EmploymentYears, LoanAmount, AnnualIncome, Result, Explanation, Confidence) :-
    credit_category(CreditScore, high),
    dti_category(DTI, excellent),
    employment_stability(EmploymentYears, stable),
    !,
    Result = approved,
    Explanation = 'Excellent credit score combined with low debt-to-income ratio and stable employment indicates very low risk. Loan is approved.',
    Confidence = 95.0.

% Rule 2: High credit score with good DTI - APPROVED
evaluate_loan(CreditScore, DTI, EmploymentYears, LoanAmount, AnnualIncome, Result, Explanation, Confidence) :-
    credit_category(CreditScore, high),
    dti_category(DTI, good),
    loan_to_income_ratio(LoanAmount, AnnualIncome, LTI),
    LTI < 30,
    !,
    Result = approved,
    Explanation = 'Strong credit history and manageable debt levels. The loan amount is reasonable relative to income. Approved.',
    Confidence = 90.0.

% Rule 3: High credit score with moderate DTI - CONDITIONAL
evaluate_loan(CreditScore, DTI, EmploymentYears, LoanAmount, AnnualIncome, Result, Explanation, Confidence) :-
    credit_category(CreditScore, high),
    dti_category(DTI, moderate),
    !,
    Result = conditional,
    Explanation = 'Good credit score but debt-to-income ratio is slightly elevated. Loan approved with conditions such as additional documentation or co-signer.',
    Confidence = 75.0.

% Rule 4: Medium credit with excellent DTI - APPROVED
evaluate_loan(CreditScore, DTI, EmploymentYears, LoanAmount, AnnualIncome, Result, Explanation, Confidence) :-
    credit_category(CreditScore, medium),
    dti_category(DTI, excellent),
    employment_stability(EmploymentYears, stable),
    !,
    Result = approved,
    Explanation = 'Good credit history with excellent debt management. Stable employment supports the loan approval.',
    Confidence = 85.0.

% Rule 5: Medium credit with good DTI - APPROVED
evaluate_loan(CreditScore, DTI, EmploymentYears, LoanAmount, AnnualIncome, Result, Explanation, Confidence) :-
    credit_category(CreditScore, medium),
    dti_category(DTI, good),
    loan_to_income_ratio(LoanAmount, AnnualIncome, LTI),
    LTI < 25,
    !,
    Result = approved,
    Explanation = 'Acceptable credit score with manageable debt levels. Loan approved.',
    Confidence = 80.0.

% Rule 6: Medium credit with moderate DTI - CONDITIONAL
evaluate_loan(CreditScore, DTI, EmploymentYears, LoanAmount, AnnualIncome, Result, Explanation, Confidence) :-
    credit_category(CreditScore, medium),
    dti_category(DTI, moderate),
    !,
    Result = conditional,
    Explanation = 'Average credit score combined with elevated debt levels requires additional review. Consider reducing loan amount or improving debt situation.',
    Confidence = 65.0.

% Rule 7: Medium credit with poor DTI - REJECTED
evaluate_loan(CreditScore, DTI, EmploymentYears, LoanAmount, AnnualIncome, Result, Explanation, Confidence) :-
    credit_category(CreditScore, medium),
    dti_category(DTI, poor),
    !,
    Result = rejected,
    Explanation = 'Debt-to-income ratio is too high relative to credit history. Recommend improving debt management before reapplying.',
    Confidence = 80.0.

% Rule 8: Low credit with excellent DTI - CONDITIONAL
evaluate_loan(CreditScore, DTI, EmploymentYears, LoanAmount, AnnualIncome, Result, Explanation, Confidence) :-
    credit_category(CreditScore, low),
    dti_category(DTI, excellent),
    employment_stability(EmploymentYears, stable),
    !,
    Result = conditional,
    Explanation = 'Despite low credit score, excellent debt management and stable employment may compensate. Additional documentation required.',
    Confidence = 55.0.

% Rule 9: Low credit with good DTI - REJECTED
evaluate_loan(CreditScore, DTI, EmploymentYears, LoanAmount, AnnualIncome, Result, Explanation, Confidence) :-
    credit_category(CreditScore, low),
    dti_category(DTI, good),
    !,
    Result = rejected,
    Explanation = 'Credit history concerns outweigh positive debt levels. Recommend improving credit score before applying.',
    Confidence = 75.0.

% Rule 10: Low credit with moderate or poor DTI - REJECTED
evaluate_loan(CreditScore, DTI, EmploymentYears, LoanAmount, AnnualIncome, Result, Explanation, Confidence) :-
    credit_category(CreditScore, low),
    !,
    Result = rejected,
    Explanation = 'Low credit score combined with high debt levels presents unacceptable risk. Application rejected.',
    Confidence = 90.0.

% Rule 11: Very high loan to income - REJECTED
evaluate_loan(CreditScore, DTI, EmploymentYears, LoanAmount, AnnualIncome, Result, Explanation, Confidence) :-
    loan_to_income_ratio(LoanAmount, AnnualIncome, LTI),
    LTI > 40,
    !,
    Result = rejected,
    Explanation = 'Loan amount exceeds reasonable limits relative to income. Consider applying for a smaller loan amount.',
    Confidence = 85.0.

% Rule 12: No employment history - REJECTED
evaluate_loan(CreditScore, DTI, 0, LoanAmount, AnnualIncome, Result, Explanation, Confidence) :-
    !,
    Result = rejected,
    Explanation = 'Employment history is required for loan approval. Please provide proof of employment.',
    Confidence = 95.0.

% Rule 13: New employment - CONDITIONAL
evaluate_loan(CreditScore, DTI, EmploymentYears, LoanAmount, AnnualIncome, Result, Explanation, Confidence) :-
    EmploymentYears < 1,
    credit_category(CreditScore, high),
    dti_category(DTI, good),
    !,
    Result = conditional,
    Explanation = 'Limited employment history requires additional verification. Co-signer may be required.',
    Confidence = 60.0.

% Default rule - REJECTED
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
