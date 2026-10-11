"""
Data quality, missing value detection, and anomaly screening tools.
"""
from typing import Any
import pandas as pd
import numpy as np
from pydantic import BaseModel, Field

class DataQualityReport(BaseModel):
    total_records: int
    missing_value_counts: dict[str, int]
    duplicate_record_count: int
    detected_outliers: dict[str, list[float]]
    data_type_summary: dict[str, str]
    quality_score: float # 0 to 100

class DataQualityChecker:
    @staticmethod
    def audit_dataframe(df: pd.DataFrame) -> DataQualityReport:
        total = len(df)
        if total == 0:
            return DataQualityReport(
                total_records=0,
                missing_value_counts={},
                duplicate_record_count=0,
                detected_outliers={},
                data_type_summary={},
                quality_score=100.0
            )

        # Missing counts
        missing = {col: int(df[col].isna().sum()) for col in df.columns}
        
        # Duplicates
        dup_count = int(df.duplicated().sum())
        
        # Outlier screening (IQR method on numeric columns)
        outliers: dict[str, list[float]] = {}
        for col in df.select_dtypes(include=[np.number]).columns:
            series = df[col].dropna()
            if len(series) >= 4:
                q25, q75 = np.percentile(series, 25), np.percentile(series, 75)
                iqr = q75 - q25
                lower_bound = q25 - 1.5 * iqr
                upper_bound = q75 + 1.5 * iqr
                col_outliers = series[(series < lower_bound) | (series > upper_bound)].tolist()
                if col_outliers:
                    outliers[col] = [round(float(x), 4) for x in col_outliers]

        # Types
        dtypes = {col: str(df[col].dtype) for col in df.columns}

        # Quality score
        total_cells = total * len(df.columns)
        missing_cells = sum(missing.values())
        completeness = ((total_cells - missing_cells) / total_cells) if total_cells > 0 else 1.0
        dup_penalty = (dup_count / total) if total > 0 else 0.0
        score = max(0.0, round((completeness - 0.2 * dup_penalty) * 100.0, 1))

        return DataQualityReport(
            total_records=total,
            missing_value_counts=missing,
            duplicate_record_count=dup_count,
            detected_outliers=outliers,
            data_type_summary=dtypes,
            quality_score=score
        )
