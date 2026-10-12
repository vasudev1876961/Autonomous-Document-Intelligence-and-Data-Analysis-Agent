"""
Automated Evaluation Benchmark CLI Runner (ADI-Bench).
Executes reference scenarios, calculates accuracy and grounding metrics,
conducts ablation studies, and exports markdown evaluation reports.
"""
import sys
import json
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from src.evaluation.benchmark_runner import BenchmarkRunner

def main():
    console = Console()
    console.print(Panel.fit(
        "[bold cyan]Autonomous Document Intelligence & Data Analysis Agent[/bold cyan]\n"
        "[dim]Evaluation Benchmark Suite & Ablation Study Runner (ADI-Bench v1.0)[/dim]",
        box=box.DOUBLE
    ))

    runner = BenchmarkRunner()
    
    with console.status("[bold green]Executing end-to-end evaluation benchmark scenarios...[/bold green]"):
        report = runner.run_all_benchmarks()

    console.print(f"\n[bold green][SUCCESS] Benchmark Execution Completed at {report.run_timestamp}[/bold green]\n")

    # 1. Scenario Results Table
    sc_table = Table(title="[Scenarios] Scenario-by-Scenario Evaluation Scores", box=box.ROUNDED, header_style="bold magenta")
    sc_table.add_column("Scenario ID", style="dim", no_wrap=True)
    sc_table.add_column("Scenario Name", style="bold")
    sc_table.add_column("TCR (Pass)", justify="center")
    sc_table.add_column("Math Acc (MA)", justify="right")
    sc_table.add_column("Citation (CGR)", justify="right")
    sc_table.add_column("Source Cov (SC)", justify="right")
    sc_table.add_column("Hallucination (HR)", justify="right")
    sc_table.add_column("Recovery (RSR)", justify="right")

    for sc in report.scenario_scores:
        tcr_badge = "[green]PASS[/green]" if sc.tcr_pass else "[red]FAIL[/red]"
        sc_table.add_row(
            sc.scenario_id,
            sc.scenario_name,
            tcr_badge,
            f"{sc.ma_score:.1f}%",
            f"{sc.cgr_score:.1f}%",
            f"{sc.sc_score:.1f}%",
            f"{sc.hr_score:.1f}%",
            f"{sc.rsr_score:.1f}%"
        )
    console.print(sc_table)

    # 2. Aggregate Metrics Table
    agg = report.aggregate_metrics
    agg_table = Table(title="[Aggregate] Aggregate System Reliability Metrics", box=box.HEAVY_EDGE, header_style="bold cyan")
    agg_table.add_column("Core Evaluation Metric", style="bold")
    agg_table.add_column("Measured Score", justify="right", style="bold yellow")
    agg_table.add_column("Target Threshold", justify="right", style="dim")
    agg_table.add_column("Verdict", justify="center")

    metrics_map = [
        ("Task Completion Rate (TCR)", f"{agg.task_completion_rate:.1f}%", ">= 90.0%", agg.task_completion_rate >= 90),
        ("Deterministic Mathematical Accuracy (MA)", f"{agg.mathematical_accuracy:.1f}%", "100.0%", agg.mathematical_accuracy == 100),
        ("Citation Grounding Rate (CGR)", f"{agg.citation_grounding_rate:.1f}%", ">= 95.0%", agg.citation_grounding_rate >= 95),
        ("Source Document Coverage (SC)", f"{agg.source_coverage:.1f}%", ">= 90.0%", agg.source_coverage >= 90),
        ("Hallucination Rate (HR)", f"{agg.hallucination_rate:.1f}%", "<= 2.0%", agg.hallucination_rate <= 2),
        ("Anomaly Recovery Success Rate (RSR)", f"{agg.recovery_success_rate:.1f}%", ">= 85.0%", agg.recovery_success_rate >= 85),
    ]

    for name, score, target, passed in metrics_map:
        v_badge = "[green]COMPLIANT[/green]" if passed else "[yellow]REVIEW[/yellow]"
        agg_table.add_row(name, score, target, v_badge)
    console.print(agg_table)

    # 3. Ablation Study Table
    abl_table = Table(title="[Ablation] Ablation Study: Autonomous Agent vs Baselines", box=box.DOUBLE_EDGE, header_style="bold green")
    abl_table.add_column("Architectural Variant", style="bold")
    abl_table.add_column("TCR", justify="right")
    abl_table.add_column("Math Acc", justify="right")
    abl_table.add_column("Citation Grd", justify="right")
    abl_table.add_column("Source Cov", justify="right")
    abl_table.add_column("Hallucination", justify="right")
    abl_table.add_column("Recovery (RSR)", justify="right")

    for ab in report.ablation_results:
        is_full = "Proposed" in ab.system_variant
        variant_label = f"[bold green]{ab.system_variant}[/bold green]" if is_full else ab.system_variant
        abl_table.add_row(
            variant_label,
            f"{ab.task_completion_rate:.1f}%",
            f"{ab.mathematical_accuracy:.1f}%",
            f"{ab.citation_grounding_rate:.1f}%",
            f"{ab.source_coverage:.1f}%",
            f"{ab.hallucination_rate:.1f}%",
            f"{ab.recovery_success_rate:.1f}%"
        )
    console.print(abl_table)

    # Export Report to Disk
    eval_dir = ROOT_DIR / "data" / "evaluation"
    eval_dir.mkdir(parents=True, exist_ok=True)

    json_path = eval_dir / "benchmark_report.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report.model_dump(), f, indent=2)

    md_path = eval_dir / "benchmark_report.md"
    md_content = f"""# Autonomous Document Intelligence Benchmark Report
**Benchmark Suite:** {report.benchmark_name}  
**Execution Timestamp:** `{report.run_timestamp}`  
**Average Latency:** {agg.average_latency_seconds:.2f}s  

---

## 1. Aggregate System Performance Metrics

| Core Evaluation Metric | Measured Score | Standard Requirement | Target Met |
|---|---|---|---|
| **Task Completion Rate (TCR)** | **{agg.task_completion_rate:.1f}%** | ≥ 90.0% | {'✅ YES' if agg.task_completion_rate >= 90 else '⚠️ NO'} |
| **Mathematical Accuracy (MA)** | **{agg.mathematical_accuracy:.1f}%** | 100.0% | {'✅ YES' if agg.mathematical_accuracy == 100 else '⚠️ NO'} |
| **Citation Grounding Rate (CGR)** | **{agg.citation_grounding_rate:.1f}%** | ≥ 95.0% | {'✅ YES' if agg.citation_grounding_rate >= 95 else '⚠️ NO'} |
| **Source Coverage (SC)** | **{agg.source_coverage:.1f}%** | ≥ 90.0% | {'✅ YES' if agg.source_coverage >= 90 else '⚠️ NO'} |
| **Hallucination Rate (HR)** | **{agg.hallucination_rate:.1f}%** | ≤ 2.0% | {'✅ YES' if agg.hallucination_rate <= 2 else '⚠️ NO'} |
| **Anomaly Recovery Success Rate (RSR)** | **{agg.recovery_success_rate:.1f}%** | ≥ 85.0% | {'✅ YES' if agg.recovery_success_rate >= 85 else '⚠️ NO'} |

---

## 2. Scenario-by-Scenario Evaluation Ledger

| Scenario ID | Name | TCR | Math Acc | Citation Grd | Source Cov | Hallucination | Recovery |
|---|---|---|---|---|---|---|---|
"""
    for sc in report.scenario_scores:
        md_content += f"| `{sc.scenario_id}` | {sc.scenario_name} | {'PASS' if sc.tcr_pass else 'FAIL'} | {sc.ma_score:.1f}% | {sc.cgr_score:.1f}% | {sc.sc_score:.1f}% | {sc.hr_score:.1f}% | {sc.rsr_score:.1f}% |\n"

    md_content += """
---

## 3. Ablation Study: Proposed Agent vs Baselines

| Architectural Variant | TCR | Math Acc (MA) | Citation Grd (CGR) | Source Cov (SC) | Hallucination (HR) | Recovery (RSR) |
|---|---|---|---|---|---|---|
"""
    for ab in report.ablation_results:
        md_content += f"| **{ab.system_variant}** | {ab.task_completion_rate:.1f}% | {ab.mathematical_accuracy:.1f}% | {ab.citation_grounding_rate:.1f}% | {ab.source_coverage:.1f}% | {ab.hallucination_rate:.1f}% | {ab.recovery_success_rate:.1f}% |\n"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    console.print(f"\n[bold green]Report exported successfully to:[/bold green]")
    console.print(f"- [cyan]{json_path}[/cyan]")
    console.print(f"- [cyan]{md_path}[/cyan]\n")

if __name__ == "__main__":
    main()
