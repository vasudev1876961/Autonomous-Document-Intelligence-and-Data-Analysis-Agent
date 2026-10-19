"""
Forensic Accounting and Benford's Law Anomaly Detection Engine.
Audits financial statements, invoice tables, expense reports, and numerical document claims
for statistical conformity, potential manipulation, and reporting irregularities.
"""
import math
from typing import Any, Optional
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field

class BenfordDigitComparison(BaseModel):
    digit: int
    observed_count: int
    observed_frequency: float
    expected_frequency: float
    frequency_difference: float
    z_score: float

class BenfordAnalysisResult(BaseModel):
    sample_size: int
    chi_square_stat: float
    p_value_approx: float
    mean_absolute_deviation: float  # MAD
    conformity_status: str          # "Close Conformity", "Acceptable Conformity", "Marginally Acceptable", "Non-Conforming"
    is_suspicious: bool
    digit_distributions: list[BenfordDigitComparison]
    interpretation: str

class NumberAnomaly(BaseModel):
    value: float
    context: str
    anomaly_type: str  # "z_score", "iqr_outlier", "digit_violation", "threshold_cluster"
    severity: str      # "low", "medium", "high"
    explanation: str

class ForensicAuditReport(BaseModel):
    total_numbers_audited: int
    benford_first_digit: Optional[BenfordAnalysisResult] = None
    anomalies_detected: list[NumberAnomaly] = Field(default_factory=list)
    repeated_values_count: int = 0
    round_numbers_percentage: float = 0.0
    overall_risk_score: float = 0.0  # 0.0 (pristine) to 1.0 (critical suspicion)
    audit_summary: str = ""

