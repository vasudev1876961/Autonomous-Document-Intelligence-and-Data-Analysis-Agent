"""
Interactive Enterprise Streamlit Dashboard for the Autonomous Document Intelligence and Data Analysis Agent.
Evidence-driven multi-format document understanding, deterministic reasoning, verified reporting,
Human-in-the-Loop supervision, and benchmark evaluation.
"""
from pathlib import Path
import json
import streamlit as st
import pandas as pd
from config.settings import settings
from src.agent.orchestrator import AgentOrchestrator
from src.agent.specialists import PlannerSpecialist, RetrievalSpecialist, AnalyticalSpecialist, VerificationAuditor, SupervisorAgent
from src.human_review.approval import ApprovalDecision, RiskLevel
from src.human_review.review_queue import ReviewQueue
from src.evaluation.benchmark_runner import BenchmarkRunner
from src.memory.sqlite_store import SQLiteStore
from src.memory.task_history import TaskHistoryManager
from src.tools.report_export import ReportExporter
from src.retrieval.knowledge_graph import DocumentKnowledgeGraph
from src.tools.scenario_modeling import ScenarioModelingEngine
from src.agent.debate import MultiAgentDebateCouncil

# Streamlit Page Setup

st.set_page_config(
    page_title="Autonomous Document Intelligence & Data Analysis Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Rich dark/clean professional executive theme)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #0284c7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.5rem;
        font-weight: 500;
    }
    
    .kpi-card {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 15px;
    }
    .kpi-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #0f172a;
        margin: 4px 0;
    }
    .kpi-delta-pos {
        color: #16a34a;
        font-weight: 700;
        font-size: 0.9rem;
    }
    .kpi-delta-neg {
        color: #dc2626;
        font-weight: 700;
        font-size: 0.9rem;
    }
    
    .badge-fact {
        background-color: #dbeafe;
        color: #1e40af;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.82rem;
        letter-spacing: 0.03em;
    }
    .badge-interp {
        background-color: #dcfce7;
        color: #166534;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.82rem;
        letter-spacing: 0.03em;
    }
    .badge-unc {
        background-color: #fef9c3;
        color: #854d0e;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.82rem;
        letter-spacing: 0.03em;
    }
    
    .audit-card {
        background: #ffffff;
        border-left: 4px solid #3b82f6;
        border: 1px solid #e2e8f0;
        border-left-width: 5px;
        padding: 14px 18px;
        margin-bottom: 12px;
        border-radius: 6px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .hitl-banner {
        background: #fffbeb;
        border: 2px solid #f59e0b;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 18px;
    }
</style>
""", unsafe_allow_html=True)

# App State Initialization
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = AgentOrchestrator()
if "last_state" not in st.session_state:
    st.session_state.last_state = None
if "selected_files" not in st.session_state:
    st.session_state.selected_files = []
if "review_queue" not in st.session_state:
    st.session_state.review_queue = ReviewQueue()
if "benchmark_report" not in st.session_state:
    st.session_state.benchmark_report = None

# Sidebar Controls
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=64)
    st.title("Control Center")
    st.caption("Agentic AI • RAG • Verification • HITL")

    st.markdown("---")
    st.subheader("📁 Document Management")
    
    # Upload documents
    uploaded_files = st.file_uploader(
        "Upload Documents",
        type=["pdf", "docx", "xlsx", "csv"],
        accept_multiple_files=True,
        help="Upload heterogeneous reports, financial workbooks, or CSVs."
    )

    sample_btn = st.button("📦 Load Sample Benchmark Documents", use_container_width=True)
    if sample_btn:
        sample_paths = [
            settings.sample_docs_dir / "Quarterly_Report.pdf",
            settings.sample_docs_dir / "Revenue_Data.xlsx",
            settings.sample_docs_dir / "Segment_Performance.csv"
        ]
        st.session_state.selected_files = [p for p in sample_paths if p.exists()]
        st.success(f"Loaded {len(st.session_state.selected_files)} benchmark sample files!")

    if uploaded_files:
        temp_paths = []
        for uf in uploaded_files:
            target_path = settings.data_dir / uf.name
            with open(target_path, "wb") as f:
                f.write(uf.getbuffer())
            temp_paths.append(target_path)
        st.session_state.selected_files = temp_paths
        st.info(f"Staged {len(temp_paths)} uploaded file(s).")

    if st.session_state.selected_files:
        st.markdown("**Staged Documents:**")
        for p in st.session_state.selected_files:
            st.markdown(f"- 📄 `{Path(p).name}`")

    st.markdown("---")
    st.subheader("⚙️ Agent Architecture & Guardrails")
    agent_mode = st.selectbox(
        "Agent Orchestration Mode",
        ["Full Autonomous Agent (LangGraph)", "Multi-Agent Specialist Collaboration", "Strict HITL Supervised Mode"],
        index=0
    )
    max_steps = st.slider("Max Investigation Steps", 5, 25, 15)
    discrepancy_threshold = st.slider("Conflict Alert Threshold (%)", 0.1, 5.0, 1.0, 0.1)
    st.checkbox("Enforce Deterministic Calculations", value=True, disabled=True)
    st.checkbox("Mandatory Citation Grounding", value=True, disabled=True)

# Main Application Layout
st.markdown('<div class="main-header">Autonomous Document Intelligence & Data Analysis Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">An Evidence-Driven Agentic AI System for Multi-Format Document Understanding, Analytical Reasoning, and Verified Reporting</div>', unsafe_allow_html=True)

tabs = st.tabs([
    "🚀 Investigation Studio",
    "📊 Analytical Findings & Visuals",
    "🔍 Verification & Discrepancy Audit",
    "🕸️ Causal Knowledge Graph",
    "📈 What-If Scenarios & Sensitivity Engine",
    "⚔️ Multi-Agent Debate Council",
    "🤝 Human-in-the-Loop Review Center",
    "🧪 Evaluation & Benchmarks",
    "📜 Audit Trail & History",
    "📁 Document & Provenance Inspector",
    "⚡ Enterprise API & System Status"
])


# ==========================================
# TAB 1: INVESTIGATION STUDIO
# ==========================================
with tabs[0]:
    st.markdown("### 1. Investigative Objective")
    
    col_input, col_quick = st.columns([3, 1])
    with col_input:
        default_goal = "Explain why revenue declined from Q1 to Q2. Identify the main contributing segments and support the explanation with evidence."
        user_goal = st.text_area(
            "Define Analytical Goal",
            value=default_goal,
            height=100,
            help="Specify an analytical question or objective."
        )
    with col_quick:
        st.markdown("**Quick Benchmark Scenarios:**")
        if st.button("📉 Standard Revenue Decline", use_container_width=True):
            user_goal = default_goal
            sample_paths = [
                settings.sample_docs_dir / "Quarterly_Report.pdf",
                settings.sample_docs_dir / "Revenue_Data.xlsx",
                settings.sample_docs_dir / "Segment_Performance.csv"
            ]
            st.session_state.selected_files = [p for p in sample_paths if p.exists()]
            st.rerun()

        if st.button("⚖️ Test Cross-Doc Conflict", use_container_width=True):
            conflict_paths = [
                settings.sample_docs_dir / "Quarterly_Report.pdf",
                settings.sample_docs_dir / "Revenue_Data.xlsx",
                settings.sample_docs_dir / "Conflicting_Report.pdf"
            ]
            st.session_state.selected_files = [p for p in conflict_paths if p.exists()]
            st.rerun()

    launch_col1, launch_col2 = st.columns([1, 3])
    with launch_col1:
        launch_btn = st.button("🚀 Launch Autonomous Investigation", type="primary", use_container_width=True)

    if launch_btn:
        if not st.session_state.selected_files:
            sample_paths = [
                settings.sample_docs_dir / "Quarterly_Report.pdf",
                settings.sample_docs_dir / "Revenue_Data.xlsx",
                settings.sample_docs_dir / "Segment_Performance.csv"
            ]
            st.session_state.selected_files = [p for p in sample_paths if p.exists()]

        with st.status("Agent actively investigating documents...", expanded=True) as status:
            st.write("🔍 **[Node 1-2] Ingestion & Hybrid Retrieval:** Preserving page & cell provenance via BM25 + Dense vector store...")
            st.write("📊 **[Node 3-4] Extraction & Discrepancy Reconciliation:** Parsing tabular structures & reconciling cross-document claims...")
            st.write("🧮 **[Node 5-6] Deterministic Mathematical Analysis:** Computing period-over-period delta and segment additivity proofs...")
            st.write("🧠 **[Node 7] Brain Reasoning:** Grounding observed facts, supported interpretations, and disclosing missing evidence...")
            st.write("🛡️ **[Node 8] Independent Verification Audit:** Recomputing formulas and verifying SHA-256 citation hashes...")
            st.write("📈 **[Node 9-10] Visual Analytics & Report Export:** Rendering waterfall charts and exporting audit-grade deliverables...")
            
            try:
                state = st.session_state.orchestrator.run_investigation(
                    goal=user_goal,
                    file_paths=st.session_state.selected_files
                )
                st.session_state.last_state = state
                
                # Check for approval requests
                for req in state.approval_requests:
                    st.session_state.review_queue.active_requests[req.request_id] = req

                status.update(label="✅ Investigation Completed & Independently Verified!", state="complete")
            except Exception as e:
                status.update(label=f"❌ Error during investigation: {e}", state="error")
                st.error(str(e))

    # Display KPI Cards if state exists
    state = st.session_state.last_state
    if state:
        st.markdown("---")
        st.subheader("Key Investigative Performance Indicators")
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        
        p_res = state.period_comparison
        s_res = state.segment_analysis
        
        with m_col1:
            st.metric("Total Baseline Revenue", f"{p_res.period_1_value:,.1f} {p_res.unit}" if p_res else "N/A")
        with m_col2:
            st.metric("Total Comparative Revenue", f"{p_res.period_2_value:,.1f} {p_res.unit}" if p_res else "N/A")
        with m_col3:
            delta_val = f"{p_res.absolute_change:+,.1f} {p_res.unit}" if p_res else "N/A"
            pct_val = f"{p_res.percentage_change:+,.1f}%" if (p_res and p_res.percentage_change) else "N/A"
            st.metric("Overall Delta (ΔR)", delta_val, delta_color="inverse", delta=pct_val)
        with m_col4:
            primary_seg = min(s_res.segments, key=lambda s: s.absolute_change) if s_res else None
            st.metric("Primary Driver", primary_seg.segment_name if primary_seg else "N/A", f"{primary_seg.contribution_percentage:.1f}% contrib" if primary_seg else "")

        # Conflict Banner
        if state.reconciliation_summary and state.reconciliation_summary.has_blocking_conflicts:
            st.warning(f"⚠️ **Cross-Document Discrepancy Detected:** Found {state.reconciliation_summary.discrepancy_count} conflicting claims between sources! Switch to the **'Human-in-the-Loop Review Center'** tab to review resolution options.")

# ==========================================
# TAB 2: ANALYTICAL FINDINGS & VISUALS
# ==========================================
with tabs[1]:
    state = st.session_state.last_state
    if not state:
        st.info("Run an investigation in the Investigation Studio tab to view analytical findings.")
    else:
        st.subheader("Verified Numerical Breakdown")
        
        # Period comparison table
        if state.period_comparison:
            p = state.period_comparison
            df_p = pd.DataFrame([{
                "Metric": p.metric_name,
                "Period 1": f"{p.period_1_value:,.1f} {p.unit}",
                "Period 2": f"{p.period_2_value:,.1f} {p.unit}",
                "Absolute Change (Δ)": f"{p.absolute_change:+,.1f} {p.unit}",
                "Percentage Change (%Δ)": f"{p.percentage_change:+,.1f}%" if p.percentage_change else "N/A",
                "Direction": p.direction.upper(),
                "Deterministic Formula": p.formula_used
            }])
            st.dataframe(df_p, use_container_width=True, hide_index=True)

        # Segment breakdown table
        if state.segment_analysis:
            s_data = []
            for s in state.segment_analysis.segments:
                s_data.append({
                    "Segment": s.segment_name,
                    "Period 1": f"{s.period_1_value:,.1f}",
                    "Period 2": f"{s.period_2_value:,.1f}",
                    "Absolute Delta (Δ)": f"{s.absolute_change:+,.1f} {state.segment_analysis.unit}",
                    "Contribution (%C)": f"{s.contribution_percentage:.1f}%",
                    "Direction": s.direction.capitalize(),
                    "Offsetting": "Yes" if s.is_offsetting else "No"
                })
            st.dataframe(pd.DataFrame(s_data), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("Epistemic Grounding of Findings")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("##### <span class='badge-fact'>OBSERVED FACTS</span>", unsafe_allow_html=True)
            for f in state.observed_facts:
                st.markdown(f"- {f}")
        with c2:
            st.markdown("##### <span class='badge-interp'>SUPPORTED INTERPRETATIONS</span>", unsafe_allow_html=True)
            for i in state.supported_interpretations:
                st.markdown(f"- {i}")
        with c3:
            st.markdown("##### <span class='badge-unc'>DISCLOSED UNCERTAINTIES</span>", unsafe_allow_html=True)
            if state.unresolved_questions:
                for u in state.unresolved_questions:
                    st.markdown(f"- {u}")
            else:
                st.markdown("*No unresolved gaps.*")

        st.markdown("---")
        st.subheader("Executive Visual Analytics")
        if state.chart_paths:
            ch_cols = st.columns(len(state.chart_paths))
            for idx, ch_p in enumerate(state.chart_paths):
                if Path(ch_p).exists():
                    with ch_cols[idx]:
                        st.image(ch_p, use_container_width=True)

# ==========================================
# TAB 3: VERIFICATION & DISCREPANCY AUDIT
# ==========================================
with tabs[2]:
    state = st.session_state.last_state
    if not state or not state.verification_audit:
        st.info("No verification audit available yet. Launch an investigation to inspect verification checks.")
    else:
        v = state.verification_audit
        st.subheader("Independent Verification Pipeline (Zero Hallucination Proofs)")
        
        if v.all_checks_passed:
            st.success(f"🛡️ **{v.summary_verdict}** (Passed {v.passed_checks}/{v.total_checks} independent checks)")
        else:
            st.warning(f"⚠️ **{v.summary_verdict}** ({v.failed_checks} check(s) flagged)")

        v_col1, v_col2 = st.columns(2)
        with v_col1:
            st.markdown("#### Mathematical Recomputations")
            for check in v.calculation_checks:
                badge = "✅ PASS" if check.is_valid else "❌ FAIL"
                st.markdown(f"- **{badge}** | **{check.test_name}**: Expected `{check.expected_value}`, Recomputed `{check.computed_value}` (Discrepancy: `{check.discrepancy}`)")

        with v_col2:
            st.markdown("#### Citation & Source Grounding Audits")
            for cite in v.citation_checks:
                badge = "✅ PASS" if cite.is_valid else "❌ FAIL"
                st.markdown(f"- **{badge}** | **{cite.citation_text}**: {cite.details}")

        st.markdown("---")
        st.subheader("Cross-Document Source Reconciliation Ledger")
        if state.reconciliation_summary:
            r = state.reconciliation_summary
            st.markdown(f"**Total Pairwise Comparisons:** {r.total_comparisons} | **Matched:** {r.matched_count} | **Discrepancies:** {r.discrepancy_count}")
            if r.material_conflicts:
                rec_rows = []
                for mc in r.material_conflicts:
                    rec_rows.append({
                        "Metric": mc.metric_name,
                        "Period": mc.period,
                        "Claim A (Source)": f"{mc.claim_a.document_name} ({mc.claim_a.reported_value} {mc.claim_a.unit})",
                        "Claim B (Source)": f"{mc.claim_b.document_name} ({mc.claim_b.reported_value} {mc.claim_b.unit})",
                        "Absolute Diff": mc.absolute_difference,
                        "Percentage Diff": f"{mc.percentage_difference:.2f}%",
                        "Materiality": "HIGH RISK (Material)" if mc.is_material else "Low"
                    })
                st.dataframe(pd.DataFrame(rec_rows), use_container_width=True, hide_index=True)
            else:
                st.success("✅ All overlapping claims across sources are perfectly reconciled.")

# ==========================================
# TAB 4: CAUSAL KNOWLEDGE GRAPH
# ==========================================
with tabs[3]:
    st.subheader("🕸️ Autonomous Causal Knowledge Graph (KG-RAG)")
    st.caption("Extracted entity nodes, causal root-cause pathways, and degree centrality hubs with source citations.")
    state = st.session_state.last_state
    if not state or not state.knowledge_graph_summary:
        st.info("No Knowledge Graph synthesized yet. Launch an investigation to extract causal entity relationships.")
    else:
        kg = state.knowledge_graph_summary
        kg_col1, kg_col2, kg_col3, kg_col4 = st.columns(4)
        with kg_col1:
            st.metric("Total Entities (Nodes)", kg.get("total_nodes", 0))
        with kg_col2:
            st.metric("Total Relationships (Edges)", kg.get("total_edges", 0))
        with kg_col3:
            st.metric("Entity Types", len(kg.get("node_types", {})))
        with kg_col4:
            st.metric("Causal Paths Discovered", len(kg.get("causal_paths", [])))

        st.markdown("---")
        st.markdown("#### 🎯 Key Central Hub Entities (Degree Centrality)")
        if kg.get("key_hubs"):
            st.dataframe(pd.DataFrame(kg["key_hubs"]), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("#### 🔗 Causal Root-Cause Pathways (Multi-Hop Graph Traversal)")
        causal_paths = kg.get("causal_paths", [])
        if causal_paths:
            for idx, p in enumerate(causal_paths, 1):
                path_str = " ➔ ".join([f"`{node_name}`" for node_name in p])
                st.markdown(f"**Path {idx}:** {path_str}")
        else:
            st.info("No multi-hop causal paths found in current subgraph.")

        st.markdown("---")
        st.markdown("#### 📊 Entity & Relationship Distribution")
        dist_col1, dist_col2 = st.columns(2)
        with dist_col1:
            st.markdown("**Entities by Type:**")
            st.json(kg.get("node_types", {}))
        with dist_col2:
            st.markdown("**Relations by Type:**")
            st.json(kg.get("relation_types", {}))

# ==========================================
# TAB 5: WHAT-IF SCENARIOS & SENSITIVITY ENGINE
# ==========================================
with tabs[4]:
    st.subheader("📈 Deterministic Scenario Modeling & What-If Studio")
    st.caption("Interactive counterfactual analysis, sensitivity shocks, recovery target trajectory solving, and Monte Carlo risk curves.")
    state = st.session_state.last_state
    
    seg_summary = state.segment_analysis if state else None
    if not seg_summary:
        from src.tools.numerical_analysis import NumericalAnalyzer
        sample_segs = [
            {"segment": "Segment A", "p1": 500.0, "p2": 420.0},
            {"segment": "Segment B", "p1": 300.0, "p2": 280.0},
            {"segment": "Segment C", "p1": 200.0, "p2": 200.0},
        ]
        seg_summary = NumericalAnalyzer.analyze_segment_contributions("Revenue", sample_segs, "₹ lakh")
        st.info("Showing interactive simulation playground calibrated on benchmark baseline data.")

    sim_tab1, sim_tab2, sim_tab3, sim_tab4 = st.tabs([
        "🔮 Counterfactual Simulation",
        "🎛️ Sensitivity Matrix",
        "🎯 Recovery Target Solver",
        "🎲 Monte Carlo Volatility Bounds"
    ])

    with sim_tab1:
        st.markdown("#### What-If Counterfactual Experiment")
        st.caption("Simulate what consolidated revenue would be if specific segments performed differently in Period 2.")
        
        c_cols = st.columns(len(seg_summary.segments))
        overrides = {}
        for idx, seg in enumerate(seg_summary.segments):
            with c_cols[idx]:
                new_val = st.slider(
                    f"{seg.segment_name} (Actual: {seg.period_2_value:.0f})",
                    min_value=0.0,
                    max_value=float(seg.period_1_value * 1.5),
                    value=float(seg.period_2_value),
                    step=5.0,
                    key=f"cf_slider_{seg.segment_name}"
                )
                if new_val != seg.period_2_value:
                    overrides[seg.segment_name] = new_val

        cf_res = ScenarioModelingEngine.simulate_counterfactual(
            base_summary=seg_summary,
            scenario_name="Executive Scenario Simulation",
            overrides=overrides
        )

        res_c1, res_c2, res_c3, res_c4 = st.columns(4)
        with res_c1:
            st.metric("Simulated Total Revenue", f"{cf_res.simulated_period_2_total:,.1f} {seg_summary.unit}")
        with res_c2:
            st.metric("Simulated Net Delta (ΔR)", f"{cf_res.simulated_delta:+,.1f} {seg_summary.unit}", f"{cf_res.simulated_pct_change:+,.1f}%")
        with res_c3:
            st.metric("Variance vs Actual Q2", f"{cf_res.delta_difference_from_actual:+,.1f} {seg_summary.unit}")
        with res_c4:
            st.metric("Decline Loss Preserved", f"{cf_res.loss_preserved_pct:.1f}%")

        st.info(f"💡 **Executive Narrative:** {cf_res.narrative_summary}")

    with sim_tab2:
        st.markdown("#### Segment Sensitivity Curve")
        st.caption("Evaluates overall revenue elasticity against percentage shocks in individual segments.")
        target_name = st.selectbox("Select Business Segment to Shock", [s.segment_name for s in seg_summary.segments])
        sens_res = ScenarioModelingEngine.compute_sensitivity_matrix(seg_summary, target_name)
        
        df_sens = pd.DataFrame([p.model_dump() for p in sens_res.points])
        df_sens.columns = ["Shock (%)", f"{target_name} Value", "Total Revenue", "Overall Growth (%)"]
        st.dataframe(df_sens, use_container_width=True, hide_index=True)
        st.line_chart(df_sens.set_index("Shock (%)")[["Total Revenue"]])

    with sim_tab3:
        st.markdown("#### Forward Recovery Target Solver")
        st.caption("Solves for the required revenue allocation across segments to hit an executive target.")
        target_rev = st.number_input("Desired Target Consolidated Revenue (₹ lakh)", value=float(seg_summary.total_period_1), step=50.0)
        rec_plan = ScenarioModelingEngine.calculate_recovery_targets(seg_summary, target_rev)
        
        st.markdown(f"**Feasibility Assessment:** `{rec_plan.feasibility_status}`")
        st.markdown(f"**Required Incremental Revenue:** `{rec_plan.required_incremental:+,.1f} {seg_summary.unit}`")
        st.info(f"📋 **Strategy Directive:** {rec_plan.narrative_strategy}")

        rec_data = []
        for s_name, t_val in rec_plan.segment_targets.items():
            rec_data.append({
                "Segment": s_name,
                "Current Q2": f"{next(s.period_2_value for s in seg_summary.segments if s.segment_name == s_name):,.1f}",
                "Required Target": f"{t_val:,.1f}",
                "Required Growth (%)": f"{rec_plan.segment_required_growth_pct.get(s_name, 0.0):+,.1f}%"
            })
        st.dataframe(pd.DataFrame(rec_data), use_container_width=True, hide_index=True)

    with sim_tab4:
        st.markdown("#### Stochastic Monte Carlo Volatility Bounds (1,000 Runs)")
        st.caption("Estimates probabilistic confidence intervals for forward performance under Gaussian market volatility.")
        sim_vol = st.slider("Market Volatility Sigma (%)", 1.0, 15.0, 6.0, 0.5) / 100.0
        mc_res = ScenarioModelingEngine.run_monte_carlo_forecast(seg_summary, num_simulations=1000, volatility_pct=sim_vol)
        
        mc1, mc2, mc3, mc4 = st.columns(4)
        with mc1:
            st.metric("5th Percentile (Conservative)", f"{mc_res.p5_conservative:,.1f}")
        with mc2:
            st.metric("50th Percentile (Median)", f"{mc_res.p50_median:,.1f}")
        with mc3:
            st.metric("95th Percentile (Optimistic)", f"{mc_res.p95_optimistic:,.1f}")
        with mc4:
            st.metric("Prob. of Baseline Recovery", f"{mc_res.prob_recovering_baseline:.1f}%")

        if mc_res.simulation_samples:
            st.bar_chart(pd.Series(mc_res.simulation_samples).sort_values().reset_index(drop=True))

# ==========================================
# TAB 6: MULTI-AGENT DEBATE COUNCIL
# ==========================================
with tabs[5]:
    st.subheader("⚔️ Multi-Agent Red-Team Debate Council")
    st.caption("Adversarial cross-examination between Quantitative Analysts, Retrieval Specialists, and Red-Team Auditors.")
    state = st.session_state.last_state
    
    debate = state.debate_session if state else None
    if not debate:
        from src.tools.numerical_analysis import NumericalAnalyzer
        sample_segs = [
            {"segment": "Segment A", "p1": 500.0, "p2": 420.0},
            {"segment": "Segment B", "p1": 300.0, "p2": 280.0},
            {"segment": "Segment C", "p1": 200.0, "p2": 200.0},
        ]
        seg_summary = NumericalAnalyzer.analyze_segment_contributions("Revenue", sample_segs, "₹ lakh")
        p_res = NumericalAnalyzer.compare_periods("Revenue", 1000.0, 900.0, "Q1", "Q2", "₹ lakh")
        council = MultiAgentDebateCouncil()
        debate = council.run_debate("Explain revenue decline from Q1 to Q2", p_res, seg_summary, None, []).model_dump()

    verdict = debate.get("verdict", {})
    v_c1, v_c2 = st.columns([1, 2])
    with v_c1:
        st.markdown(f"### Consensus Status")
        if verdict.get("consensus_reached"):
            st.success(f"🤝 **Consensus Achieved** ({verdict.get('confidence_score', 0)*100:.1f}% confidence)")
        else:
            st.warning("⚠️ **Unresolved Dissenting Claims**")
        st.markdown(f"**HITL Mandate:** `{'Required' if verdict.get('requires_hitl') else 'Automated Verification'}`")
    with v_c2:
        st.markdown("### Executive Supervisor Recommendation")
        st.info(f"📜 {verdict.get('audit_recommendation', 'Approved.')}")

    st.markdown("---")
    st.markdown("#### 🎙️ Chamber Debate Transcript")
    for msg in debate.get("rounds", []):
        role = msg.get("speaker_role")
        name = msg.get("speaker_name")
        r_num = msg.get("round_number")
        content = msg.get("content")
        cites = msg.get("citations", [])

        role_icons = {
            "Quantitative Analyst": "🧮",
            "Retrieval Specialist": "🔍",
            "Red-Team Auditor": "🛡️",
            "Executive Supervisor": "👑"
        }
        icon = role_icons.get(role, "🤖")
        with st.chat_message(name, avatar=icon):
            st.markdown(f"**[Round {r_num}] {role} ({name})**")
            st.write(content)
            if cites:
                st.caption(f"Citations: {', '.join(cites)}")

    st.markdown("---")
    f_c1, f_c2 = st.columns(2)
    with f_c1:
        st.markdown("#### ✅ Agreed Facts")
        for f in verdict.get("agreed_facts", []):
            st.markdown(f"- {f}")
    with f_c2:
        st.markdown("#### ❓ Surviving Uncertainties / Disputed Claims")
        for d in verdict.get("disputed_claims", []):
            st.markdown(f"- ⚠️ {d}")

# ==========================================
# TAB 7: HUMAN-IN-THE-LOOP REVIEW CENTER
# ==========================================
with tabs[6]:

    st.subheader("🤝 Human-in-the-Loop Review Queue")
    st.caption("Inspect and resolve escalations, approve plans, or resolve cross-document data conflicts.")

    queue = st.session_state.review_queue
    pending = queue.get_pending_requests()

    if not pending:
        st.info("✅ No pending approval requests. Agent operations are within automated confidence guardrails.")
    else:
        st.markdown(f"**Pending Requests ({len(pending)}):**")
        for req in pending:
            with st.container():
                st.markdown(f"""
                <div class="hitl-banner">
                    <h4>⚠️ [{req.risk_level.value.upper()}] {req.title}</h4>
                    <p>{req.description}</p>
                    <p><b>Proposed Action:</b> {req.proposed_action}</p>
                </div>
                """, unsafe_allow_html=True)
                
                selected_opt = st.radio(
                    f"Choose resolution policy for {req.request_id}:",
                    options=req.options,
                    key=f"opt_{req.request_id}"
                )
                user_comment = st.text_input("Reviewer Comments / Instructions:", key=f"comm_{req.request_id}")
                
                btn_col1, btn_col2 = st.columns([1, 4])
                with btn_col1:
                    if st.button("Confirm Decision", key=f"btn_confirm_{req.request_id}", type="primary"):
                        queue.submit_decision(
                            request_id=req.request_id,
                            decision=ApprovalDecision.APPROVE,
                            selected_option=selected_opt,
                            comments=user_comment,
                            decided_by="Human Reviewer"
                        )
                        st.success(f"Decision registered for {req.request_id}!")
                        st.rerun()

# ==========================================
# TAB 8: EVALUATION & BENCHMARKS
# ==========================================
with tabs[7]:
    st.subheader("🧪 Automated Benchmark Suite (ADI-Bench v1.0)")
    st.caption("Measures task completion, numerical accuracy, citation grounding, hallucination suppression, and recovery success.")

    run_bench_btn = st.button("⚡ Run Full Benchmark Suite & Ablation Study", type="primary")

    if run_bench_btn:
        with st.spinner("Running benchmark scenarios and calculating comparative metrics..."):
            runner = BenchmarkRunner()
            report = runner.run_all_benchmarks()
            st.session_state.benchmark_report = report
            st.success("Benchmark suite execution complete!")

    report = st.session_state.benchmark_report
    if report:
        st.markdown(f"**Benchmark Run Timestamp:** `{report.run_timestamp}`")
        
        # Aggregate scorecard
        agg = report.aggregate_metrics
        b1, b2, b3, b4, b5, b6 = st.columns(6)
        with b1:
            st.metric("Task Completion (TCR)", f"{agg.task_completion_rate:.1f}%")
        with b2:
            st.metric("Math Accuracy (MA)", f"{agg.mathematical_accuracy:.1f}%")
        with b3:
            st.metric("Citation Grounding (CGR)", f"{agg.citation_grounding_rate:.1f}%")
        with b4:
            st.metric("Source Coverage (SC)", f"{agg.source_coverage:.1f}%")
        with b5:
            st.metric("Hallucination Rate (HR)", f"{agg.hallucination_rate:.1f}%", delta_color="inverse")
        with b6:
            st.metric("Recovery Rate (RSR)", f"{agg.recovery_success_rate:.1f}%")

        st.markdown("---")
        st.subheader("Ablation Study: Autonomous Agent vs Conventional RAG")
        abl_rows = []
        for ab in report.ablation_results:
            abl_rows.append({
                "System Architecture": ab.system_variant,
                "TCR (%)": ab.task_completion_rate,
                "Math Accuracy (%)": ab.mathematical_accuracy,
                "Citation Grounding (%)": ab.citation_grounding_rate,
                "Source Coverage (%)": ab.source_coverage,
                "Hallucination Rate (%)": ab.hallucination_rate,
                "Recovery Rate (%)": ab.recovery_success_rate
            })
        st.dataframe(pd.DataFrame(abl_rows), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("Scenario-by-Scenario Evaluation Scores")
        sc_rows = []
        for s in report.scenario_scores:
            sc_rows.append({
                "Scenario ID": s.scenario_id,
                "Scenario Name": s.scenario_name,
                "TCR": "PASS" if s.tcr_pass else "FAIL",
                "Math Acc": f"{s.ma_score:.1f}%",
                "Citation Grd": f"{s.cgr_score:.1f}%",
                "Source Cov": f"{s.sc_score:.1f}%",
                "Hallucination": f"{s.hr_score:.1f}%",
                "Recovery": f"{s.rsr_score:.1f}%",
                "Notes": s.notes
            })
        st.dataframe(pd.DataFrame(sc_rows), use_container_width=True, hide_index=True)
    else:
        st.info("Click 'Run Full Benchmark Suite' above to execute the benchmark evaluation and ablation study.")

# ==========================================
# TAB 9: AUDIT TRAIL & HISTORY
# ==========================================
with tabs[8]:
    state = st.session_state.last_state
    if state:
        st.subheader("Step-by-Step Autonomous Execution Trail")
        for step in state.plan:
            st.markdown(f"""
            <div class="audit-card">
                <b>[{step.step_id.upper()}] {step.description}</b><br/>
                <small>Tool Category: <code>{step.tool_category}</code> • Status: <b>{step.status.upper()}</b></small><br/>
                <span>Output: {step.result_summary or 'In Progress'}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Persistent Task History (SQLite)")
    hist_mgr = TaskHistoryManager()
    past_tasks = hist_mgr.get_past_investigations()
    if past_tasks:
        st.dataframe(pd.DataFrame(past_tasks), use_container_width=True, hide_index=True)
    else:
        st.info("No past investigations recorded in SQLite database yet.")

    # Downloadable deliverables
    if state and state.report_markdown_path and Path(state.report_markdown_path).exists():
        st.markdown("---")
        st.subheader("Download Generated Reports")
        d_col1, d_col2 = st.columns(2)
        with d_col1:
            with open(state.report_markdown_path, "r", encoding="utf-8") as f:
                md_bytes = f.read()
            st.download_button(
                "📥 Download Analytical Report (Markdown)",
                data=md_bytes,
                file_name="analytical_report.md",
                mime="text/markdown",
                use_container_width=True
            )
        with d_col2:
            if state.report_pdf_path and Path(state.report_pdf_path).exists():
                with open(state.report_pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                st.download_button(
                    "📥 Download Analytical Report (PDF)",
                    data=pdf_bytes,
                    file_name="analytical_report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

# ==========================================
# TAB 10: DOCUMENT & PROVENANCE INSPECTOR
# ==========================================
with tabs[9]:
    st.subheader("Document Catalog & Chunk Provenance Inspector")
    state = st.session_state.last_state
    if state and state.document_manifest:
        doc_rows = []
        for d in state.document_manifest:
            doc_rows.append({
                "Document ID": d.document_id,
                "Filename": d.file_name,
                "Format": d.file_type.value.upper(),
                "Size (Bytes)": f"{d.file_size_bytes:,}",
                "SHA-256 Checksum": d.content_hash,
                "Extraction Status": d.extraction_status
            })
        st.dataframe(pd.DataFrame(doc_rows), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("Granular Chunk Inspector")
        chunk_data = []
        for c in state.raw_chunks[:25]:
            chunk_data.append({
                "Chunk ID": c.chunk_id,
                "Document": c.file_name,
                "Content Type": c.content_type,
                "Location Provenance": c.location.to_citation_str(),
                "Content Snippet": c.content[:120] + "..." if len(c.content) > 120 else c.content
            })
        st.dataframe(pd.DataFrame(chunk_data), use_container_width=True, hide_index=True)
    else:
        st.info("No documents inspected yet. Launch an investigation to explore chunk provenance.")

# ==========================================
# TAB 11: ENTERPRISE API & SYSTEM STATUS
# ==========================================
with tabs[10]:
    st.subheader("⚡ Enterprise FastAPI REST Microservice")
    st.caption("Headless microservice architecture for programmatic document intelligence, automated CI/CD pipelines, and microservice integration.")

    api_c1, api_c2 = st.columns(2)
    with api_c1:
        st.markdown("""
        #### 📚 Microservice Specifications
        - **Swagger / OpenAPI Documentation:** [`http://localhost:8000/docs`](http://localhost:8000/docs)
        - **Redoc Interactive Explorer:** [`http://localhost:8000/redoc`](http://localhost:8000/redoc)
        - **Core Architecture:** FastAPI + Pydantic v2 + Uvicorn + SQLite WAL
        
        #### 🔗 Available REST Endpoints:
        | Method | Endpoint | Description |
        |---|---|---|
        | `GET` | `/health` | System health check & active database indicator |
        | `POST` | `/api/v1/investigate` | Autonomous investigation runner |
        | `POST` | `/api/v1/scenarios/simulate` | What-if simulation, sensitivity & Monte Carlo |
        | `POST` | `/api/v1/debate` | Multi-Agent Red-Team Debate Council |
        | `GET` | `/api/v1/hitl/queue` | List pending human approvals |
        | `POST` | `/api/v1/hitl/decision` | Submit human override / approval |
        | `GET` | `/api/v1/benchmarks/run` | Execute ADI-Bench v1.0 suite |
        | `GET` | `/api/v1/reports/{report_name}` | Download PDF / Markdown deliverables |
        """)

    with api_c2:
        st.markdown("""
        #### 💻 Launching the Headless Microservice
        ```bash
        # Start server with auto-reload on port 8000
        python scripts/run_api.py --port 8000 --host 0.0.0.0
        ```

        #### 📡 Sample cURL Query:
        ```bash
        curl -X POST "http://localhost:8000/api/v1/scenarios/simulate" \\
             -H "Content-Type: application/json" \\
             -d '{
               "scenario_name": "Flat Segment A",
               "overrides": {"Segment A": 500.0},
               "target_revenue": 1000.0,
               "num_simulations": 500
             }'
        ```
        """)

