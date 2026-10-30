"""
Enterprise Command-Line Interface (CLI) for Autonomous Document Intelligence & Data Analysis Agent.
Allows headless execution of investigations, forensic accounting audits, multi-agent debates,
counterfactual scenario simulations, and benchmark evaluations.
"""
import argparse
import sys
import json
from pathlib import Path
from typing import Optional

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def cmd_status(args):
    """Prints system architecture health, database statistics, and storage paths."""
    from config.settings import settings
    from src.memory.sqlite_store import SQLiteStore

    print("\n" + "=" * 65)
    print("🧠 AUTONOMOUS DOCUMENT INTELLIGENCE & DATA ANALYSIS AGENT")
    print("   Enterprise Edition v4.1 • System Health & Status")
    print("=" * 65)
    print(f"  • Base Directory:   {settings.base_dir}")
    print(f"  • SQLite Database:  {settings.db_path} (Exists: {settings.db_path.exists()})")
    print(f"  • Outputs Folder:   {settings.outputs_dir}")
    print(f"  • Sample Data Dir:  {settings.sample_docs_dir}")
    print(f"  • Execution Mode:   Deterministic Hybrid Agentic")
    print(f"  • Forensic Engine:  Benford's Law First/Second Digit + MAD")
    print(f"  • Multi-Agent Team: Quant-Alpha, Lexi-Search, Adversary-Prime, Supervisor")
    
    store = SQLiteStore(settings.db_path)
    tasks = store.list_recent_tasks(limit=5)
    print(f"  • Recorded Tasks:   {len(tasks)} recent tasks in WAL store")
    for t in tasks:
        print(f"      - [{t.get('status', 'unknown').upper()}] {t.get('task_id')}: {t.get('goal', '')[:50]}...")
    print("=" * 65 + "\n")

def cmd_investigate(args):
    """Executes an end-to-end autonomous document investigation."""
    from config.settings import settings
    from src.agent.orchestrator import AgentOrchestrator

    print("\n" + "=" * 65)
    print("🚀 INITIATING AUTONOMOUS DOCUMENT INVESTIGATION")
    print("=" * 65)

    if args.files:
        files = [Path(f) for f in args.files]
    else:
        sample_paths = [
            settings.sample_docs_dir / "Quarterly_Report.pdf",
            settings.sample_docs_dir / "Revenue_Data.xlsx",
            settings.sample_docs_dir / "Segment_Performance.csv"
        ]
        files = [p for p in sample_paths if p.exists()]

    if not files:
        print("❌ Error: No valid files provided or found in sample_docs directory.")
        sys.exit(1)

    print(f"  • Objective: {args.goal}")
    print(f"  • Documents ({len(files)}):")
    for f in files:
        print(f"      - {f.name} ({f.stat().st_size:,} bytes)")

    print("\n⚡ Orchestrating LangGraph autonomous agent workflow...")
    orchestrator = AgentOrchestrator()
    state = orchestrator.run_investigation(goal=args.goal, file_paths=files)

    print("\n✅ INVESTIGATION COMPLETE & VERIFIED")
    print("-" * 65)
    print(f"  • Task ID:             {state.task_id}")
    print(f"  • Completion Status:   {'PASSED & GROUNDED' if state.is_completed else 'FLAGGED'}")
    
    if state.period_comparison:
        p = state.period_comparison
        delta_str = f"+{p.absolute_change:,.1f}" if p.absolute_change > 0 else f"{p.absolute_change:,.1f}"
        pct_str = f" ({p.percentage_change:+.1f}%)" if p.percentage_change is not None else ""
        print(f"  • Primary Metric:      {p.metric_name} ({p.period_1_name} ➔ {p.period_2_name})")
        print(f"  • Net Performance:     {delta_str} {p.unit}{pct_str} [{p.direction.upper()}]")

    if state.segment_analysis:
        print("  • Segment Attribution Breakdown:")
        for s in state.segment_analysis.segments:
            print(f"      - {s.segment_name:<16}: {s.absolute_change:+,.1f} {state.segment_analysis.unit} ({s.contribution_percentage or 0.0:.1f}% contribution)")

    print(f"  • Observed Facts:      {len(state.observed_facts)} verified statements")
    print(f"  • Interpretations:     {len(state.supported_interpretations)} grounded findings")
    
    if state.verification_audit:
        va = state.verification_audit
        print(f"  • Math Verification:   {va.summary_verdict} ({va.passed_checks}/{va.total_checks} checks passed)")

    print("\n📄 EXPORTED DELIVERABLES:")
    print(f"  • Markdown Report:     {state.report_markdown_path}")
    print(f"  • PDF Report:          {state.report_pdf_path}")
    print(f"  • Interactive HTML:    {state.report_html_path}")
    print(f"  • JSON Audit Pack:     {state.audit_pack_json_path}")
    print("=" * 65 + "\n")

