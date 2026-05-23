import os
import pytest
from prolog_engine import initialize_prolog, evaluate_loan

ROOT = os.path.dirname(__file__) or '.'
RULES_PATH = os.path.join(os.path.dirname(__file__), '..', 'rules.pl')
RULES_PATH = os.path.abspath(RULES_PATH)


@pytest.fixture(scope='module', autouse=True)
def init_prolog():
    # Try to initialize Prolog; if not available and degraded not set, skip tests
    try:
        ok = initialize_prolog(RULES_PATH)
        if not ok:
            if os.getenv('PROLOG_DEGRADED', 'false').lower() == 'true':
                pytest.skip('Prolog not available; running in degraded mode')
            else:
                pytest.skip('Prolog not available; set PROLOG_DEGRADED=true to allow degraded mode')
    except Exception:
        if os.getenv('PROLOG_DEGRADED', 'false').lower() == 'true':
            pytest.skip('Prolog initialization failed; running in degraded mode')
        else:
            pytest.skip('Prolog initialization failed; set PROLOG_DEGRADED=true to allow degraded mode')


def test_high_credit_low_dti_approved():
    # High credit score, low DTI
    res = evaluate_loan(780, 5000, 120000, 5, 10000)
    assert res['result'] in ('approved', 'conditional')


def test_medium_credit_conditional_or_approved():
    res = evaluate_loan(680, 10000, 80000, 3, 15000)
    assert res['result'] in ('approved', 'conditional')


def test_low_credit_rejected():
    res = evaluate_loan(580, 30000, 40000, 0, 20000)
    assert res['result'] == 'rejected'
