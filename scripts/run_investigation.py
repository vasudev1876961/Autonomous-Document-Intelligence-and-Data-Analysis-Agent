"""
Autonomous Investigation CLI:
Allows running end-to-end evidence-driven document investigations directly from the command line.
"""
import sys
import argparse
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
from rich.panel import Panel
from rich.table import Table
from rich import box

from config.settings import settings
from src.agent.orchestrator import AgentOrchestrator

def main():
    parser = argparse.ArgumentParser(description="Autonomous Document Intelligence Agent CLI")
    parser.add_argument(
        "--goal",
        type=str,
        default="Explain why revenue declined from Q1 to Q2. Identify the main contributing segments and support the explanation with evidence.",
        help="Analytical goal or investigative objective"
    )
    parser.add_argument(
        "--files",
        nargs="*",
        type=str,
        help="List of document file paths to ingest and analyze"
    )
    args = parser.parse_args()

    console = Console()
    console.print(Panel.fit(
        "[bold cyan]Autonomous Document Intelligence Agent (CLI)[/bold cyan]\n"
        "[dim]Evidence-Driven Multi-Format Reasoning & Deterministic Reporting[/dim]",
        box=box.DOUBLE
    ))

    # Resolve files
    if args.files:
        files = [Path(f) for f in args.files]
    else:
        files = [
            settings.sample_docs_dir / "Quarterly_Report.pdf",
            settings.sample_docs_dir / "Revenue_Data.xlsx",
            settings.sample_docs_dir / "Segment_Performance.csv"
        ]

    valid_files = [f for f in files if f.exists()]
    if not valid_files:
        console.print("[bold red]Error: No valid document files found.[/bold red]")
        sys.exit(1)

    console.print(f"[bold]Investigative Objective:[/bold] [italic cyan]\"{args.goal}\"[/italic cyan]\n")
    console.print(f"[bold]Ingesting {len(valid_files)} documents:[/bold]")
    for f in valid_files:
        console.print(f"  • [green]{f.name}[/green] ({f.stat().st_size:,} bytes)")

    console.print("\n[bold yellow]Launching autonomous agent execution graph...[/bold yellow]")
    orchestrator = AgentOrchestrator()

    with console.status("[bold green]Agent actively investigating, computing, and verifying...[/bold green]"):
        state = orchestrator.run_investigation(goal=args.goal, file_paths=valid_files)

    console.print("\n[bold green][SUCCESS] Autonomous Investigation Completed & Verified![/bold green]\n")

    # Metrics Summary
    p = state.period_comparison
    s = state.segment_analysis
    if p:
        summary_table = Table(title="[Metrics] Verified Financial Metrics", box=box.ROUNDED)
        summary_table.add_column("Metric", style="bold")
        summary_table.add_column("Baseline (Q1)", justify="right")
        summary_table.add_column("Comparative (Q2)", justify="right")
        summary_table.add_column("Delta (Δ)", justify="right", style="bold red" if p.absolute_change < 0 else "bold green")
        summary_table.add_column("% Change", justify="right")

        summary_table.add_row(
            p.metric_name,
            f"{p.period_1_value:,.1f} {p.unit}",
            f"{p.period_2_value:,.1f} {p.unit}",
            f"{p.absolute_change:+,.1f} {p.unit}",
            f"{p.percentage_change:+,.1f}%" if p.percentage_change else "N/A"
        )
        console.print(summary_table)

    if s:
        seg_table = Table(title="[Segments] Segment Contribution Breakdown", box=box.SIMPLE_HEAD)
        seg_table.add_column("Segment Name", style="bold")
        seg_table.add_column("Q1", justify="right")
        seg_table.add_column("Q2", justify="right")
        seg_table.add_column("Absolute Delta", justify="right")
        seg_table.add_column("% Contribution", justify="right", style="bold cyan")
        seg_table.add_column("Offsetting", justify="center")

        for seg in s.segments:
            seg_table.add_row(
                seg.segment_name,
                f"{seg.period_1_value:,.1f}",
                f"{seg.period_2_value:,.1f}",
                f"{seg.absolute_change:+,.1f}",
                f"{seg.contribution_percentage:.1f}%",
                "Yes" if seg.is_offsetting else "No"
            )
        console.print(seg_table)

    # Verification Audit
    v = state.verification_audit
    if v:
        v_badge = "[bold green]PASS[/bold green]" if v.all_checks_passed else "[bold yellow]WARNING[/bold yellow]"
        console.print(Panel(
            f"[bold]Verdict:[/bold] {v_badge} • {v.summary_verdict}\n"
            f"[dim]Checks Passed: {v.passed_checks}/{v.total_checks}[/dim]",
            title="[Audit] Independent Verification Audit"
        ))

    console.print(f"\n[bold]Exported Deliverables:[/bold]")
    if state.report_markdown_path:
        console.print(f"  • Markdown Report: [cyan]{state.report_markdown_path}[/cyan]")
    if state.report_pdf_path:
        console.print(f"  • PDF Report: [cyan]{state.report_pdf_path}[/cyan]")
    for ch in state.chart_paths:
        console.print(f"  • Visual Chart: [cyan]{ch}[/cyan]")

if __name__ == "__main__":
    main()