class ForensicAuditor:
    """
    Forensic Auditing Engine for document data integrity verification.
    """

    # Theoretical Benford distribution for leading digits 1..9
    BENFORD_P1 = {d: math.log10(1.0 + 1.0 / d) for d in range(1, 10)}

    @staticmethod
    def extract_leading_digit(val: float | int) -> Optional[int]:
        """Extracts the first non-zero leading digit of a number."""
        try:
            num = abs(float(val))
            if num == 0 or math.isnan(num) or math.isinf(num):
                return None
            s = f"{num:.10e}".split("e")[0].replace(".", "").lstrip("0")
            if s:
                return int(s[0])
            return None
        except Exception:
            return None

    @classmethod
    def test_benford_first_digit(cls, numbers: list[float | int]) -> BenfordAnalysisResult:
        """
        Executes Benford's Law First-Digit Analysis across a sequence of numbers.
        Applies Nigrini's Mean Absolute Deviation (MAD) and Pearson Chi-Square test.
        """
        valid_digits: list[int] = []
        for n in numbers:
            d = cls.extract_leading_digit(n)
            if d is not None and 1 <= d <= 9:
                valid_digits.append(d)

        N = len(valid_digits)
        if N < 10:
            # Insufficient sample for statistical significance
            return BenfordAnalysisResult(
                sample_size=N,
                chi_square_stat=0.0,
                p_value_approx=1.0,
                mean_absolute_deviation=0.0,
                conformity_status="Insufficient Data (N < 10)",
                is_suspicious=False,
                digit_distributions=[],
                interpretation="Dataset size is too small to reliably establish Benford compliance."
            )

        # Count frequencies
        counts = {d: 0 for d in range(1, 10)}
        for d in valid_digits:
            counts[d] += 1

        digit_comparisons: list[BenfordDigitComparison] = []
        chi_square = 0.0
        mad_sum = 0.0

        for d in range(1, 10):
            obs_cnt = counts[d]
            obs_freq = obs_cnt / N
            exp_freq = cls.BENFORD_P1[d]
            exp_cnt = N * exp_freq

            diff = obs_freq - exp_freq
            mad_sum += abs(diff)

            # Chi-square component
            if exp_cnt > 0:
                chi_square += ((obs_cnt - exp_cnt) ** 2) / exp_cnt

            # Binomial z-score per digit: (p_obs - p_exp) / sqrt(p_exp * (1 - p_exp) / N)
            variance = (exp_freq * (1.0 - exp_freq)) / N
            std_err = math.sqrt(variance) if variance > 0 else 1e-6
            z_score = round(diff / std_err, 3)

            digit_comparisons.append(BenfordDigitComparison(
                digit=d,
                observed_count=obs_cnt,
                observed_frequency=round(obs_freq, 4),
                expected_frequency=round(exp_freq, 4),
                frequency_difference=round(diff, 4),
                z_score=z_score
            ))

        mad = round(mad_sum / 9.0, 5)
        chi_square = round(chi_square, 3)

        # Approximate p-value for 8 degrees of freedom (chi-square critical val at p=0.05 is 15.51)
        # Using Wilson-Hilferty transformation approximation for chi-square df=8
        if chi_square <= 0:
            p_val = 1.0
        elif chi_square > 35.0:
            p_val = 0.0001
        elif chi_square > 20.0:
            p_val = 0.01
        elif chi_square > 15.51:
            p_val = 0.05
        else:
            p_val = 0.20

        # Nigrini (2012) MAD Conformity Thresholds for First Digit
        if mad <= 0.006:
            conformity = "Close Conformity"
            suspicious = False
        elif mad <= 0.012:
            conformity = "Acceptable Conformity"
            suspicious = False
        elif mad <= 0.015:
            conformity = "Marginally Acceptable"
            suspicious = False
        else:
            conformity = "Non-Conforming"
            suspicious = True

        if suspicious:
            interp = (
                f"Data exhibits non-conformity with Benford's Law (MAD = {mad:.4f} > 0.015, Chi-Sq = {chi_square}). "
                f"Distribution of leading digits deviates significantly from natural logarithmic patterns. "
                f"Further audit of source figures is recommended."
            )
        else:
            interp = (
                f"Data conforms to Benford's Law (MAD = {mad:.4f}, Status: {conformity}). "
                f"Leading digits reflect natural logarithmic distributions typical of unmanipulated accounting figures."
            )

        return BenfordAnalysisResult(
            sample_size=N,
            chi_square_stat=chi_square,
            p_value_approx=p_val,
            mean_absolute_deviation=mad,
            conformity_status=conformity,
            is_suspicious=suspicious,
            digit_distributions=digit_comparisons,
            interpretation=interp
        )

    @classmethod
    def audit_tabular_data(
        cls,
        df: pd.DataFrame,
        numeric_columns: Optional[list[str]] = None
    ) -> ForensicAuditReport:
        """
        Conducts an end-to-end forensic audit across all numeric columns of a dataframe.
        Evaluates Benford compliance, checks for repeated numbers and extreme statistical outliers.
        """
        if numeric_columns is None:
            numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
        else:
            numeric_cols = [c for c in numeric_columns if c in df.columns]

        all_numbers: list[float] = []
        for col in numeric_cols:
            clean_series = pd.to_numeric(df[col], errors="coerce").dropna()
            all_numbers.extend([float(v) for v in clean_series if abs(v) > 1e-4])

        if not all_numbers:
            return ForensicAuditReport(
                total_numbers_audited=0,
                audit_summary="No valid numeric columns found in dataframe for forensic audit."
            )

        # 1. Benford First-Digit Analysis
        benford_res = cls.test_benford_first_digit(all_numbers)

        # 2. Outlier and Anomaly Detection
        anomalies: list[NumberAnomaly] = []
        arr = np.array(all_numbers)
        mean_val = float(np.mean(arr))
        std_val = float(np.std(arr))

        q25, q75 = np.percentile(arr, [25, 75])
        iqr = q75 - q25
        lower_bound = q25 - 1.5 * iqr
        upper_bound = q75 + 1.5 * iqr

        for val in all_numbers:
            # Z-score outlier test
            if std_val > 0:
                z = abs(val - mean_val) / std_val
                if z >= 3.0:
                    anomalies.append(NumberAnomaly(
                        value=round(val, 2),
                        context="Aggregate series",
                        anomaly_type="z_score",
                        severity="high",
                        explanation=f"Extreme statistical outlier (Z-score = {z:.2f} >= 3.0)."
                    ))

            # IQR outlier test
            if val < lower_bound or val > upper_bound:
                anomalies.append(NumberAnomaly(
                    value=round(val, 2),
                    context="Aggregate series",
                    anomaly_type="iqr_outlier",
                    severity="medium",
                    explanation=f"Value falls outside IQR Tukey fence [{lower_bound:.2f}, {upper_bound:.2f}]."
                ))

        # Deduplicate anomalies by value
        seen_vals = set()
        unique_anomalies = []
        for an in anomalies:
            if an.value not in seen_vals:
                seen_vals.add(an.value)
                unique_anomalies.append(an)

        # 3. Repeated Values & Rounding Check
        total_cnt = len(all_numbers)
        unique_cnt = len(set(all_numbers))
        repeated_cnt = total_cnt - unique_cnt

        round_cnt = sum(1 for v in all_numbers if abs(v) >= 10 and v == round(v, -1))
        round_pct = round((round_cnt / total_cnt) * 100.0, 2) if total_cnt > 0 else 0.0

        # Calculate composite risk score (0.0 to 1.0)
        risk = 0.0
        if benford_res.is_suspicious:
            risk += 0.45
        elif benford_res.conformity_status == "Marginally Acceptable":
            risk += 0.20

        if len(unique_anomalies) > 0:
            risk += min(0.30, len(unique_anomalies) * 0.05)

        if round_pct > 60.0:
            risk += 0.25
        elif round_pct > 40.0:
            risk += 0.15

        risk_score = round(min(1.0, risk), 2)

        summary_lines = [
            f"Audited {total_cnt} values across {len(numeric_cols)} numeric columns.",
            f"Benford Test: {benford_res.conformity_status} (MAD: {benford_res.mean_absolute_deviation:.4f}, Chi-Sq: {benford_res.chi_square_stat}).",
            f"Detected {len(unique_anomalies)} statistical anomalies.",
            f"Round Numbers: {round_pct}% of values. Repeated occurrences: {repeated_cnt}.",
            f"Composite Forensic Risk Index: {risk_score:.2f} ({'ELEVATED RISK' if risk_score >= 0.5 else 'LOW RISK'})."
        ]

        return ForensicAuditReport(
            total_numbers_audited=total_cnt,
            benford_first_digit=benford_res,
            anomalies_detected=unique_anomalies,
            repeated_values_count=repeated_cnt,
            round_numbers_percentage=round_pct,
            overall_risk_score=risk_score,
            audit_summary=" ".join(summary_lines)
        )
