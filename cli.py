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

def cmd_committee(args):
    """Executes a 5-Agent Autonomous Financial & Audit Committee debate with adversarial cross-examination."""
    from src.agent.committee import AutonomousAuditCommittee

    print("\n" + "=" * 65)
    print("🏛️ AUTONOMOUS FINANCIAL & AUDIT COMMITTEE")
    print("   5-Agent Adversarial Swarm Consensus Protocol")
    print("=" * 65)
    print(f"  • Mandate:                 {args.goal}")
    print(f"  • Disagreement Tolerance:  {args.disagreement_threshold * 100:.1f}%")
    print(f"  • Active Committee Personas:")
    print("      1. Dr. Benford (Forensic Auditor)")
    print("      2. Quant-Sigma (Quantitative Financial Analyst)")
    print("      3. Recon-Omni (Cross-Document Reconciler)")
    print("      4. Devil's Advocate (Adversarial Red-Team Lead)")
    print("      5. Chief Risk Officer (Synthesizer & Committee Chair)")

    # Construct numbers or period data
    period_data = {
        "metric": "Revenue",
        "p1": args.p1,
        "p2": args.p2,
        "p1_name": "Q1",
        "p2_name": "Q2",
        "unit": "₹ lakh"
    }
    sample_segments = [
        {"segment": "Segment A", "p1": args.p1 * 0.5, "p2": args.p2 * 0.467},
        {"segment": "Segment B", "p1": args.p1 * 0.3, "p2": args.p2 * 0.311},
        {"segment": "Segment C", "p1": args.p1 * 0.2, "p2": args.p2 * 0.222},
    ]

    dupont_data = None
    if getattr(args, "dupont", False):
        dupont_data = {
            "net_income": getattr(args, "ni", None) or (args.p2 * 0.12),
            "revenue": args.p2,
            "total_assets": getattr(args, "assets", None) or (args.p2 * 1.5),
            "total_equity": getattr(args, "equity", None) or (args.p2 * 0.8)
        }

    committee = AutonomousAuditCommittee(disagreement_threshold=args.disagreement_threshold)
    session = committee.convene_committee(
        task_id="cli_committee",
        goal=args.goal,
        period_data=period_data,
        segment_data=sample_segments,
        dupont_data=dupont_data
    )

    print(f"\n⚡ Completed {len(session.debate_rounds)} Structured Rounds across Committee:")
    for r in session.debate_rounds:
        print(f"\n  [ROUND {r.round_number} - {r.stage.upper()}] {r.speaker_name} ({r.speaker_role.value}):")
        for line in r.content.split("\n"):
            print(f"    {line}")
        if r.citations:
            print(f"    ↳ Citations: {', '.join(r.citations)}")

    v = session.verdict
    print("\n" + "-" * 65)
    print("📋 CHIEF RISK OFFICER CONSENSUS ADJUDICATION:")
    print(f"  • Consensus Reached:       {v.consensus_reached}")
    print(f"  • Consensus Confidence:    {v.consensus_confidence_score * 100:.1f}%")
    print(f"  • Disagreement Rate:       {v.disagreement_rate * 100:.1f}% (Threshold: {args.disagreement_threshold * 100:.1f}%)")
    print(f"  • Risk Posture:            {v.risk_posture}")
    print(f"  • HITL Review Required:    {v.requires_hitl}")
    if v.hitl_reason:
        print(f"  • Escalation Rationale:    {v.hitl_reason}")
    print(f"  • Executive Recommendation:{v.audit_recommendation}")
    if v.agreed_facts:
        print("  • Agreed Facts:")
        for af in v.agreed_facts[:4]:
            print(f"      ✓ {af}")
    if v.disputed_claims:
        print("  • Disputed Claims / Red-Team Objections:")
        for dc in v.disputed_claims:
            print(f"      ✗ {dc}")
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

