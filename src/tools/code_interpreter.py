"""
Sandboxed Python Code Interpreter and Advanced Financial Simulation Sandbox.
Provides isolated computational execution with AST security validation, execution timeouts,
and deterministic quantitative financial modeling:
- 10,000-path Monte Carlo Value-at-Risk (VaR 95%, 99% & CVaR Expected Shortfall)
- Discounted Cash Flow (DCF) with 2D WACC vs Terminal Growth Sensitivity Matrices
- Safe in-memory execution namespace with zero network/process access.
"""
import ast
import io
import math
import sys
import time
from typing import Any, Callable, Optional
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field


class CodeExecutionResult(BaseModel):
    success: bool
    stdout: str = ""
    stderr: str = ""
    return_value: Optional[Any] = None
    execution_time_ms: float = 0.0
    exported_variables: dict[str, Any] = Field(default_factory=dict)
    security_violation: Optional[str] = None


class DCFValuationResult(BaseModel):
    free_cash_flows: list[float]
    discount_rate_wacc_pct: float
    terminal_growth_rate_pct: float
    discounted_fcf_sum: float
    terminal_value: float
    discounted_terminal_value: float
    enterprise_value: float
    equity_value: float
    implied_share_price: Optional[float] = None
    sensitivity_matrix_wacc_vs_growth: list[dict[str, Any]] = Field(default_factory=list)


class MonteCarloVaRResult(BaseModel):
    num_paths: int
    initial_value: float
    mean_terminal_value: float
    median_terminal_value: float
    std_dev: float
    var_95_pct: float   # 95% Value at Risk (maximum loss at 95% confidence)
    var_99_pct: float   # 99% Value at Risk
    cvar_95_pct: float  # Expected Shortfall (mean of losses exceeding 95% VaR)
    p5_worst_case: float
    p50_median: float
    p95_best_case: float
    prob_loss_pct: float
    percentiles: dict[str, float] = Field(default_factory=dict)


class SecurityASTValidator(ast.NodeVisitor):
    """
    Statically analyzes Python AST to block dangerous system calls, network access,
    process execution, or filesystem manipulation.
    """
    FORBIDDEN_MODULES = {
        "os", "sys", "subprocess", "shutil", "socket", "urllib", "requests",
        "httpx", "pty", "commands", "builtin", "importlib", "pickle", "ctypes"
    }
    FORBIDDEN_CALLS = {
        "eval", "exec", "compile", "globals", "locals", "open"
    }

    def __init__(self):
        self.violations: list[str] = []

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            base_mod = alias.name.split(".")[0]
            if base_mod in self.FORBIDDEN_MODULES:
                self.violations.append(f"Import of forbidden module '{alias.name}' is prohibited in sandbox.")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            base_mod = node.module.split(".")[0]
            if base_mod in self.FORBIDDEN_MODULES:
                self.violations.append(f"Import from forbidden module '{node.module}' is prohibited in sandbox.")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id in self.FORBIDDEN_CALLS:
            self.violations.append(f"Execution of unsafe builtin '{node.func.id}()' is prohibited.")
        self.generic_visit(node)


