"""
Provenance and Citation Tracker: Links claims, calculations, and tables to verified source origins.
"""
from typing import Optional
from pydantic import BaseModel, Field
from src.ingestion.metadata import SourceLocation, ClaimCategory

class GroundedClaim(BaseModel):
    claim_id: str
    claim_text: str
    category: ClaimCategory
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    calculation_reference: Optional[str] = None
    citations: list[str] = Field(default_factory=list)
    verification_status: str = "pending" # "verified", "unverified", "discrepancy"
    uncertainty_notes: Optional[str] = None

class ProvenanceManager:
    def __init__(self):
        self.claims: dict[str, GroundedClaim] = {}

    def register_claim(
        self,
        claim_id: str,
        text: str,
        category: ClaimCategory,
        evidence_ids: list[str],
        citations: list[str],
        calc_ref: Optional[str] = None,
        verification_status: str = "verified",
        notes: Optional[str] = None
    ) -> GroundedClaim:
        claim = GroundedClaim(
            claim_id=claim_id,
            claim_text=text,
            category=category,
            supporting_evidence_ids=evidence_ids,
            calculation_reference=calc_ref,
            citations=citations,
            verification_status=verification_status,
            uncertainty_notes=notes
        )
        self.claims[claim_id] = claim
        return claim

    def get_verified_claims(self) -> list[GroundedClaim]:
        return [c for c in self.claims.values() if c.verification_status == "verified"]

    def get_unresolved_uncertainties(self) -> list[GroundedClaim]:
        return [c for c in self.claims.values() if c.verification_status != "verified" or c.uncertainty_notes]