def cmd_forensic(args):
    """Executes Benford's Law and anomaly detection on a file or numeric list."""
    from src.tools.forensic_auditor import ForensicAuditor
    import pandas as pd

    print("\n" + "=" * 65)
    print("🛡️ FORENSIC ACCOUNTING & BENFORD'S LAW AUDIT")
    print("=" * 65)

    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"❌ File not found: {args.file}")
            sys.exit(1)
        
        print(f"  • Ingesting file for forensic scan: {file_path.name}")
        if file_path.suffix.lower() == ".csv":
            df = pd.read_csv(file_path)
        elif file_path.suffix.lower() in [".xlsx", ".xls"]:
            df = pd.read_excel(file_path)
        else:
            print("❌ Supported file formats for direct tabular audit: .csv, .xlsx, .xls")
            sys.exit(1)

        report = ForensicAuditor.audit_tabular_data(df)
        print(f"  • Values Audited:      {report.total_numbers_audited}")
        print(f"  • Benford 1st-Digit:   {report.benford_first_digit.conformity_status if report.benford_first_digit else 'N/A'}")
        print(f"  • Benford 2nd-Digit:   {report.benford_second_digit.conformity_status if report.benford_second_digit else 'N/A'}")
        print(f"  • Mean Abs Deviation:  {report.benford_first_digit.mean_absolute_deviation if report.benford_first_digit else 'N/A'}")
        print(f"  • Anomalies Detected:  {len(report.anomalies_detected)}")
        print(f"  • Repeated Values:     {report.repeated_values_count}")
        print(f"  • Round Numbers Pct:   {report.round_numbers_percentage}%")
        print(f"  • Composite Risk:      {report.overall_risk_score} / 1.0")
        print(f"\n  • Audit Verdict:\n    {report.audit_summary}")

    elif args.numbers:
        nums = [float(x) for x in args.numbers]
        if getattr(args, "first_two_digits", False):
            res = ForensicAuditor.test_benford_first_two_digits(nums)
            digit_range = "(10..99)"
        elif getattr(args, "second_digit", False):
            res = ForensicAuditor.test_benford_second_digit(nums)
            digit_range = "(0..9)"
        else:
            res = ForensicAuditor.test_benford_first_digit(nums)
            digit_range = "(1..9)"

        print(f"  • Sample Size:         {res.sample_size}")
        print(f"  • MAD Conformity:      {res.conformity_status} (MAD: {res.mean_absolute_deviation:.5f})")
        print(f"  • Chi-Square Stat:     {res.chi_square_stat} (p-value: {res.p_value_approx})")
        print(f"  • Suspicious Flag:     {res.is_suspicious}")
        print(f"\n  • Digit Distribution {digit_range}:")
        print("    Digit | Observed | Expected | Diff   | Z-Score")
        print("    ------+----------+----------+--------+--------")
        for d in res.digit_distributions[:25]:  # Preview first 25 bins
            print(f"      {d.digit:<3} |  {d.observed_frequency:.4f}  |  {d.expected_frequency:.4f}  | {d.frequency_difference:+.4f} | {d.z_score:+.2f}")
        if len(res.digit_distributions) > 25:
            print(f"      ... [{len(res.digit_distributions) - 25} additional digit bins omitted for display]")
    else:
        print("❌ Error: Must provide either --file or --numbers.")
        sys.exit(1)

    print("=" * 65 + "\n")

