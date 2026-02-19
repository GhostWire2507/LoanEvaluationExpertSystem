%=====================================================================
% System Configuration and Management - Prolog Rules
% This file contains system-wide configuration and business logic
%=====================================================================

%=====================================================================
% System Configuration
%=====================================================================

% Database configuration
database_config(database_file, 'loan_system.db').
database_config(track_modifications, false).
database_config(echo, false).

% Session configuration
session_config(permanent, false).
session_config(lifetime_hours, 24).

% Application configuration
app_config(debug, true).
app_config(default_port, 5000).
app_config(secret_key, 'change-this-in-production').

% Prolog configuration
prolog_config(executable, 'swipl').
prolog_config(rules_file, 'rules.pl').
prolog_config(config_file, 'system_config.pl').

% Business configuration
business_config(min_loan_amount, 100).
business_config(max_loan_amount, 1000000).
business_config(min_credit_score, 300).
business_config(max_credit_score, 850).
business_config(min_annual_income, 1000).
business_config(max_annual_income, 10000000).

% Risk assessment weights
risk_weight(credit_score, excellent, 5).
risk_weight(credit_score, good, 10).
risk_weight(credit_score, fair, 20).
risk_weight(credit_score, poor, 40).

risk_weight(dti, excellent, 5).
risk_weight(dti, good, 10).
risk_weight(dti, fair, 25).
risk_weight(dti, poor, 50).

risk_weight(employment, stable, 5).
risk_weight(employment, moderate, 15).
risk_weight(employment, unstable, 30).

risk_weight(loan_to_income, low, 5).
risk_weight(loan_to_income, moderate, 15).
risk_weight(loan_to_income, high, 25).
risk_weight(loan_to_income, excessive, 40).

%=====================================================================
% System Management Rules
%=====================================================================

% Get configuration value
get_config(Category, Key, Value) :-
    call(Category, Key, Value).

% Validate configuration
validate_config(Category, Key, Value) :-
    call(Category, Key, Value),
    validate_config_value(Category, Key, Value).

% Configuration validation rules
validate_config_value(business_config, min_loan_amount, Value) :-
    number(Value),
    Value > 0,
    Value < 1000000.

validate_config_value(business_config, max_loan_amount, Value) :-
    number(Value),
    Value > 1000,
    Value =< 10000000.

validate_config_value(business_config, min_credit_score, Value) :-
    number(Value),
    Value >= 300,
    Value =< 850.

validate_config_value(business_config, max_credit_score, Value) :-
    number(Value),
    Value >= 300,
    Value =< 850.

validate_config_value(risk_weight, _, Value) :-
    number(Value),
    Value >= 0,
    Value =< 100.

%=====================================================================
% User Management Rules
%=====================================================================

% User validation
validate_username(Username) :-
    atom(Username),
    atom_length(Username, Length),
    Length >= 3,
    Length =< 50.

validate_email(Email) :-
    atom(Email),
    sub_atom(Email, _, 1, _, '@'),
    sub_atom(Email, _, 1, _, '.'),
    atom_length(Email, Length),
    Length >= 5,
    Length =< 100.

validate_password(Password) :-
    atom(Password),
    atom_length(Password, Length),
    Length >= 6,
    Length =< 128.

% User roles
user_role(admin).
user_role(user).
user_role(lender).
user_role(analyst).

% Role permissions
role_permission(admin, all).
role_permission(user, apply_loan).
role_permission(user, view_own_applications).
role_permission(lender, review_applications).
role_permission(analyst, view_analytics).

% Check if user has permission
has_permission(Role, Permission) :-
    role_permission(Role, Permission).
has_permission(admin, _). % Admin has all permissions

%=====================================================================
% Application State Management
%=====================================================================

% Application status
application_status(draft).
application_status(submitted).
application_status(under_review).
application_status(approved).
application_status(rejected).
application_status(cancelled).

% Status transitions
status_transition(draft, submitted).
status_transition(submitted, under_review).
status_transition(under_review, approved).
status_transition(under_review, rejected).
status_transition(approved, cancelled).
status_transition(rejected, draft).

% Check if status transition is valid
valid_status_transition(From, To) :-
    status_transition(From, To).

%=====================================================================
% Business Logic Rules
%=====================================================================

% Loan amount limits by income tier
income_loan_limit(0, 25000, 50000).
income_loan_limit(25001, 50000, 100000).
income_loan_limit(50001, 75000, 200000).
income_loan_limit(75001, 100000, 350000).
income_loan_limit(100001, 200000, 500000).
income_loan_limit(200001, 999999999, 1000000).

% Get maximum loan amount for given income
get_max_loan_amount(AnnualIncome, MaxLoan) :-
    income_loan_limit(MinIncome, MaxIncome, MaxLoan),
    AnnualIncome >= MinIncome,
    AnnualIncome =< MaxIncome,
    !.
get_max_loan_amount(_, 1000000). % Default maximum

