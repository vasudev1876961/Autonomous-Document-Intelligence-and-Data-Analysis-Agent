"""
Cross-Document Reconciliation Engine:
Identifies discrepancies and conflicts between overlapping figures across multiple sources.
"""
from typing import Optional
from pydantic import BaseModel, Field
from src.ingestion.metadata import SourceLocation

class SourceClaim(BaseModel):
    metric_name: str
    period: str
    reported_value: float
    unit: str
    source_location: SourceLocation
    document_name: str

class DiscrepancyRecord(BaseModel):
    metric_name: str
    period: str
    claim_a: SourceClaim
    claim_b: SourceClaim
    absolute_difference: float
    percentage_difference: float
    is_material: bool
    requires_human_review: bool
    reconciliation_notes: str

class ReconciliationSummary(BaseModel):
    total_comparisons: int
    matched_count: int
    discrepancy_count: int
    material_conflicts: list[DiscrepancyRecord]
    has_blocking_conflicts: bool

class SourceReconciliationEngine:
    def __init__(self, material_threshold_pct: float = 1.0):
        self.material_threshold_pct = material_threshold_pct

    def reconcile_claims(self, claims: list[SourceClaim]) -> ReconciliationSummary:
        """
        Compares all pairwise claims matching the same metric and reporting period.
        Flags material differences (e.g. >1%) for Human-in-the-Loop review.
        """
        # Group by (metric_name.lower(), period.lower())
        grouped: dict[tuple[str, str], list[SourceClaim]] = {}
        for c in claims:
            key = (c.metric_name.strip().lower(), c.period.strip().lower())
            grouped.setdefault(key, []).append(c)

        total_comparisons = 0
        matched_count = 0
        conflicts: list[DiscrepancyRecord] = []

        for (metric, period), claim_list in grouped.items():
            if len(claim_list) < 2:
                continue

            for i in range(len(claim_list)):
                for j in range(i + 1, len(claim_list)):
                    total_comparisons += 1
                    c1 = claim_list[i]
                    c2 = claim_list[j]

                    abs_diff = round(abs(c1.reported_value - c2.reported_value), 4)
                    base = max(abs(c1.reported_value), abs(c2.reported_value))
                    pct_diff = round((abs_diff / base * 100.0), 2) if base > 0 else 0.0

                    if abs_diff == 0:
                        matched_count += 1
                    else:
                        is_mat = pct_diff >= self.material_threshold_pct
                        notes = (
                            f"Source '{c1.document_name}' reports {c1.reported_value} {c1.unit}, whereas "
                            f"'{c2.document_name}' reports {c2.reported_value} {c2.unit} (diff: {abs_diff}, {pct_diff}%)."
                        )
                        conflicts.append(
                            DiscrepancyRecord(
                                metric_name=c1.metric_name,
                                period=c1.period,
                                claim_a=c1,
                                claim_b=c2,
                                absolute_difference=abs_diff,
                                percentage_difference=pct_diff,
                                is_material=is_mat,
                                requires_human_review=is_mat,
                                reconciliation_notes=notes
                            )
                        )

        has_blocking = any(c.is_material for c in conflicts)
        return ReconciliationSummary(
            total_comparisons=total_comparisons,
            matched_count=matched_count,
            discrepancy_count=len(conflicts),
            material_conflicts=conflicts,
            has_blocking_conflicts=has_blocking
        )