def cmd_debate(args):
    """Executes a 4-round Red-Team Multi-Agent Debate."""
    from src.agent.debate import MultiAgentDebateCouncil
    from src.tools.numerical_analysis import NumericalAnalyzer

    print("\n" + "=" * 65)
    print("⚔️ MULTI-AGENT RED-TEAM DEBATE COUNCIL")
    print("=" * 65)
    print(f"  • Debate Resolution: \"{args.goal}\"")
    print("  • Participating Specialists:")
    print("      - Quant-Alpha      (Quantitative Analyst)")
    print("      - Lexi-Search      (Grounded Retrieval Specialist)")
    print("      - Adversary-Prime  (Red-Team Discrepancy Auditor)")
    print("      - Supervisor-Chief (Executive Arbiter)")

    sample_segments = [
        {"segment": "Segment A", "p1": 500.0, "p2": 420.0},
        {"segment": "Segment B", "p1": 300.0, "p2": 280.0},
        {"segment": "Segment C", "p1": 200.0, "p2": 200.0},
    ]
    seg_summary = NumericalAnalyzer.analyze_segment_contributions("Revenue", sample_segments, "₹ lakh")
    p_res = NumericalAnalyzer.compare_periods("Revenue", 1000.0, 900.0, "Q1", "Q2", "₹ lakh")

    council = MultiAgentDebateCouncil()
    session = council.run_debate(
        goal=args.goal,
        period_res=p_res,
        seg_summary=seg_summary,
        reconciliation=None,
        evidence_chunks=[]
    )

    print(f"\n⚡ Completed {len(session.rounds)} Adversarial Turns across Council:")
    for msg in session.rounds:
        print(f"\n  [ROUND {msg.round_number}] {msg.speaker_name} ({msg.speaker_role}):")
        print(f"    \"{msg.content}\"")
        if msg.citations:
            print(f"    ↳ Citations: {', '.join(msg.citations)}")

    if session.verdict:
        print("\n🏛️ COUNCIL VERDICT & CONSENSUS RULING:")
        print(f"  • Consensus Reached:    {session.verdict.consensus_reached}")
        print(f"  • Confidence Score:     {session.verdict.confidence_score*100:.1f}%")
        print(f"  • Audit Recommendation: {session.verdict.audit_recommendation}")
        print(f"  • Requires HITL Review: {session.verdict.requires_hitl}")
    print("=" * 65 + "\n")