% Check if loan amount is within limits for income
valid_loan_amount_for_income(LoanAmount, AnnualIncome) :-
    get_max_loan_amount(AnnualIncome, MaxLoan),
    LoanAmount =< MaxLoan.

% Interest rates by credit category
interest_rate(high, 3.5).
interest_rate(medium, 6.5).
interest_rate(low, 12.0).

% Get interest rate for credit score
get_interest_rate(CreditScore, Rate) :-
    credit_category(CreditScore, Category),
    interest_rate(Category, Rate).

% Loan terms by amount
loan_term(Amount, Term) :-
    Amount =< 50000, Term = 36.
loan_term(Amount, Term) :-
    Amount > 50000, Amount =< 200000, Term = 60.
loan_term(Amount, Term) :-
    Amount > 200000, Term = 120.

% Get loan term for amount
get_loan_term(LoanAmount, Term) :-
    loan_term(LoanAmount, Term).

%=====================================================================
% Analytics and Reporting Rules
%=====================================================================

% Calculate monthly payment
calculate_monthly_payment(Principal, AnnualRate, TermMonths, MonthlyPayment) :-
    MonthlyRate is AnnualRate / 100 / 12,
    MonthlyPayment is Principal * MonthlyRate / (1 - (1 + MonthlyRate) ** (-TermMonths)).

% Calculate total interest paid
calculate_total_interest(Principal, AnnualRate, TermMonths, TotalInterest) :-
    calculate_monthly_payment(Principal, AnnualRate, TermMonths, MonthlyPayment),
    TotalPaid is MonthlyPayment * TermMonths,
    TotalInterest is TotalPaid - Principal.

% Calculate debt-to-income ratio including new loan
calculate_new_dti(ExistingDebt, AnnualIncome, NewLoanPayment, NewDTI) :-
    AnnualDebtPayment is ExistingDebt / 12,
    MonthlyIncome is AnnualIncome / 12,
    TotalDebtPayment is AnnualDebtPayment + NewLoanPayment,
    NewDTI is (TotalDebtPayment / MonthlyIncome) * 100.

% Check if new DTI is acceptable
acceptable_new_dti(NewDTI) :-
    NewDTI =< 43.

%=====================================================================
% System Health and Monitoring
%=====================================================================

% System health checks
health_check(database) :-
    database_config(database_file, _).

health_check(prolog) :-
    prolog_config(executable, _).

health_check(rules) :-
    prolog_config(rules_file, _).

% Overall system health
system_health(Status) :-
    forall(health_check(Component), true),
    Status = healthy.
system_health(unhealthy) :-
    \+ (forall(health_check(Component), true)).

% Performance metrics
performance_metric(loan_evaluation_time, target_ms, 100).
performance_metric(validation_time, target_ms, 50).
performance_metric(database_query_time, target_ms, 200).

%=====================================================================
% Error Handling and Logging
%=====================================================================

% Error categories
error_category(validation).
error_category(business_logic).
error_category(system).
error_category(database).

% Log levels
log_level(debug).
log_level(info).
log_level(warning).
log_level(error).
log_level(critical).

% Error logging
log_error(Category, Message, Level) :-
    error_category(Category),
    log_level(Level),
    % In a real system, this would write to a log file
    format('Error [~w] ~w: ~w~n', [Level, Category, Message]).

%=====================================================================
% Integration Points
%=====================================================================

% External system connections
external_system(credit_bureau).
external_system(employment_verification).
external_system(banking_system).

% System integration status
integration_status(System, connected).
integration_status(System, disconnected).

% Check if all required systems are connected
all_systems_connected :-
    forall(external_system(System), integration_status(System, connected)).

%=====================================================================
% Utility Predicates
%=====================================================================

% Format currency
format_currency(Amount, Formatted) :-
    format(atom(Formatted), '$~2f', [Amount]).

% Format percentage
format_percentage(Value, Formatted) :-
    format(atom(Formatted), '~2f%', [Value]).

% Date calculations
days_between_dates(Date1, Date2, Days) :-
    % In a real implementation, this would use proper date libraries
    Days is 0. % Placeholder

%=====================================================================
% Export predicates
%=====================================================================

% Export main predicates for use by Python
:- export(get_config/3).
:- export(validate_config/3).
:- export(validate_username/1).
:- export(validate_email/1).
:- export(validate_password/1).
:- export(has_permission/2).
:- export(valid_status_transition/2).
:- export(get_max_loan_amount/2).
:- export(valid_loan_amount_for_income/2).
:- export(get_interest_rate/2).
:- export(get_loan_term/2).
:- export(calculate_monthly_payment/4).
:- export(calculate_total_interest/4).
:- export(calculate_new_dti/4).
:- export(acceptable_new_dti/1).
:- export(system_health/1).
:- export(log_error/3).
:- export(format_currency/2).
:- export(format_percentage/2).