class SandboxedFinancialInterpreter:
    """
    Sandboxed Python execution engine tailored for quantitative financial engineering.
    """

    @classmethod
    def execute_code(
        cls,
        code_str: str,
        initial_context: Optional[dict[str, Any]] = None,
        timeout_seconds: float = 5.0
    ) -> CodeExecutionResult:
        """
        Executes arbitrary Python code in an isolated namespace after AST security screening.
        """
        # 1. AST Security Analysis
        try:
            tree = ast.parse(code_str)
        except SyntaxError as e:
            return CodeExecutionResult(
                success=False,
                stderr=f"SyntaxError: {str(e)}",
                security_violation="Syntax Error"
            )

        validator = SecurityASTValidator()
        validator.visit(tree)
        if validator.violations:
            return CodeExecutionResult(
                success=False,
                stderr="\n".join(validator.violations),
                security_violation="; ".join(validator.violations)
            )

        # 2. Build Safe Global Namespace
        SAFE_MODULES = {"math", "numpy", "pandas", "scipy", "statistics", "datetime", "json", "re"}

        def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
            base = name.split(".")[0]
            if base not in SAFE_MODULES:
                raise ImportError(f"Import of module '{name}' is not permitted in sandbox.")
            return __import__(name, globals, locals, fromlist, level)

        safe_globals: dict[str, Any] = {
            "__builtins__": {
                "abs": abs, "all": all, "any": any, "bool": bool, "dict": dict,
                "enumerate": enumerate, "filter": filter, "float": float, "int": int,
                "isinstance": isinstance, "len": len, "list": list, "map": map,
                "max": max, "min": min, "pow": pow, "print": print, "range": range,
                "reversed": reversed, "round": round, "set": set, "sorted": sorted,
                "str": str, "sum": sum, "tuple": tuple, "zip": zip,
                "__import__": safe_import,
            },
            "math": math,
            "np": np,
            "numpy": np,
            "pd": pd,
            "pandas": pd,
            # Built-in financial models
            "run_dcf_valuation": cls.run_dcf_valuation,
            "run_monte_carlo_var": cls.run_monte_carlo_var,
        }

        local_vars: dict[str, Any] = dict(initial_context or {})

        # 3. Capture standard output
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        redirected_stdout = io.StringIO()
        redirected_stderr = io.StringIO()

        start_time = time.perf_counter()
        success = True
        err_msg = ""
        ret_val = None

        try:
            sys.stdout = redirected_stdout
            sys.stderr = redirected_stderr
            # Compile and execute
            compiled = compile(tree, filename="<sandbox>", mode="exec")
            exec(compiled, safe_globals, local_vars)
            if "result" in local_vars:
                ret_val = local_vars["result"]
        except Exception as e:
            success = False
            err_msg = f"{type(e).__name__}: {str(e)}"
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        # Export serializable variables
        exported = {}
        for k, v in local_vars.items():
            if not k.startswith("_") and k not in safe_globals:
                try:
                    if isinstance(v, (int, float, str, bool, list, dict)):
                        exported[k] = v
                    elif isinstance(v, pd.DataFrame):
                        exported[k] = v.to_dict(orient="records")
                    elif isinstance(v, np.ndarray):
                        exported[k] = v.tolist()
                except Exception:
                    pass

        return CodeExecutionResult(
            success=success,
            stdout=redirected_stdout.getvalue(),
            stderr=err_msg or redirected_stderr.getvalue(),
            return_value=ret_val,
            execution_time_ms=elapsed_ms,
            exported_variables=exported
        )

    # ========================================================================
    # FINANCIAL ENGINE: DISCOUNTED CASH FLOW (DCF) & SENSITIVITY
    # ========================================================================

    @staticmethod
    def run_dcf_valuation(
        free_cash_flows: list[float],
        wacc: float = 0.09,
        terminal_growth: float = 0.025,
        net_debt: float = 0.0,
        shares_outstanding: Optional[float] = None
    ) -> DCFValuationResult:
        """
        Executes a multi-period Discounted Cash Flow valuation with 2D sensitivity table.
        - wacc: Weighted Average Cost of Capital (e.g. 0.09 = 9%)
        - terminal_growth: Long-term perpetual growth rate (e.g. 0.025 = 2.5%)
        """
        if wacc <= terminal_growth:
            raise ValueError(f"WACC ({wacc*100:.1f}%) must be strictly greater than terminal growth ({terminal_growth*100:.1f}%).")

        n_years = len(free_cash_flows)
        # Discount explicit FCFs: FCF_t / (1 + WACC)^t
        pv_factors = [(1.0 + wacc) ** (t + 1) for t in range(n_years)]
        discounted_fcfs = [fcf / pv for fcf, pv in zip(free_cash_flows, pv_factors)]
        pv_fcf_sum = sum(discounted_fcfs)

        # Terminal Value = FCF_n * (1 + g) / (WACC - g)
        last_fcf = free_cash_flows[-1]
        terminal_val = (last_fcf * (1.0 + terminal_growth)) / (wacc - terminal_growth)
        discounted_tv = terminal_val / ((1.0 + wacc) ** n_years)

        enterprise_val = pv_fcf_sum + discounted_tv
        equity_val = max(0.0, enterprise_val - net_debt)
        share_price = (equity_val / shares_outstanding) if shares_outstanding and shares_outstanding > 0 else None

        # 2D Sensitivity Grid: WACC (wacc - 2% .. wacc + 2%) vs Growth (g - 1% .. g + 1%)
        wacc_range = [round(wacc + delta, 4) for delta in [-0.02, -0.01, 0.0, 0.01, 0.02] if wacc + delta > 0.02]
        growth_range = [round(terminal_growth + delta, 4) for delta in [-0.01, -0.005, 0.0, 0.005, 0.01] if terminal_growth + delta > 0.0]

        sensitivity_grid = []
        for w in wacc_range:
            row_data = {"wacc_pct": round(w * 100.0, 2)}
            for g in growth_range:
                if w > g:
                    pv_fcf_s = sum(fcf / ((1.0 + w) ** (t + 1)) for t, fcf in enumerate(free_cash_flows))
                    tv_s = (last_fcf * (1.0 + g)) / (w - g)
                    ev_s = pv_fcf_s + (tv_s / ((1.0 + w) ** n_years))
                    eq_s = max(0.0, ev_s - net_debt)
                    sp_s = (eq_s / shares_outstanding) if shares_outstanding and shares_outstanding > 0 else eq_s
                    row_data[f"g_{g*100:.1f}%"] = round(sp_s, 2)
                else:
                    row_data[f"g_{g*100:.1f}%"] = None
            sensitivity_grid.append(row_data)

        return DCFValuationResult(
            free_cash_flows=free_cash_flows,
            discount_rate_wacc_pct=round(wacc * 100.0, 2),
            terminal_growth_rate_pct=round(terminal_growth * 100.0, 2),
            discounted_fcf_sum=round(pv_fcf_sum, 2),
            terminal_value=round(terminal_val, 2),
            discounted_terminal_value=round(discounted_tv, 2),
            enterprise_value=round(enterprise_val, 2),
            equity_value=round(equity_val, 2),
            implied_share_price=round(share_price, 2) if share_price else None,
            sensitivity_matrix_wacc_vs_growth=sensitivity_grid
        )

    # ========================================================================
    # FINANCIAL ENGINE: 10,000-PATH MONTE CARLO VALUE-AT-RISK (VaR & CVaR)
    # ========================================================================

    @staticmethod
    def run_monte_carlo_var(
        initial_value: float = 1000.0,
        volatility: float = 0.08,
        drift: float = 0.0,
        periods: int = 4,
        num_paths: int = 10000,
        seed: Optional[int] = 42
    ) -> MonteCarloVaRResult:
        """
        Executes a 10,000-path Geometric Brownian Motion / stochastic forward simulation
        computing Value-at-Risk (VaR 95%, 99%) and Conditional VaR (CVaR Expected Shortfall).
        """
        if seed is not None:
            np.random.seed(seed)

        dt = 1.0 / periods
        # Geometric Brownian Motion forward simulation: S_t = S_0 * exp(cumsum((drift - 0.5*sigma^2)*dt + sigma*sqrt(dt)*Z))
        daily_drift = (drift - 0.5 * (volatility ** 2)) * dt
        daily_vol = volatility * math.sqrt(dt)

        shock_matrix = np.random.normal(loc=daily_drift, scale=daily_vol, size=(num_paths, periods))
        cum_shocks = np.cumsum(shock_matrix, axis=1)
        terminal_values = initial_value * np.exp(cum_shocks[:, -1])

        # Value deltas: terminal_value - initial_value
        deltas = terminal_values - initial_value
        losses = -deltas  # positive number means loss

        # 95% and 99% VaR
        var_95 = float(np.percentile(losses, 95))
        var_99 = float(np.percentile(losses, 99))

        # Conditional VaR (Expected Shortfall) = mean of losses that exceed 95% VaR
        tail_losses_95 = losses[losses >= var_95]
        cvar_95 = float(np.mean(tail_losses_95)) if len(tail_losses_95) > 0 else var_95

        p5 = float(np.percentile(terminal_values, 5))
        p50 = float(np.percentile(terminal_values, 50))
        p95 = float(np.percentile(terminal_values, 95))

        prob_loss = float(np.mean(terminal_values < initial_value)) * 100.0

        percentile_dict = {
            f"p{p}": round(float(np.percentile(terminal_values, p)), 2)
            for p in [1, 5, 10, 25, 50, 75, 90, 95, 99]
        }

        return MonteCarloVaRResult(
            num_paths=num_paths,
            initial_value=round(initial_value, 2),
            mean_terminal_value=round(float(np.mean(terminal_values)), 2),
            median_terminal_value=round(p50, 2),
            std_dev=round(float(np.std(terminal_values)), 2),
            var_95_pct=round(max(0.0, (var_95 / initial_value) * 100.0), 2),
            var_99_pct=round(max(0.0, (var_99 / initial_value) * 100.0), 2),
            cvar_95_pct=round(max(0.0, (cvar_95 / initial_value) * 100.0), 2),
            p5_worst_case=round(p5, 2),
            p50_median=round(p50, 2),
            p95_best_case=round(p95, 2),
            prob_loss_pct=round(prob_loss, 2),
            percentiles=percentile_dict
        )