def cmd_scenario(args):
    """Executes counterfactual simulation and Monte Carlo risk forecast."""
    from src.tools.numerical_analysis import NumericalAnalyzer
    from src.tools.scenario_modeling import ScenarioModelingEngine

    print("\n" + "=" * 65)
    print("📈 DETERMINISTIC SCENARIO & RISK SIMULATION")
    print("=" * 65)

    sample_segments = [
        {"segment": "Segment A", "p1": args.p1 * 0.5, "p2": args.p2 * 0.467},
        {"segment": "Segment B", "p1": args.p1 * 0.3, "p2": args.p2 * 0.311},
        {"segment": "Segment C", "p1": args.p1 * 0.2, "p2": args.p2 * 0.222},
    ]
    seg_summary = NumericalAnalyzer.analyze_segment_contributions("Revenue", sample_segments, "₹ lakh")

    # Counterfactual
    cf = ScenarioModelingEngine.simulate_counterfactual(
        base_summary=seg_summary,
        scenario_name="Segment A Loss Neutralization",
        overrides={"Segment A": args.p1 * 0.5}
    )
    print(f"  • Baseline: Period 1 = {args.p1:,.1f}, Period 2 Actual = {args.p2:,.1f}")
    print(f"  • Simulated Counterfactual: {cf.simulated_period_2_total:,.1f} ({cf.simulated_pct_change:+.1f}%)")
    print(f"  • Narrative: {cf.narrative_summary}")

    # Recovery target
    rec = ScenarioModelingEngine.calculate_recovery_targets(
        base_summary=seg_summary,
        target_revenue=args.target
    )
    print(f"\n  • Recovery Target Plan to {args.target:,.1f}:")
    print(f"    - Required Incremental: +{rec.required_incremental:,.1f}")
    print(f"    - Feasibility:          {rec.feasibility_status.upper()}")
    for s_name, req_pct in rec.segment_required_growth_pct.items():
        print(f"      ↳ {s_name:<12}: +{req_pct:.1f}% growth required")

    # Monte Carlo
    mc = ScenarioModelingEngine.run_monte_carlo_forecast(seg_summary, num_simulations=1000)
    print(f"\n  • Monte Carlo 1,000-Path Volatility Bounds:")
    print(f"    - Conservative (P5):  {mc.p5_conservative:,.1f}")
    print(f"    - Median (P50):        {mc.p50_median:,.1f}")
    print(f"    - Optimistic (P95):    {mc.p95_optimistic:,.1f}")
    print(f"    - Prob of Recovery:    {mc.prob_recovering_baseline*100:.1f}%")
    print("=" * 65 + "\n")

def cmd_benchmark(args):
    """Executes the ADI-Bench v1.0 benchmark suite."""
    from src.evaluation.benchmark_runner import BenchmarkRunner

    print("\n" + "=" * 65)
    print("🧪 RUNNING ADI-BENCH v1.0 BENCHMARK SUITE")
    print("=" * 65)
    runner = BenchmarkRunner()
    result = runner.run_all_benchmarks()

    print(f"  • Suite Name:           {result.benchmark_name}")
    print(f"  • Timestamp:            {result.run_timestamp}")
    print(f"  • Scenarios Evaluated:  {len(result.scenario_scores)}")
    print("\n📊 EMPIRICAL METRICS COMPARISON (Proposed vs Baseline RAG):")
    proposed = result.ablation_results[0]
    baseline = result.ablation_results[1]
    print(f"  • Task Completion Rate (TCR):       {proposed.task_completion_rate:.1f}% vs {baseline.task_completion_rate:.1f}%")
    print(f"  • Mathematical Accuracy (MA):       {proposed.mathematical_accuracy:.1f}% vs {baseline.mathematical_accuracy:.1f}%")
    print(f"  • Citation Grounding Rate (CGR):    {proposed.citation_grounding_rate:.1f}% vs {baseline.citation_grounding_rate:.1f}%")
    print(f"  • Source Coverage (SC):             {proposed.source_coverage:.1f}% vs {baseline.source_coverage:.1f}%")
    print(f"  • Hallucination Rate (HR):          {proposed.hallucination_rate:.1f}% vs {baseline.hallucination_rate:.1f}%")
    print(f"  • Recovery Success Rate (RSR):      {proposed.recovery_success_rate:.1f}% vs {baseline.recovery_success_rate:.1f}%")
    print("=" * 65 + "\n")

def cmd_dupont(args):
    """Executes 3-Stage DuPont Analysis with mathematical proof."""
    from src.tools.numerical_analysis import NumericalAnalyzer
    print("\n" + "=" * 65)
    print("📐 3-STAGE DUPONT ROE DECOMPOSITION & PROOF")
    print("=" * 65)
    res = NumericalAnalyzer.calculate_dupont_analysis(
        net_income=args.ni,
        revenue=args.rev,
        total_assets=args.assets,
        total_equity=args.equity
    )
    print(f"  • Inputs: Net Income={res.net_income:,.1f}, Revenue={res.revenue:,.1f}, Assets={res.total_assets:,.1f}, Equity={res.total_equity:,.1f}")
    print(f"  • Net Profit Margin:       {res.net_profit_margin_pct:.2f}%")
    print(f"  • Asset Turnover:          {res.asset_turnover:.2f}x")
    print(f"  • Equity Multiplier:       {res.equity_multiplier:.2f}x")
    print(f"  • Direct ROE:              {res.roe_pct:.2f}%")
    print(f"  • 3-Stage Product ROE:     {res.reconciled_product_roe_pct:.2f}%")
    print(f"  • Deterministic Proof:     {'MATHEMATICALLY PROVEN (Delta <= 0.05%)' if res.is_mathematically_proven else 'DISCREPANCY DETECTED'}")
    print(f"  • Driver Interpretation:   {res.driver_breakdown}")
    print("=" * 65 + "\n")

