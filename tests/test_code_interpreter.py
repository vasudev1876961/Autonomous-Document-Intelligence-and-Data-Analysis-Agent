"""
Unit and Integration Tests for Pillar 3: Sandboxed Python Code Interpreter & Financial Simulation Engine.
Tests AST static security filtering, isolated execution, DCF 2D sensitivity,
10,000-path stochastic Monte Carlo VaR & CVaR risk bounds, and REST APIs.
"""
import pytest
from src.tools.code_interpreter import (
    SandboxedFinancialInterpreter,
    SecurityASTValidator,
    DCFValuationResult,
    MonteCarloVaRResult,
    CodeExecutionResult
)


def test_security_ast_validator_blocks_unsafe_imports():
    """Tests that AST screening blocks malicious and dangerous module imports."""
    unsafe_code = """
import os
os.system("dir")
"""
    res = SandboxedFinancialInterpreter.execute_code(unsafe_code)
    assert res.success is False
    assert "Import of forbidden module 'os' is prohibited in sandbox." in res.stderr
    assert res.security_violation is not None


def test_security_ast_validator_blocks_unsafe_calls():
    """Tests that execution of eval(), exec(), and open() is blocked."""
    unsafe_eval = "x = eval('2 + 2')"
    res = SandboxedFinancialInterpreter.execute_code(unsafe_eval)
    assert res.success is False
    assert "Execution of unsafe builtin 'eval()' is prohibited." in res.stderr

    unsafe_open = "f = open('secret.txt', 'r')"
    res2 = SandboxedFinancialInterpreter.execute_code(unsafe_open)
    assert res2.success is False
    assert "Execution of unsafe builtin 'open()' is prohibited." in res2.stderr


def test_safe_sandboxed_code_execution():
    """Tests executing clean financial calculation code in isolated namespace."""
    safe_code = """
import numpy as np
revenues = [100.0, 120.0, 140.0, 170.0]
growth = [(revenues[i] - revenues[i-1])/revenues[i-1] for i in range(1, len(revenues))]
mean_growth = float(np.mean(growth))
print(f"Mean Growth: {mean_growth*100:.1f}%")
result = round(mean_growth * 100.0, 2)
"""
    res = SandboxedFinancialInterpreter.execute_code(safe_code)
    assert res.success is True
    assert "Mean Growth:" in res.stdout
    assert res.return_value == 19.37
    assert "mean_growth" in res.exported_variables
    assert res.execution_time_ms > 0


def test_dcf_valuation_and_sensitivity():
    """Tests multi-period DCF valuation and 2D WACC vs Terminal Growth sensitivity matrix."""
    fcfs = [100.0, 115.0, 130.0, 145.0, 160.0]
    res = SandboxedFinancialInterpreter.run_dcf_valuation(
        free_cash_flows=fcfs,
        wacc=0.09,
        terminal_growth=0.025,
        net_debt=200.0,
        shares_outstanding=10.0
    )

    assert isinstance(res, DCFValuationResult)
    assert res.discount_rate_wacc_pct == 9.0
    assert res.terminal_growth_rate_pct == 2.5
    assert res.discounted_fcf_sum > 400.0
    assert res.terminal_value > 2000.0
    assert res.enterprise_value > 2000.0
    assert res.equity_value == round(res.enterprise_value - 200.0, 2)
    assert res.implied_share_price == round(res.equity_value / 10.0, 2)

    # Verify 2D Sensitivity matrix
    assert len(res.sensitivity_matrix_wacc_vs_growth) == 5  # 5 WACC points
    row_9 = next(r for r in res.sensitivity_matrix_wacc_vs_growth if r["wacc_pct"] == 9.0)
    assert row_9["g_2.5%"] == res.implied_share_price


def test_monte_carlo_var_10000_paths():
    """Tests 10,000-path stochastic Monte Carlo simulation with 95% and 99% VaR and CVaR."""
    res = SandboxedFinancialInterpreter.run_monte_carlo_var(
        initial_value=1000.0,
        volatility=0.08,
        drift=0.02,
        periods=4,
        num_paths=10000,
        seed=42
    )

    assert isinstance(res, MonteCarloVaRResult)
    assert res.num_paths == 10000
    assert res.initial_value == 1000.0
    assert res.mean_terminal_value > 950.0
    assert res.p5_worst_case < res.p50_median < res.p95_best_case
    assert res.var_95_pct > 0.0
    assert res.var_99_pct >= res.var_95_pct  # 99% VaR is more conservative than 95%
    assert res.cvar_95_pct >= res.var_95_pct  # Expected shortfall >= VaR
    assert "p1" in res.percentiles and "p99" in res.percentiles


def test_api_interpreter_endpoints():
    """Tests REST API endpoints for Sandboxed Python Interpreter, DCF, and Monte Carlo VaR."""
    from fastapi.testclient import TestClient
    from src.api.server import app

    client = TestClient(app)

    # 1. Code execution
    res1 = client.post("/api/v1/interpreter/execute", json={
        "code": "result = 42 * 2\nprint('Computed!')"
    })
    assert res1.status_code == 200
    d1 = res1.json()
    assert d1["success"] is True
    assert d1["return_value"] == 84
    assert "Computed!" in d1["stdout"]

    # 2. DCF Valuation
    res2 = client.post("/api/v1/interpreter/dcf", json={
        "free_cash_flows": [100.0, 120.0, 140.0],
        "wacc": 0.09,
        "terminal_growth": 0.025,
        "net_debt": 50.0,
        "shares_outstanding": 5.0
    })
    assert res2.status_code == 200
    d2 = res2.json()
    assert d2["enterprise_value"] > 0
    assert len(d2["sensitivity_matrix_wacc_vs_growth"]) > 0

    # 3. Monte Carlo VaR
    res3 = client.post("/api/v1/interpreter/monte-carlo-var", json={
        "initial_value": 1000.0,
        "volatility": 0.08,
        "num_paths": 1000
    })
    assert res3.status_code == 200
    d3 = res3.json()
    assert d3["num_paths"] == 1000
    assert d3["var_95_pct"] > 0