def cmd_ground(args):
    """Highlights exact coordinates on a PDF page and exports a visual evidence snippet."""
    from src.ingestion.visual_grounding import VisualGroundingEngine
    from config.settings import settings
    pdf_path = Path(args.file) if args.file else (settings.sample_docs_dir / "Quarterly_Report.pdf")
    print("\n" + "=" * 65)
    print("📍 MULTIMODAL SPATIAL VISUAL GROUNDING")
    print("=" * 65)
    print(f"  • Source PDF:      {pdf_path.name}")
    print(f"  • Page Number:     {args.page}")

    bboxes = []
    if args.text:
        print(f"  • Text Query:      '{args.text}'")
        bboxes = VisualGroundingEngine.find_text_coordinates(pdf_path, args.page, args.text)
        print(f"  • Matches Found:   {len(bboxes)} occurrences")
    elif args.bbox:
        coords = [float(c) for c in args.bbox.split(",")]
        bboxes = [(coords[0], coords[1], coords[2], coords[3])]
    else:
        bboxes = [(50.0, 50.0, 350.0, 120.0)]

    out_file = settings.outputs_dir / "charts" / f"grounding_snippet_p{args.page}.png"
    res = VisualGroundingEngine.highlight_bboxes_on_page(
        pdf_path=pdf_path,
        page_number=args.page,
        bboxes=bboxes,
        output_path=out_file
    )
    print(f"  • Grounding Snippet: {res.highlighted_image_path}")
    print(f"  • Page Dimensions:   {res.page_width:.1f} x {res.page_height:.1f} pt")
    if res.matched_text:
        print(f"  • Grounded Snippet:  \"{res.matched_text[:80]}...\"")
    print("=" * 65 + "\n")

def cmd_dcf(args):
    """Executes multi-period DCF valuation and 2D WACC vs Terminal Growth sensitivity matrix."""
    from src.tools.code_interpreter import SandboxedFinancialInterpreter
    fcfs = [float(v.strip()) for v in args.fcf.split(",")]
    res = SandboxedFinancialInterpreter.run_dcf_valuation(
        free_cash_flows=fcfs,
        wacc=args.wacc,
        terminal_growth=args.growth,
        net_debt=args.debt or 0.0,
        shares_outstanding=args.shares or 1.0
    )
    print("\n" + "=" * 65)
    print("💰 DISCOUNTED CASH FLOW (DCF) & SENSITIVITY VALUATION")
    print("=" * 65)
    print(f"  • Projected Free Cash Flows: {res.free_cash_flows}")
    print(f"  • WACC (Discount Rate):      {res.discount_rate_wacc_pct:.2f}%")
    print(f"  • Perpetual Growth Rate (g): {res.terminal_growth_rate_pct:.2f}%")
    print(f"  • PV of Explicit FCFs:       {res.discounted_fcf_sum:,.2f}")
    print(f"  • Terminal Value (Nominal):  {res.terminal_value:,.2f}")
    print(f"  • Discounted Terminal Value: {res.discounted_terminal_value:,.2f}")
    print(f"  • Implied Enterprise Value:  {res.enterprise_value:,.2f}")
    print(f"  • Implied Equity Value:      {res.equity_value:,.2f}")
    if res.implied_share_price:
        print(f"  • Implied Target Share Price:{res.implied_share_price:,.2f}")

    print("\n📊 2D SENSITIVITY MATRIX (WACC vs Perpetual Growth Rate):")
    if res.sensitivity_matrix_wacc_vs_growth:
        keys = [k for k in res.sensitivity_matrix_wacc_vs_growth[0].keys() if k != "wacc_pct"]
        header = f"  {'WACC':<8} | " + " | ".join(f"{k:<8}" for k in keys)
        print(header)
        print("  " + "-" * len(header))
        for row in res.sensitivity_matrix_wacc_vs_growth:
            line = f"  {row['wacc_pct']:.1f}%   | " + " | ".join(f"{row[k]:>8,.1f}" if row[k] else "     N/A" for k in keys)
            print(line)
    print("=" * 65 + "\n")