def cmd_ratios(args):
    """Calculates audited liquidity, solvency, and profitability ratios."""
    from src.tools.numerical_analysis import NumericalAnalyzer
    print("\n" + "=" * 65)
    print("📊 COMPREHENSIVE CORPORATE FINANCIAL RATIOS")
    print("=" * 65)
    res = NumericalAnalyzer.calculate_financial_ratios(
        revenue=args.rev,
        cost_of_goods_sold=args.cogs,
        operating_income=args.ebit,
        net_income=args.ni,
        current_assets=args.ca,
        current_liabilities=args.cl,
        inventory=args.inventory or 0.0,
        total_debt=args.debt,
        total_equity=args.equity,
        total_assets=args.assets
    )
    print("  • Profitability:")
    if res.gross_margin_pct is not None:
        print(f"      - Gross Margin:          {res.gross_margin_pct:.2f}%")
    if res.operating_margin_pct is not None:
        print(f"      - Operating Margin:      {res.operating_margin_pct:.2f}%")
    if res.net_profit_margin_pct is not None:
        print(f"      - Net Profit Margin:     {res.net_profit_margin_pct:.2f}%")
    if res.return_on_assets_pct is not None:
        print(f"      - Return on Assets (ROA):{res.return_on_assets_pct:.2f}%")

    print("  • Liquidity & Solvency:")
    if res.current_ratio is not None:
        print(f"      - Current Ratio:         {res.current_ratio:.2f} [{res.liquidity_status.upper()}]")
    if res.quick_ratio is not None:
        print(f"      - Quick Ratio:           {res.quick_ratio:.2f}")
    if res.debt_to_equity is not None:
        print(f"      - Debt-to-Equity:        {res.debt_to_equity:.2f} [{res.solvency_status.upper()}]")
    if res.asset_turnover is not None:
        print(f"      - Asset Turnover:        {res.asset_turnover:.2f}x")
    print("=" * 65 + "\n")

def cmd_verify_pack(args):
    """Verifies cryptographic SHA-256 digital signature of an audit pack."""
    from src.tools.report_export import ReportExporter
    print("\n" + "=" * 65)
    print("🔐 CRYPTOGRAPHIC AUDIT PACK INTEGRITY VERIFIER")
    print("=" * 65)
    pack_path = Path(args.file)
    print(f"  • Verifying File:     {pack_path.name}")
    res = ReportExporter.verify_audit_pack_integrity(pack_path)
    if res["is_valid"]:
        print(f"  • Verification Status: [PASSED] {res['status']}")
        print(f"  • Task ID:             {res.get('task_id')}")
        print(f"  • SHA-256 Digest:      {res.get('recomputed_sha256')}")
        print(f"  • Documents Verified:  {res.get('total_documents_manifested')}")
    else:
        print(f"  • Verification Status: [FAILED] {res.get('status')}")
        print(f"  • Error:               {res.get('error')}")
        if "expected_sha256" in res:
            print(f"  • Expected Hash:       {res.get('expected_sha256')}")
            print(f"  • Recomputed Hash:     {res.get('recomputed_sha256')}")
    print("=" * 65 + "\n")

