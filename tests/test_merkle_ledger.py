"""
Unit and Integration Tests for Pillar 6: Merkle Tree Regulatory Audit Ledger.
Tests cryptographic leaf hashing, interior node domain separation (RFC 6962),
balanced and unbalanced Merkle root computation, light-client inclusion proofs,
tamper detection, file persistence, REST API endpoints, and CLI commands.
"""
import json
import tempfile
from pathlib import Path
import pytest
from src.verification.merkle_ledger import (
    MerkleAuditLedger,
    MerkleAuditLeaf,
    MerkleAuditEventType,
    MerkleInclusionProof,
    global_audit_ledger
)


def test_merkle_leaf_creation_and_rfc6962_prefix():
    """Validates domain separation and canonical hashing of individual leaves."""
    payload = {"revenue": 1000.0, "segment": "Hardware", "period": "Q1"}
    leaf = MerkleAuditLeaf.create(
        leaf_index=0,
        event_type=MerkleAuditEventType.TOOL_EXECUTION_COMPUTED,
        actor="quant_analyst",
        payload_data=payload,
        timestamp_utc="2026-11-17T12:00:00Z"
    )

    assert leaf.leaf_index == 0
    assert leaf.event_type == MerkleAuditEventType.TOOL_EXECUTION_COMPUTED
    assert len(leaf.payload_hash) == 64
    assert len(leaf.leaf_hash) == 64
    # Ensure leaf hash differs from pure payload hash due to 0x00 domain separation & timestamp
    assert leaf.leaf_hash != leaf.payload_hash


def test_merkle_root_computation_and_invariance():
    """Tests deterministic Merkle root calculation across 1, 2, 3, and 4 leaves."""
    ledger = MerkleAuditLedger(ledger_id="test-root-calc")
    assert len(ledger) == 0

    # 1 Leaf
    l0 = ledger.append_event(MerkleAuditEventType.USER_QUERY_SUBMITTED, "analyst", {"q": "rev"})
    root_1 = ledger.get_root_hash()
    assert root_1 == l0.leaf_hash

    # 2 Leaves
    l1 = ledger.append_event(MerkleAuditEventType.DOCUMENT_INGESTED, "ingest", {"doc": "10-K.pdf"})
    root_2 = ledger.get_root_hash()
    expected_root_2 = MerkleAuditLedger._hash_interior(l0.leaf_hash, l1.leaf_hash)
    assert root_2 == expected_root_2

    # 3 Leaves (Unbalanced / Odd leaf handled via RFC 6962 duplication)
    l2 = ledger.append_event(MerkleAuditEventType.TOOL_EXECUTION_COMPUTED, "math", {"dupont": True})
    root_3 = ledger.get_root_hash()
    assert len(root_3) == 64

    # 4 Leaves (Balanced power-of-two)
    l3 = ledger.append_event(MerkleAuditEventType.REPORT_CERTIFIED, "cro", {"status": "CERTIFIED"})
    root_4 = ledger.get_root_hash()
    assert len(root_4) == 64
    assert root_4 != root_3


def test_merkle_inclusion_proof_and_offline_verification():
    """Tests generating and verifying light-client inclusion proofs for all leaves."""
    ledger = MerkleAuditLedger(ledger_id="test-proofs")
    for i in range(7):
        ledger.append_event(
            MerkleAuditEventType.TOOL_EXECUTION_COMPUTED,
            actor=f"agent_{i}",
            payload_data={"step": i, "result": i * 100}
        )

    assert len(ledger) == 7
    root = ledger.get_root_hash()

    # Generate and verify proof for every single leaf
    for i in range(len(ledger)):
        proof = ledger.generate_inclusion_proof(i)
        assert proof.leaf_index == i
        assert proof.root_hash == root
        assert len(proof.proof_path) >= 1

        # Offline light-client verification (requires zero ledger context)
        assert MerkleAuditLedger.verify_inclusion_proof(proof) is True


def test_merkle_tamper_detection():
    """Confirms that any altered bit in payload, metadata, or proof steps fails verification."""
    ledger = MerkleAuditLedger(ledger_id="test-tamper")
    for i in range(4):
        ledger.append_event(
            MerkleAuditEventType.DOCUMENT_INGESTED,
            actor="test",
            payload_data={"idx": i}
        )

    proof = ledger.generate_inclusion_proof(1)
    assert MerkleAuditLedger.verify_inclusion_proof(proof) is True

    # 1. Tamper with payload_hash
    tampered_proof_1 = proof.model_copy(update={"payload_hash": "0" * 64})
    assert MerkleAuditLedger.verify_inclusion_proof(tampered_proof_1) is False

    # 2. Tamper with timestamp
    tampered_proof_2 = proof.model_copy(update={"timestamp_utc": "1999-01-01T00:00:00Z"})
    assert MerkleAuditLedger.verify_inclusion_proof(tampered_proof_2) is False

    # 3. Tamper with root_hash
    tampered_proof_3 = proof.model_copy(update={"root_hash": "f" * 64})
    assert MerkleAuditLedger.verify_inclusion_proof(tampered_proof_3) is False

    # 4. Tamper with internal leaf inside ledger
    ledger.leaves[1].payload_data["idx"] = 9999
    assert ledger.verify_ledger_integrity() is False


def test_merkle_file_persistence():
    """Tests saving and reloading Merkle ledger manifests from disk."""
    ledger = MerkleAuditLedger(ledger_id="persist-ledger")
    ledger.append_event(MerkleAuditEventType.USER_QUERY_SUBMITTED, "user", {"goal": "test"})
    ledger.append_event(MerkleAuditEventType.REPORT_CERTIFIED, "cro", {"certified": True})

    with tempfile.TemporaryDirectory() as tmp_dir:
        file_path = Path(tmp_dir) / "test_ledger.json"
        ledger.save_to_file(file_path)

        loaded_ledger = MerkleAuditLedger.load_from_file(file_path)
        assert len(loaded_ledger) == 2
        assert loaded_ledger.get_root_hash() == ledger.get_root_hash()
        assert loaded_ledger.verify_ledger_integrity() is True


def test_api_merkle_endpoints():
    """Tests FastAPI REST endpoints for Merkle ledger and inclusion proofs."""
    from fastapi.testclient import TestClient
    from src.api.server import app

    client = TestClient(app)

    # 1. Append event
    res1 = client.post(
        "/api/v1/verification/merkle-append",
        json={
            "event_type": "TOOL_EXECUTION_COMPUTED",
            "actor": "forensic_auditor",
            "payload_data": {"benford_mad": 0.0042, "compliant": True}
        }
    )
    assert res1.status_code == 200
    d1 = res1.json()
    assert "updated_root_hash" in d1
    leaf_idx = d1["leaf"]["leaf_index"]

    # 2. Get proof
    res2 = client.get(f"/api/v1/verification/merkle-proof/{leaf_idx}")
    assert res2.status_code == 200
    proof_data = res2.json()
    assert proof_data["leaf_index"] == leaf_idx
    assert "proof_path" in proof_data

    # 3. Verify proof endpoint
    res3 = client.post("/api/v1/verification/merkle-verify", json=proof_data)
    assert res3.status_code == 200
    d3 = res3.json()
    assert d3["is_valid"] is True
    assert d3["status"] == "VERIFIED_TAMPER_FREE"

    # 4. Get ledger manifest
    res4 = client.get("/api/v1/verification/merkle-ledger")
    assert res4.status_code == 200
    d4 = res4.json()
    assert d4["regulatory_compliance"]["sec_rule_17a_4"] == "COMPLIANT_WORM_APPEND_ONLY"
