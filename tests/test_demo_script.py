"""
Test suite validating the end-to-end golden demonstration script (scripts/demo_all_pillars.py).
Ensures all 6 pillars execute seamlessly without runtime exceptions.
"""
import pytest
from scripts.demo_all_pillars import run_demo

def test_demo_all_pillars_execution(capsys):
    """Executes the complete all-pillars demonstration function and verifies stdout outputs."""
    run_demo()
    captured = capsys.readouterr()
    
    # Assert all 6 pillars executed and printed expected verification milestones
    assert "PILLAR 1: Autonomous Financial & Audit Committee" in captured.out
    assert "PILLAR 2: Multimodal Spatial Grounding" in captured.out
    assert "PILLAR 3: Sandboxed Python Code Interpreter" in captured.out
    assert "PILLAR 4: SEC EDGAR US-GAAP XBRL Connector" in captured.out
    assert "PILLAR 5: Enterprise Production DevOps" in captured.out
    assert "PILLAR 6: Merkle Tree Regulatory Audit Ledger" in captured.out
    assert "ALL 6 ADVANCED ARCHITECTURAL PILLARS VERIFIED & OPERATIONAL" in captured.out
    assert "SEC Rule 17a-4, SOC 2 Type II" in captured.out