def main():
    parser = argparse.ArgumentParser(
        prog="adida",
        description="Autonomous Document Intelligence & Data Analysis Agent (ADIDA v4.1)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # status
    p_status = subparsers.add_parser("status", help="Check system status and configuration")
    p_status.set_defaults(func=cmd_status)

    # investigate
    p_inv = subparsers.add_parser("investigate", help="Run autonomous document investigation")
    p_inv.add_argument("--goal", default="Explain why revenue declined from Q1 to Q2 and identify the main contributing segments.", help="Investigation objective")
    p_inv.add_argument("--files", nargs="*", help="Paths to files to investigate")
    p_inv.set_defaults(func=cmd_investigate)

    # forensic
    p_forensic = subparsers.add_parser("forensic", help="Run Benford's Law and anomaly detection")
    p_forensic.add_argument("--file", help="Path to CSV or Excel file to audit")
    p_forensic.add_argument("--numbers", nargs="*", help="List of numbers to test")
    p_forensic.add_argument("--second-digit", action="store_true", help="Run Benford's Law Second-Digit test (0..9)")
    p_forensic.add_argument("--first-two-digits", action="store_true", help="Run Benford's Law First-Two Digits test (10..99)")
    p_forensic.set_defaults(func=cmd_forensic)

    # dupont
    p_dupont = subparsers.add_parser("dupont", help="Run 3-Stage DuPont ROE Decomposition and proof")
    p_dupont.add_argument("--ni", type=float, required=True, help="Net Income")
    p_dupont.add_argument("--rev", type=float, required=True, help="Consolidated Revenue")
    p_dupont.add_argument("--assets", type=float, required=True, help="Total Assets")
    p_dupont.add_argument("--equity", type=float, required=True, help="Total Equity")
    p_dupont.set_defaults(func=cmd_dupont)

    # ratios
    p_ratios = subparsers.add_parser("ratios", help="Calculate corporate profitability and solvency ratios")
    p_ratios.add_argument("--rev", type=float, required=True, help="Consolidated Revenue")
    p_ratios.add_argument("--cogs", type=float, help="Cost of Goods Sold (COGS)")
    p_ratios.add_argument("--ebit", type=float, help="Operating Income (EBIT)")
    p_ratios.add_argument("--ni", type=float, help="Net Income")
    p_ratios.add_argument("--ca", type=float, help="Current Assets")
    p_ratios.add_argument("--cl", type=float, help="Current Liabilities")
    p_ratios.add_argument("--inventory", type=float, default=0.0, help="Inventory value")
    p_ratios.add_argument("--debt", type=float, help="Total Debt")
    p_ratios.add_argument("--equity", type=float, help="Total Equity")
    p_ratios.add_argument("--assets", type=float, help="Total Assets")
    p_ratios.set_defaults(func=cmd_ratios)

    # verify-pack
    p_verify = subparsers.add_parser("verify-pack", help="Verify cryptographic SHA-256 digest of an audit pack")
    p_verify.add_argument("file", help="Path to audit_pack_*.json file")
    p_verify.set_defaults(func=cmd_verify_pack)

    # debate
    p_debate = subparsers.add_parser("debate", help="Run 4-agent red-team debate council")
    p_debate.add_argument("--goal", default="Explain why revenue declined from Q1 to Q2.", help="Debate resolution topic")
    p_debate.set_defaults(func=cmd_debate)

    # scenario
    p_scenario = subparsers.add_parser("scenario", help="Run counterfactual simulation and risk bounds")
    p_scenario.add_argument("--p1", type=float, default=1000.0, help="Period 1 revenue")
    p_scenario.add_argument("--p2", type=float, default=900.0, help="Period 2 revenue")
    p_scenario.add_argument("--target", type=float, default=1000.0, help="Recovery revenue target")
    p_scenario.set_defaults(func=cmd_scenario)

    # benchmark
    p_bench = subparsers.add_parser("benchmark", help="Run ADI-Bench v1.0 benchmark suite")
    p_bench.set_defaults(func=cmd_benchmark)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)

if __name__ == "__main__":
    main()
