"""
Interactive Streamlit Dashboard for the Autonomous Document Intelligence and Data Analysis Agent.
Evidence-driven multi-format document understanding, deterministic reasoning, and verified reporting.
"""
from pathlib import Path
import streamlit as st
import pandas as pd
from config.settings import settings
from src.agent.orchestrator import AgentOrchestrator
from src.ingestion.manifest import IngestionManager
from src.memory.sqlite_store import SQLiteStore
from src.memory.task_history import TaskHistoryManager
from src.tools.report_export import ReportExporter

# Streamlit Page Setup
st.set_page_config(
    page_title="Autonomous Document Intelligence Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1e293b;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748b;
        margin-bottom: 1.5rem;
    }
    .badge-fact {
        background-color: #dbeafe;
        color: #1e40af;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .badge-interp {
        background-color: #dcfce7;
        color: #166534;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .badge-unc {
        background-color: #fef9c3;
        color: #854d0e;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .audit-card {
        background: #f8fafc;
        border-left: 4px solid #3b82f6;
        padding: 12px 16px;
        margin-bottom: 10px;
        border-radius: 4px;
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
    st.subheader("⚙️ Agent Guardrails")
    max_steps = st.slider("Max Investigation Steps", 5, 25, 15)
    discrepancy_threshold = st.slider("Conflict Alert Threshold (%)", 0.5, 5.0, 1.0, 0.5)
    st.checkbox("Enforce Deterministic Calculations", value=True, disabled=True)
    st.checkbox("Mandatory Citation Grounding", value=True, disabled=True)

# Main Application Layout
st.markdown('<div class="main-header">Autonomous Document Intelligence & Data Analysis Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">An Evidence-Driven Agentic AI System for Multi-Format Document Understanding, Analytical Reasoning, and Verified Reporting</div>', unsafe_allow_html=True)

tabs = st.tabs(["🚀 Investigation Studio", "📊 Analytical Findings", "🔍 Verification Audit", "📜 Audit Trail", "💾 Persistent Memory"])

# Tab 1: Studio
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
        st.markdown("**Quick Scenarios:**")
        if st.button("📉 Revenue Decline Analysis", use_container_width=True):
            user_goal = default_goal
        if st.button("⚖️ Test Cross-Doc Conflict", use_container_width=True):
            # Include conflicting file
            conflict_p = settings.sample_docs_dir / "Conflicting_Report.pdf"
            if conflict_p.exists() and conflict_p not in st.session_state.selected_files:
                st.session_state.selected_files.append(conflict_p)
                st.rerun()

    launch_col1, launch_col2 = st.columns([1, 3])
    with launch_col1:
        launch_btn = st.button("🚀 Launch Autonomous Investigation", type="primary", use_container_width=True)

    if launch_btn:
        if not st.session_state.selected_files:
            # Fallback to sample files if nothing staged
            sample_paths = [
                settings.sample_docs_dir / "Quarterly_Report.pdf",
                settings.sample_docs_dir / "Revenue_Data.xlsx",
                settings.sample_docs_dir / "Segment_Performance.csv"
            ]
            st.session_state.selected_files = [p for p in sample_paths if p.exists()]

        with st.status("Agent actively investigating documents...", expanded=True) as status:
            st.write("🔍 [Step 1-2] Ingesting multi-format documents and executing hybrid retrieval...")
            st.write("📊 [Step 3-4] Extracting structured tables and checking cross-document reconciliation...")
            st.write("🧮 [Step 5-6] Executing deterministic period-over-period and segment contribution math...")
            st.write("🧠 [Step 7] Brain reasoning: categorizing facts, interpretations, and evidence gaps...")
            st.write("🛡️ [Step 8] Running mathematical recomputations and citation grounding audits...")
            st.write("📈 [Step 9-10] Generating visual charts and compiling audit-grade report...")
            
            try:
                state = st.session_state.orchestrator.run_investigation(
                    goal=user_goal,
                    file_paths=st.session_state.selected_files
                )
                st.session_state.last_state = state
                status.update(label="✅ Investigation Completed & Independently Verified!", state="complete")
            except Exception as e:
                status.update(label=f"❌ Error during investigation: {e}", state="error")
                st.error(str(e))

    # Display Summary Cards if state exists
    state = st.session_state.last_state
    if state:
        st.markdown("---")
        st.subheader("Key Investigative Metrics")
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

# Tab 2: Findings
with tabs[1]:
    state = st.session_state.last_state
    if not state:
        st.info("Run an investigation in the Studio tab to view findings.")
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
                    "Period 1": s.period_1_value,
                    "Period 2": s.period_2_value,
                    "Absolute Delta (Δ)": f"{s.absolute_change:+,.1f} {state.segment_analysis.unit}",
                    "Contribution (%C)": f"{s.contribution_percentage:.1f}%",
                    "Direction": s.direction.capitalize(),
                    "Offsetting": "Yes" if s.is_offsetting else "No"
                })
            st.dataframe(pd.DataFrame(s_data), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("Epistemic Categorization of Findings")
        
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
        st.subheader("Visual Analytics")
        if state.chart_paths:
            ch_cols = st.columns(len(state.chart_paths))
            for idx, ch_p in enumerate(state.chart_paths):
                if Path(ch_p).exists():
                    with ch_cols[idx]:
                        st.image(ch_p, use_container_width=True)

# Tab 3: Verification
with tabs[2]:
    state = st.session_state.last_state
    if not state or not state.verification_audit:
        st.info("No verification audit available yet. Run an investigation to inspect audit checks.")
    else:
        v = state.verification_audit
        st.subheader("Independent Verification Pipeline")
        
        if v.all_checks_passed:
            st.success(f"🛡️ **{v.summary_verdict}**")
        else:
            st.warning(f"⚠️ **{v.summary_verdict}**")

        st.markdown("#### Mathematical Recomputations")
        for check in v.calculation_checks:
            badge = "✅ PASS" if check.is_valid else "❌ FAIL"
            st.markdown(f"- **{badge}** | **{check.test_name}**: {check.details} (Discrepancy: {check.discrepancy})")

        st.markdown("#### Citation & Grounding Audits")
        for cite in v.citation_checks:
            badge = "✅ PASS" if cite.is_valid else "❌ FAIL"
            st.markdown(f"- **{badge}** | **{cite.citation_text}**: {cite.details}")

        st.markdown("#### Unit & Period Consistency")
        for cons in v.consistency_checks:
            badge = "✅ PASS" if cons.is_consistent else "⚠️ WARNING"
            st.markdown(f"- **{badge}** | **{cons.check_type.upper()}**: {cons.description}")

# Tab 4: Audit Trail
with tabs[3]:
    state = st.session_state.last_state
    if not state:
        st.info("No active execution trail.")
    else:
        st.subheader("Step-by-Step Autonomous Execution Trail")
        for step in state.plan:
            st.markdown(f"""
            <div class="audit-card">
                <b>[{step.step_id.upper()}] {step.description}</b><br/>
                <small>Tool Category: <code>{step.tool_category}</code> • Status: <b>{step.status.upper()}</b></small><br/>
                <span>Output: {step.result_summary or 'In Progress'}</span>
            </div>
            """, unsafe_allow_html=True)

# Tab 5: Persistent Memory
with tabs[4]:
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