def cmd_edgar(args):
    """Fetches SEC EDGAR XBRL corporate filings and macro benchmark context."""
    from src.ingestion.edgar_connector import SECEDGARConnector
    print("\n" + "=" * 65)
    print("🏛️ SEC EDGAR & XBRL CORPORATE FINANCIAL CONNECTOR")
    print("=" * 65)
    print(f"  • Target Ticker:   {args.ticker.upper()}")
    print(f"  • Filing Form:     {args.form.upper()}")
    print(f"  • Fiscal Year:     {args.year}")

    manifest, chunks = SECEDGARConnector.fetch_filing(
        ticker=args.ticker,
        filing_type=args.form,
        fiscal_year=args.year
    )

    print(f"  • Company Name:    {manifest.company_name} (CIK: {manifest.cik})")
    print(f"  • XBRL Facts:      {manifest.facts_count} standardized US-GAAP line items")

    print("\n📋 AUDITED INCOME STATEMENT:")
    for k, v in manifest.income_statement.items():
        print(f"    - {k:<28}: ${v:>18,.2f} USD")

    print("\n📋 AUDITED BALANCE SHEET:")
    for k, v in manifest.balance_sheet.items():
        print(f"    - {k:<28}: ${v:>18,.2f} USD")

    macro = SECEDGARConnector.get_macro_benchmark(args.year)
    print("\n🌐 MACROECONOMIC BENCHMARK CONTEXT:")
    print(f"    - 10Y Treasury Benchmark Yield: {macro.risk_free_rate_10y_pct:.2f}%")
    print(f"    - US Headline CPI Inflation:    {macro.us_cpi_inflation_pct:.2f}%")
    print(f"    - Real GDP Growth:              {macro.gdp_real_growth_pct:.2f}%")
    print(f"    - Sector Median Operating Margin:{macro.tech_sector_median_operating_margin_pct:.2f}%")
    print(f"  • Ingested Chunks for RAG:        {len(chunks)} grounded chunks")
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

    # committee (Pillar 1: Autonomous Audit Committee)
    p_comm = subparsers.add_parser("committee", help="Run 5-agent autonomous financial & audit committee")
    p_comm.add_argument("--goal", default="Audit financial integrity, earnings performance, and accounting compliance.", help="Committee mandate")
    p_comm.add_argument("--p1", type=float, default=1000.0, help="Period 1 revenue/metric")
    p_comm.add_argument("--p2", type=float, default=900.0, help="Period 2 revenue/metric")
    p_comm.add_argument("--disagreement-threshold", type=float, default=0.15, help="Disagreement tolerance before HITL escalation (default: 0.15 = 15%)")
    p_comm.add_argument("--dupont", action="store_true", help="Include 3-Stage DuPont ROE calculation")
    p_comm.add_argument("--ni", type=float, help="Net Income for DuPont")
    p_comm.add_argument("--assets", type=float, help="Total Assets for DuPont")
    p_comm.add_argument("--equity", type=float, help="Total Equity for DuPont")
    p_comm.set_defaults(func=cmd_committee)

    # ground (Pillar 2: Multimodal Visual Grounding)
    p_ground = subparsers.add_parser("ground", help="Highlight exact coordinates on a PDF page and export evidence image")
    p_ground.add_argument("--file", help="Path to PDF file")
    p_ground.add_argument("--page", type=int, default=1, help="Page number to inspect (1-indexed)")
    p_ground.add_argument("--bbox", help="Comma-separated bounding box x0,y0,x1,y1")
    p_ground.add_argument("--text", help="Text string to find and highlight")
    p_ground.set_defaults(func=cmd_ground)

    # dcf (Pillar 3: Financial Sandbox & DCF Valuation)
    p_dcf = subparsers.add_parser("dcf", help="Run multi-period DCF valuation and 2D sensitivity matrix")
    p_dcf.add_argument("--fcf", required=True, help="Comma-separated projected FCFs, e.g. 100,115,130,145,160")
    p_dcf.add_argument("--wacc", type=float, default=0.09, help="Discount rate / WACC (default 0.09 = 9%)")
    p_dcf.add_argument("--growth", type=float, default=0.025, help="Terminal growth rate (default 0.025 = 2.5%)")
    p_dcf.add_argument("--debt", type=float, default=0.0, help="Net debt to deduct")
    p_dcf.add_argument("--shares", type=float, default=1.0, help="Shares outstanding for target price")
    p_dcf.set_defaults(func=cmd_dcf)

    # edgar (Pillar 4: SEC EDGAR & Market Data Connectors)
    p_edgar = subparsers.add_parser("edgar", help="Fetch SEC EDGAR XBRL corporate filings and macro benchmark context")
    p_edgar.add_argument("--ticker", default="MSFT", help="Stock ticker symbol (e.g. MSFT, AAPL, GOOGL, NVDA)")
    p_edgar.add_argument("--year", type=int, default=2024, help="Fiscal year to retrieve (default: 2024)")
    p_edgar.add_argument("--form", default="10-K", help="SEC Form type (10-K, 10-Q, 8-K)")
    p_edgar.set_defaults(func=cmd_edgar)

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
