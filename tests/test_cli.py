"""
Unit tests for CLI commands.
"""
import pytest
from cli import cmd_status, cmd_benchmark, cmd_scenario, cmd_debate, cmd_forensic

class MockArgs:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

def test_cli_status(capsys):
    args = MockArgs()
    cmd_status(args)
    captured = capsys.readouterr()
    assert "AUTONOMOUS DOCUMENT INTELLIGENCE" in captured.out
    assert "Enterprise Edition v4.0" in captured.out

def test_cli_forensic_numbers(capsys):
    numbers = [100, 150, 200, 250, 300, 400, 500, 600, 700, 800, 900, 1000]
    args = MockArgs(file=None, numbers=numbers)
    cmd_forensic(args)
    captured = capsys.readouterr()
    assert "FORENSIC ACCOUNTING & BENFORD'S LAW AUDIT" in captured.out
    assert "Sample Size" in captured.out

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

def test_cli_benchmark(capsys):
    args = MockArgs()
    cmd_benchmark(args)
    captured = capsys.readouterr()
    assert "RUNNING ADI-BENCH v1.0 BENCHMARK SUITE" in captured.out
    assert "EMPIRICAL METRICS COMPARISON" in captured.out
