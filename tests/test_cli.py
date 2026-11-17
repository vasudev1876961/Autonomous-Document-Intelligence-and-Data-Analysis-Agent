"""
Unit tests for CLI commands.
"""
from pathlib import Path
import json
import pytest
from cli import (
    cmd_status,
    cmd_benchmark,
    cmd_scenario,
    cmd_debate,
    cmd_forensic,
    cmd_dupont,
    cmd_ratios,
    cmd_verify_pack,
)

class MockArgs:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

def test_cli_status(capsys):
    args = MockArgs()
    cmd_status(args)
    captured = capsys.readouterr()
    assert "AUTONOMOUS DOCUMENT INTELLIGENCE" in captured.out

def test_cli_forensic_numbers(capsys):
    numbers = [100, 150, 200, 250, 300, 400, 500, 600, 700, 800, 900, 1000]
    args = MockArgs(file=None, numbers=numbers, second_digit=False, first_two_digits=False)
    cmd_forensic(args)
    captured = capsys.readouterr()
    assert "FORENSIC ACCOUNTING & BENFORD'S LAW AUDIT" in captured.out
    assert "Sample Size" in captured.out

def test_cli_forensic_second_digit(capsys):
    numbers = [105, 115, 125, 135, 145, 155, 165, 175, 185, 195, 205, 215]
    args = MockArgs(file=None, numbers=numbers, second_digit=True, first_two_digits=False)
    cmd_forensic(args)
    captured = capsys.readouterr()
    assert "FORENSIC ACCOUNTING & BENFORD'S LAW AUDIT" in captured.out
    assert "Digit Distribution (0..9)" in captured.out

def test_cli_forensic_first_two_digits(capsys):
    numbers = [
        105, 115, 125, 135, 145, 155, 165, 175, 185, 195,
        205, 215, 225, 235, 245, 255, 265, 275, 285, 295, 310
    ]
    args = MockArgs(file=None, numbers=numbers, second_digit=False, first_two_digits=True)
    cmd_forensic(args)
    captured = capsys.readouterr()
    assert "FORENSIC ACCOUNTING & BENFORD'S LAW AUDIT" in captured.out
    assert "Digit Distribution (10..99)" in captured.out

def test_cli_dupont(capsys):
    args = MockArgs(ni=150.0, rev=1000.0, assets=2000.0, equity=500.0)
    cmd_dupont(args)
    captured = capsys.readouterr()
    assert "3-STAGE DUPONT ROE DECOMPOSITION & PROOF" in captured.out
    assert "MATHEMATICALLY PROVEN" in captured.out
    assert "30.00%" in captured.out

def test_cli_ratios(capsys):
    args = MockArgs(
        rev=1200.0, cogs=720.0, ebit=240.0, ni=180.0,
        ca=600.0, cl=300.0, inventory=0.0, debt=400.0, equity=800.0, assets=1500.0
    )
    cmd_ratios(args)
    captured = capsys.readouterr()
    assert "COMPREHENSIVE CORPORATE FINANCIAL RATIOS" in captured.out
    assert "Operating Margin" in captured.out
    assert "Current Ratio" in captured.out

def test_cli_verify_pack(tmp_path: Path, capsys):
    from src.tools.report_export import ReportExporter
    from pydantic import BaseModel

    class MiniState(BaseModel):
        task_id: str = "task_cli_test"
        user_goal: str = "Audit pack test"

    exporter = ReportExporter(output_dir=tmp_path)
    pack_file = exporter.export_audit_pack(MiniState(), filename="cli_pack.json")

    args = MockArgs(file=str(pack_file))
    cmd_verify_pack(args)
    captured = capsys.readouterr()
    assert "CRYPTOGRAPHIC AUDIT PACK INTEGRITY VERIFIER" in captured.out
    assert "VERIFIED_TAMPER_FREE" in captured.out

def test_cli_scenario(capsys):
    args = MockArgs(p1=1000.0, p2=900.0, target=1000.0)
    cmd_scenario(args)
    captured = capsys.readouterr()
    assert "DETERMINISTIC SCENARIO & RISK SIMULATION" in captured.out
    assert "Monte Carlo" in captured.out

def test_cli_debate(capsys):
    args = MockArgs(goal="Explain why revenue declined from Q1 to Q2.")
    cmd_debate(args)
    captured = capsys.readouterr()
    assert "MULTI-AGENT RED-TEAM DEBATE COUNCIL" in captured.out
    assert "COUNCIL VERDICT" in captured.out

def test_cli_committee(capsys):
    from cli import cmd_committee
    args = MockArgs(
        goal="Audit corporate financials and return on equity.",
        p1=1000.0,
        p2=900.0,
        disagreement_threshold=0.15,
        dupont=True,
        ni=120.0,
        assets=1500.0,
        equity=800.0
    )
    cmd_committee(args)
    captured = capsys.readouterr()
    assert "AUTONOMOUS FINANCIAL & AUDIT COMMITTEE" in captured.out
    assert "5-Agent Adversarial Swarm Consensus Protocol" in captured.out
    assert "CHIEF RISK OFFICER CONSENSUS ADJUDICATION" in captured.out
    assert "Consensus Reached:" in captured.out

def test_cli_ground(capsys):
    from cli import cmd_ground
    args = MockArgs(
        file=None,
        page=1,
        bbox="50,50,300,100",
        text=None
    )
    cmd_ground(args)
    captured = capsys.readouterr()
    assert "MULTIMODAL SPATIAL VISUAL GROUNDING" in captured.out
    assert "Grounding Snippet:" in captured.out
    assert "Page Dimensions:" in captured.out

def test_cli_dcf(capsys):
    from cli import cmd_dcf
    args = MockArgs(
        fcf="100,115,130,145,160",
        wacc=0.09,
        growth=0.025,
        debt=0.0,
        shares=1.0
    )
    cmd_dcf(args)
    captured = capsys.readouterr()
    assert "DISCOUNTED CASH FLOW (DCF) & SENSITIVITY VALUATION" in captured.out
    assert "Implied Enterprise Value:" in captured.out
    assert "2D SENSITIVITY MATRIX" in captured.out

def test_cli_edgar(capsys):
    from cli import cmd_edgar
    args = MockArgs(
        ticker="MSFT",
        year=2024,
        form="10-K"
    )
    cmd_edgar(args)
    captured = capsys.readouterr()
    assert "SEC EDGAR & XBRL CORPORATE FINANCIAL CONNECTOR" in captured.out
    assert "Microsoft Corporation" in captured.out
    assert "MACROECONOMIC BENCHMARK CONTEXT" in captured.out
    assert "10Y Treasury Benchmark Yield:" in captured.out

def test_cli_benchmark(capsys):
    args = MockArgs()
    cmd_benchmark(args)
    captured = capsys.readouterr()
    assert "RUNNING ADI-BENCH v1.0 BENCHMARK SUITE" in captured.out
    assert "EMPIRICAL METRICS COMPARISON" in captured.out
