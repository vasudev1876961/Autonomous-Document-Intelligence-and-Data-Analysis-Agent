"""
Unit tests for Cryptographic Audit Pack Signing and Tamper Verification.
"""
import json
import pytest
from pathlib import Path
from pydantic import BaseModel
from src.tools.report_export import ReportExporter

class MockDoc(BaseModel):
    document_id: str = "doc_123"
    file_name: str = "Quarterly_Report.pdf"
    file_type: str = "pdf"
    file_size_bytes: int = 1024
    content_hash: str = "a1b2c3d4"
    extraction_status: str = "success"

class MockState(BaseModel):
    task_id: str = "task_test_crypto"
    user_goal: str = "Verify cryptographic integrity"
    is_completed: bool = True
    document_manifest: list[MockDoc] = [MockDoc()]
    period_comparison: None = None
    segment_analysis: None = None
    verification_audit: None = None
    observed_facts: list[str] = ["Fact 1: Revenue was 1000"]
    supported_interpretations: list[str] = ["Interpretation: Demand declined"]
    unresolved_questions: list[str] = []

def test_export_and_verify_audit_pack_clean(tmp_path: Path):
    exporter = ReportExporter(output_dir=tmp_path)
    state = MockState()

    pack_file = exporter.export_audit_pack(state, filename="test_pack.json")
    assert pack_file.exists()

    # Verify integrity of untampered file
    res = ReportExporter.verify_audit_pack_integrity(pack_file)
    assert res["is_valid"] is True
    assert res["status"] == "VERIFIED_TAMPER_FREE"
    assert res["task_id"] == "task_test_crypto"
    assert res["expected_sha256"] == res["recomputed_sha256"]

def test_verify_audit_pack_tampered(tmp_path: Path):
    exporter = ReportExporter(output_dir=tmp_path)
    state = MockState()

    pack_file = exporter.export_audit_pack(state, filename="test_pack_tamper.json")
    
    # Intentionally tamper with the file contents
    with open(pack_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Maliciously alter a fact
    data["epistemic_findings"]["observed_facts"][0] = "ALTERED: Revenue was 99999"

    with open(pack_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    # Verify integrity of tampered file
    res = ReportExporter.verify_audit_pack_integrity(pack_file)
    assert res["is_valid"] is False
    assert res["status"] == "TAMPER_DETECTED"
    assert res["expected_sha256"] != res["recomputed_sha256"]

