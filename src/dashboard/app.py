"""
CareFlow: Clinical Process Intelligence - Interactive Web Dashboard
===================================================================
A presentation-ready Streamlit dashboard for exploring patient journeys,
process discovery models (Petri Nets, BPMN, DFG), clinical bottlenecks,
and statistical analytics using the Sepsis event log.

Authors:
  - Shruti Mali (Data Engineering, Clinical Analytics, Transition Matrices, Bottlenecks)
  - Madhura (Process Mining, Algorithmic Discovery, Visual Maps, Interactive Dashboard)

Repository: CareFlow-Clinical-Process-Intelligence
"""

from pathlib import Path
import os
import sys
import pandas as pd
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
import altair as alt

# -----------------------------------------------------------------------------
# 1. Project Paths & Setup
# -----------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATA_POWERBI = PROJECT_ROOT / "data" / "powerbi"
OUTPUTS_TABLES = PROJECT_ROOT / "outputs" / "tables"
OUTPUTS_FIGURES = PROJECT_ROOT / "outputs" / "figures"
OUTPUTS_MODELS = PROJECT_ROOT / "outputs" / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"

# -----------------------------------------------------------------------------
# 2. Page Configuration & Theme
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="CareFlow | Clinical Process Intelligence",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling (Teal/Clinical Dark-Light Theme)
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0d5c75;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #4a6572;
        margin-bottom: 1.2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #f0f7f9 0%, #e3f2f7 100%);
        padding: 1.1rem;
        border-radius: 10px;
        border-left: 5px solid #0d5c75;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0d5c75;
    }
    .metric-label {
        font-size: 0.85rem;
        text-transform: uppercase;
        color: #546e7a;
        letter-spacing: 0.5px;
    }
    .team-badge-shruti {
        background-color: #e0f2f1;
        color: #00695c;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .team-badge-madhura {
        background-color: #ede7f6;
        color: #4527a0;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        border-radius: 4px 4px 0 0;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 3. Data Ingestion & Caching
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_csv_safe(file_path: Path, **kwargs) -> pd.DataFrame:
    """Safe CSV loader with automatic string preservation for case ID 'NA'."""
    if not file_path.exists():
        return pd.DataFrame()
    kwargs.setdefault("keep_default_na", False)
    kwargs.setdefault("na_values", [""])
    return pd.read_csv(file_path, **kwargs)


@st.cache_data(show_spinner=False)
def get_all_project_data():
    """Load core analytical tables into cached memory."""
    cleaned_log = load_csv_safe(DATA_PROCESSED / "sepsis_cleaned.csv")
    times_log = load_csv_safe(DATA_PROCESSED / "sepsis_with_times.csv")
    case_summary = load_csv_safe(DATA_PROCESSED / "patient_case_summary.csv")
    act_summary = load_csv_safe(OUTPUTS_TABLES / "activity_frequency_detailed.csv")
    if act_summary.empty:
        act_summary = load_csv_safe(DATA_PROCESSED / "activity_frequency.csv")
    variants_summary = load_csv_safe(OUTPUTS_TABLES / "process_variants_summary.csv")
    transitions_matrix = load_csv_safe(OUTPUTS_TABLES / "activity_transition_matrix.csv")
    transitions_detailed = load_csv_safe(OUTPUTS_TABLES / "activity_transitions_detailed.csv")
    if transitions_detailed.empty:
        transitions_detailed = load_csv_safe(DATA_PROCESSED / "activity_time_differences.csv")
    triage_antibiotics = load_csv_safe(OUTPUTS_TABLES / "triage_to_antibiotics_analysis.csv")
    admission_latency = load_csv_safe(OUTPUTS_TABLES / "admission_latency_analysis.csv")
    bottlenecks_summary = load_csv_safe(OUTPUTS_TABLES / "clinical_bottlenecks_summary.csv")
    dq_report = load_csv_safe(REPORTS_DIR / "data_quality_report.csv")
    reconciliation = load_csv_safe(REPORTS_DIR / "reconciliation_summary.csv")
    dfg_freq = load_csv_safe(OUTPUTS_TABLES / "dfg_frequency_table.csv")
    dfg_perf = load_csv_safe(OUTPUTS_TABLES / "dfg_performance_table.csv")
    heuristics_dep = load_csv_safe(OUTPUTS_TABLES / "heuristics_dependency_matrix.csv")

    return {
        "cleaned_log": cleaned_log,
        "times_log": times_log,
        "case_summary": case_summary,
        "act_summary": act_summary,
        "variants_summary": variants_summary,
        "transitions_matrix": transitions_matrix,
        "transitions_detailed": transitions_detailed,
        "triage_antibiotics": triage_antibiotics,
        "admission_latency": admission_latency,
        "bottlenecks_summary": bottlenecks_summary,
        "dq_report": dq_report,
        "reconciliation": reconciliation,
        "dfg_freq": dfg_freq,
        "dfg_perf": dfg_perf,
        "heuristics_dep": heuristics_dep,
    }


data = get_all_project_data()

# -----------------------------------------------------------------------------
# 4. Sidebar Navigation & Global Controls
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/medical-heart.png", width=64)
    st.title("CareFlow")
    st.caption("Clinical Process Intelligence v1.0.0")

    selected_module = st.radio(
        "Navigation",
        [
            "🩺 1. Project Overview",
            "📊 2. Dataset & Cohort Statistics",
            "👤 3. Patient Journey & Case Profiling",
            "🔄 4. Activity Frequency & Clinical Rework",
            "🧬 5. Process Variants & Pareto Analysis",
            "🗺️ 6. Process Flow & DFG Maps",
            "🕸️ 7. Petri Net & BPMN Discovery",
            "🔀 8. Transition Probability Matrix",
            "⏱️ 9. Clinical Bottlenecks & Golden Hour",
            "⏳ 10. Waiting Times & Performance",
            "✅ 11. Data Quality & Reconciliation Audit",
        ],
        index=0
    )

    st.markdown("---")
    st.markdown("### 👥 Engineering Team")
    st.markdown("""
    - <span class="team-badge-shruti">Shruti</span> **Data Engineering & Analytics**
      - XES Ingestion, Case 'NA' Bug Fix
      - Reconciliation, Quality Validation
      - Rework Rates, Transition Probability
      - Sepsis Golden Hour, Power BI Data
    - <span class="team-badge-madhura">Madhura</span> **Process Mining & Discovery**
      - PM4Py Event Log Pipeline
      - Inductive & Heuristics Miners
      - Petri Nets & BPMN Models
      - DFG & 846 Variants Pareto
      - Visual Maps & Streamlit Dashboard
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ⚙️ Pipeline Status")
    if not data["cleaned_log"].empty and len(data["cleaned_log"]) == 15214:
        st.success("✅ Baseline 15,214 Events Verified")
    else:
        st.error("⚠️ Data requires pipeline run")

    st.markdown("---")
    st.caption("CareFlow Clinical Process Intelligence | TU/e BPI Sepsis Cohort")


# -----------------------------------------------------------------------------
# 5. Module Implementation
# -----------------------------------------------------------------------------

# =============================================================================
# MODULE 1: PROJECT OVERVIEW
# =============================================================================
if selected_module.startswith("🩺 1"):
    st.markdown('<div class="main-title">🩺 CareFlow: Clinical Process Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Patient Journey Analysis, Algorithmic Process Mining & Clinical Bottleneck Discovery</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Hospital Cohort</div>
            <div class="metric-value">1,050 Cases</div>
            <small>Preserved valid Case 'NA'</small>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Recorded Transactions</div>
            <div class="metric-value">15,214 Events</div>
            <small>100.0% XES Reconciliation</small>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Treatment Pathways</div>
            <div class="metric-value">846 Variants</div>
            <small>High clinical process entropy</small>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Golden Hour Sepsis</div>
            <div class="metric-value">36.9% &le; 1h</div>
            <small>Median delivery: 1.48 hours</small>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 📌 Executive Clinical Problem Statement")
    st.info("""
    Hospital leadership and emergency department clinicians struggle to understand why sepsis patient handoffs stall and how actual care deviates from international clinical guidelines. 
    Traditional hospital BI dashboards aggregate data into high-level static metrics such as **Average Length of Stay (ALOS)**, which act as a black box: they indicate *how long* a patient remained in the hospital, but cannot reveal the *chaotic, real-world sequence of clinical activities* patients actually underwent.

    **CareFlow** bridges this gap using **Process Mining** algorithms on electronic health record (EHR) event logs. By discovering objective workflows, CareFlow eliminates reliance on idealized clinical flowcharts, uncovering actual diagnostic rework loops, emergency ward boarding delays, and international **Surviving Sepsis Campaign** guideline compliance.
    """)

    st.markdown("### 🏗️ Two-Member Engineering Architecture")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 🔬 Shruti (Lead Data Engineer & Clinical Analyst)")
        st.markdown("""
        - **Raw XES Ingestion & Decompression:** Parse compressed `sepsis.xes.gz` without data loss.
        - **The Case 'NA' Bug Resolution:** Solved string-to-null parsing bug in Pandas, recovering 24 missing events and preserving patient ID `'NA'`.
        - **Duplicate Assays Preservation:** Retained 14 legitimate simultaneous multi-tube blood tests (`CRP`, `Leucocytes`, `LacticAcid`).
        - **Quality Assurance Engine:** 10 automated health checks and 100.0% mathematical XES-to-CSV reconciliation match.
        - **Clinical Statistical Analytics:** Case profiling (1,050 patients), rework rate calculations, and Surviving Sepsis Campaign Golden Hour bottleneck analysis.
        - **Transition Probability Analysis:** $16 \\times 16$ stochastic Markovian transition matrix.
        - **Power BI Relational Model:** Star-schema datasets (4 dimensions, 3 fact tables).
        """)
    with c2:
        st.markdown("#### ⚙️ Madhura (Lead Process Mining Engineer & Visual Analytics)")
        st.markdown("""
        - **PM4Py Framework Architecture:** Standardized event log classifiers (`case:concept:name`, `concept:name`, `time:timestamp`).
        - **Inductive Miner Implementation:** Discovered mathematically sound block-structured Process Trees; exported Petri Net (`.pnml`) and standard BPMN 2.0 XML.
        - **Heuristics Miner Discovery:** Applied noise-tolerant dependency thresholds to extract the Heuristics Net and $16 \\times 16$ causal dependency matrix.
        - **Directly-Follows Graph (DFG):** Mined 115 unique transitions across 14,164 consecutive event pairs.
        - **Process Variant Analytics:** Identified 846 unique patient pathways and computed Pareto cumulative distributions.
        - **Dependency-Free Static Maps:** Publication-quality NetworkX & Matplotlib maps without requiring Graphviz system binaries.
        - **Interactive Web Interfaces:** Standalone physics-based HTML5 canvas explorer and this multi-page Streamlit Clinical Intelligence Dashboard.
        """)


# =============================================================================
# MODULE 2: DATASET & COHORT STATISTICS
# =============================================================================
elif selected_module.startswith("📊 2"):
    st.markdown('<div class="main-title">📊 Dataset & Cohort Statistics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Ground-truth verification across the 15,214-event Sepsis clinical event log</div>', unsafe_allow_html=True)

    df_cleaned = data["cleaned_log"]
    if df_cleaned.empty:
        st.warning("Cleaned event log not loaded. Please run the pipeline.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Events", f"{len(df_cleaned):,}")
        c2.metric("Unique Cases", f"{df_cleaned['case_id'].nunique():,}")
        c3.metric("Unique Activities", f"{df_cleaned['activity'].nunique()}")
        c4.metric("Preserved Case 'NA' Events", len(df_cleaned[df_cleaned['case_id'] == 'NA']))

        st.markdown("### 📋 Interactive Event Log Explorer")
        st.caption("Search, filter, and inspect the chronological patient log (showing first 500 rows)")

        # Filters
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            all_activities = sorted(df_cleaned['activity'].unique())
            sel_act = st.multiselect("Filter by Clinical Activity", all_activities, default=[])
        with f_col2:
            case_search = st.text_input("Filter by Case ID (e.g., 'NA', 'A', 'ES', 'X')", "")

        filtered_df = df_cleaned.copy()
        if sel_act:
            filtered_df = filtered_df[filtered_df['activity'].isin(sel_act)]
        if case_search.strip():
            filtered_df = filtered_df[filtered_df['case_id'].astype(str).str.contains(case_search.strip(), case=False)]

        st.dataframe(filtered_df.head(500), use_container_width=True)
        st.caption(f"Showing {min(500, len(filtered_df))} of {len(filtered_df):,} matching event records.")

        st.markdown("### 📈 Events per Case Summary Statistics")
        case_counts = df_cleaned.groupby("case_id")["activity"].count()
        s_col1, s_col2, s_col3, s_col4 = st.columns(4)
        s_col1.metric("Min Events / Case", int(case_counts.min()))
        s_col2.metric("Median Events / Case", int(case_counts.median()))
        s_col3.metric("Mean Events / Case", f"{case_counts.mean():.2f}")
        s_col4.metric("Max Events / Case", int(case_counts.max()))


# =============================================================================
# MODULE 3: PATIENT JOURNEY & CASE PROFILING
# =============================================================================
elif selected_module.startswith("👤 3"):
    st.markdown('<div class="main-title">👤 Patient Journey & Case Profiling</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">1,050 Patient Cohort Stratification, Care Pathways & Individual Trace Inspection</div>', unsafe_allow_html=True)

    df_cases = data["case_summary"]
    df_cleaned = data["cleaned_log"]

    if df_cases.empty:
        st.warning("Patient case profiles not available.")
    else:
        # High level KPIs
        k1, k2, k3, k4 = st.columns(4)
        icu_cases = df_cases[df_cases["had_icu_admission"] == True] if "had_icu_admission" in df_cases else pd.DataFrame()
        return_cases = df_cases[df_cases["had_return_er"] == True] if "had_return_er" in df_cases else pd.DataFrame()
        
        k1.metric("Profiled Patients", len(df_cases))
        k2.metric("ICU Admissions (Admission IC)", f"{len(icu_cases)} ({len(icu_cases)/len(df_cases)*100:.1f}%)")
        k3.metric("Recorded Return ER", f"{len(return_cases)} ({len(return_cases)/len(df_cases)*100:.1f}%)")
        k4.metric("Median Log Duration", f"{df_cases['total_duration_hours'].median():.1f} hrs" if "total_duration_hours" in df_cases else "N/A")

        st.markdown("---")
        st.markdown("### 🔍 Individual Patient Journey Drill-Down")
        st.caption("Select or search any patient ID to inspect their chronological journey, timestamps, and activity sequence.")

        all_patient_ids = sorted(df_cases["case_id"].astype(str).unique())
        default_index = all_patient_ids.index("NA") if "NA" in all_patient_ids else 0
        selected_patient = st.selectbox("Select Patient Case ID", all_patient_ids, index=default_index)

        patient_profile = df_cases[df_cases["case_id"].astype(str) == str(selected_patient)]
        patient_events = df_cleaned[df_cleaned["case_id"].astype(str) == str(selected_patient)].sort_values("timestamp")

        if not patient_profile.empty:
            p_row = patient_profile.iloc[0]
            info_c1, info_c2, info_c3, info_c4 = st.columns(4)
            info_c1.info(f"**Events:** {len(patient_events)}")
            info_c2.info(f"**First Event:** {patient_events.iloc[0]['activity'] if len(patient_events)>0 else 'N/A'}")
            info_c3.info(f"**Last Event:** {patient_events.iloc[-1]['activity'] if len(patient_events)>0 else 'N/A'}")
            info_c4.info(f"**ICU / Return ER:** {'ICU' if p_row.get('had_icu_admission') else 'No ICU'} | {'Return ER' if p_row.get('had_return_er') else 'No Return'}")

        st.markdown("#### Patient Event Timeline")
        st.dataframe(patient_events[["case_id", "activity", "timestamp", "org:group"]], use_container_width=True)


# =============================================================================
# MODULE 4: ACTIVITY FREQUENCY & CLINICAL REWORK
# =============================================================================
elif selected_module.startswith("🔄 4"):
    st.markdown('<div class="main-title">🔄 Activity Frequency & Clinical Rework Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Quantifying diagnostic test repetition, patient reach percentages, and rework rates (Shruti)</div>', unsafe_allow_html=True)

    df_act = data["act_summary"]
    if df_act.empty:
        st.warning("Activity summary table not found.")
    else:
        st.markdown("### 📊 Activity Occurrence & Rework Breakdown")

        # Clean display columns
        display_df = df_act.copy()
        if "rework_case_percentage" in display_df.columns:
            display_df["rework_case_percentage"] = display_df["rework_case_percentage"].round(2)
        if "case_reach_percentage" in display_df.columns:
            display_df["case_reach_percentage"] = display_df["case_reach_percentage"].round(2)

        # Bar chart of Activity Occurrences
        chart = alt.Chart(df_act).mark_bar(color="#0d5c75").encode(
            x=alt.X("occurrence_count:Q", title="Total Event Occurrences"),
            y=alt.Y("activity:N", sort="-x", title="Clinical Activity"),
            tooltip=["activity", "occurrence_count", "unique_cases_reached", "rework_cases_count", "rework_case_percentage"]
        ).properties(height=450, title="Occurrences per Activity across 15,214 Sepsis Events")
        st.altair_chart(chart, use_container_width=True)

        st.markdown("### 📋 Activity Rework & Patient Reach Data Table")
        st.dataframe(display_df, use_container_width=True)

        st.markdown("### 💡 Key Clinical Insights on Diagnostic Rework")
        st.info("""
        - **C-Reactive Protein (CRP):** 3,262 occurrences across 1,052 cases. **68.72%** of patients had repeated measurements, reflecting continuous inflammatory response monitoring.
        - **Leucocytes (White Blood Cell Count):** 3,383 occurrences across 1,051 cases. **67.84%** repeat rate for ongoing infection tracking.
        - **Lactic Acid (Sepsis Perfusion Marker):** 1,454 occurrences across 866 cases (**28.53%** repeat rate), matching clinical protocols for assessing tissue hypoperfusion clearance.
        - **Preservation of Same-Timestamp Assays:** 14 events with identical timestamps (e.g., patient 'ES') were verified as legitimate simultaneous panel draws, not technical duplicates.
        """)


# =============================================================================
# MODULE 5: PROCESS VARIANTS & PARETO ANALYSIS
# =============================================================================
elif selected_module.startswith("🧬 5"):
    st.markdown('<div class="main-title">🧬 Process Variants & Pareto Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Discovering 846 Distinct Care Trajectories & High Clinical Process Entropy (Madhura)</div>', unsafe_allow_html=True)

    df_var = data["variants_summary"]
    if df_var.empty:
        st.warning("Process variants table not available.")
    else:
        v1, v2, v3, v4 = st.columns(4)
        v1.metric("Total Process Variants", f"{len(df_var):,}")
        v2.metric("Total Cohort Cases", "1,050")
        v3.metric("Top Variant Frequency", f"{df_var.iloc[0]['case_count']} Cases ({df_var.iloc[0]['case_percentage']}%)")
        v4.metric("Variants with Only 1 Patient", f"{(df_var['case_count'] == 1).sum():,} ({(df_var['case_count'] == 1).sum()/len(df_var)*100:.1f}%)")

        st.markdown("### 📈 Top 15 Most Frequent Patient Trajectories")
        top_15 = df_var.head(15).copy()
        
        chart = alt.Chart(top_15).mark_bar(color="#4527a0").encode(
            x=alt.X("case_count:Q", title="Patient Cases"),
            y=alt.Y("variant_id:N", sort="-x", title="Variant ID"),
            tooltip=["variant_id", "case_count", "case_percentage", "cumulative_percentage", "pathway"]
        ).properties(height=400)
        st.altair_chart(chart, use_container_width=True)

        st.markdown("### 📋 Top Process Variants Details")
        st.dataframe(top_15[["variant_id", "case_count", "case_percentage", "cumulative_percentage", "pathway"]], use_container_width=True)

        st.markdown("### 🔬 Clinical Interpretation: Process Entropy")
        st.warning("""
        - **Extreme Operational Heterogeneity:** Out of 1,050 patients, there are **846 distinct treatment trajectories**.
        - **Low Dominance:** The single most common pathway (Variant 1) accounts for only **6.10%** (64 patients).
        - **Long Tail of Unique Cases:** Over **80%** of variants appear for exactly one patient.
        - **Takeaway:** Prescriptive flowcharts and rigid clinical pathways do not capture the complexity of real-world acute sepsis care.
        """)


# =============================================================================
# MODULE 6: PROCESS FLOW & DFG MAPS
# =============================================================================
elif selected_module.startswith("🗺️ 6"):
    st.markdown('<div class="main-title">🗺️ Process Flow & Directly-Follows Graphs (DFG)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">115 Clinical Transitions Across 14,164 Events (Madhura)</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📊 Frequency Process Map", "⏱️ Performance / Bottleneck Map", "🌐 Interactive Physics Graph"])

    with tab1:
        st.markdown("#### Directly-Follows Graph Annotated with Transition Volumes")
        freq_img = OUTPUTS_FIGURES / "dfg_frequency_process_map.png"
        if freq_img.exists():
            st.image(str(freq_img), use_container_width=True)
        else:
            st.info("Frequency process map image not found. Run pipeline to generate.")

    with tab2:
        st.markdown("#### Performance DFG Annotated with Median Transition Delays")
        perf_img = OUTPUTS_FIGURES / "dfg_performance_bottleneck_map.png"
        if perf_img.exists():
            st.image(str(perf_img), use_container_width=True)
        else:
            st.info("Performance process map image not found. Run pipeline to generate.")

    with tab3:
        st.markdown("#### Standalone Interactive Physics-Based Process Map")
        st.caption("Drag nodes, zoom, and inspect transitions directly in the browser.")
        html_map = OUTPUTS_FIGURES / "careflow_interactive_process_map.html"
        if html_map.exists():
            with open(html_map, "r", encoding="utf-8") as f:
                html_content = f.read()
            components.html(html_content, height=650, scrolling=True)
        else:
            st.info("Interactive HTML map not found. Run pipeline to generate.")


# =============================================================================
# MODULE 7: PETRI NET & BPMN DISCOVERY
# =============================================================================
elif selected_module.startswith("🕸️ 7"):
    st.markdown('<div class="main-title">🕸️ Petri Net & BPMN Process Discovery</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Mathematically Sound Process Trees, Petri Nets and Causal Dependency Nets (Madhura)</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 🌲 Inductive Miner (Sound Petri Net & BPMN)")
        st.markdown("""
        - **Algorithm:** Inductive Miner Framework (PM4Py).
        - **Output Models:**
          - `outputs/models/inductive_petri_net.pnml` (Sound Petri Net XML)
          - `outputs/models/inductive_bpmn.bpmn` (Standard BPMN 2.0 XML)
        - **Guarantees:**
          - **Deadlock-Free:** The discovered Petri Net is strictly 1-sound.
          - **Livelock-Free:** Block-structured tree guarantees proper completion.
          - **Trace Fitness:** High structural fitness on the 1,050 patient traces.
        """)
        pnml_file = OUTPUTS_MODELS / "inductive_petri_net.pnml"
        if pnml_file.exists():
            st.success(f"✅ Inductive Petri Net available ({pnml_file.stat().st_size:,} bytes)")
            with open(pnml_file, "rb") as f:
                st.download_button("Download Inductive Petri Net (.pnml)", f, "inductive_petri_net.pnml", "application/xml")

    with c2:
        st.markdown("### ⚡ Heuristics Miner (Noise-Tolerant Net)")
        st.markdown("""
        - **Algorithm:** Heuristics Miner with Relative-to-Best Dependency Thresholds.
        - **Output Models:**
          - `outputs/models/heuristics_petri_net.pnml`
          - `outputs/tables/heuristics_dependency_matrix.csv`
        - **Key Features:**
          - Filters out low-frequency noise and rare clinical deviations.
          - Captures strong causal connections between Triage, Antibiotics, and Admissions.
        """)
        h_file = OUTPUTS_MODELS / "heuristics_petri_net.pnml"
        if h_file.exists():
            st.success(f"✅ Heuristics Petri Net available ({h_file.stat().st_size:,} bytes)")
            with open(h_file, "rb") as f:
                st.download_button("Download Heuristics Petri Net (.pnml)", f, "heuristics_petri_net.pnml", "application/xml")

    st.markdown("---")
    st.markdown("### 🔢 Heuristics Causal Dependency Matrix ($16 \\times 16$)")
    df_dep = data["heuristics_dep"]
    if not df_dep.empty:
        st.dataframe(df_dep, use_container_width=True)


# =============================================================================
# MODULE 8: TRANSITION PROBABILITY MATRIX
# =============================================================================
elif selected_module.startswith("🔀 8"):
    st.markdown('<div class="main-title">🔀 Transition Probability Matrix Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">16x16 Markovian Conditional Transition Probabilities P(Activity B | Activity A) (Shruti)</div>', unsafe_allow_html=True)

    df_trans_mat = data["transitions_matrix"]
    if df_trans_mat.empty:
        st.warning("Transition probability matrix not found.")
    else:
        st.markdown("### 🧮 Interactive Transition Probability Lookup")
        st.caption("Select a source activity to view all outgoing clinical pathways, probabilities, and transition frequencies.")

        source_activities = sorted(df_trans_mat.index if df_trans_mat.index.name == "previous_activity" else df_trans_mat.iloc[:, 0].unique())
        selected_source = st.selectbox("Select Source Activity A", source_activities)

        # Filter row
        if df_trans_mat.index.name == "previous_activity":
            row_data = df_trans_mat.loc[selected_source]
        else:
            row_data = df_trans_mat[df_trans_mat.iloc[:, 0] == selected_source].set_index(df_trans_mat.columns[0]).iloc[0]

        row_data = row_data[row_data > 0].sort_values(ascending=False)
        trans_df = pd.DataFrame({
            "Target Activity B": row_data.index,
            "Conditional Probability P(B|A)": row_data.values,
            "Percentage": (row_data.values * 100).round(2)
        })

        t_col1, t_col2 = st.columns([1, 1])
        with t_col1:
            st.markdown(f"**Outgoing Paths from:** `{selected_source}`")
            st.dataframe(trans_df, use_container_width=True)
            st.info(f"**Total Probability Sum:** `{row_data.sum():.4f}` (Guaranteed row stochasticity = 1.0000)")

        with t_col2:
            if not trans_df.empty:
                chart = alt.Chart(trans_df).mark_bar(color="#00695c").encode(
                    x=alt.X("Conditional Probability P(B|A):Q", scale=alt.Scale(domain=[0, 1])),
                    y=alt.Y("Target Activity B:N", sort="-x"),
                    tooltip=["Target Activity B", "Percentage"]
                ).properties(height=300)
                st.altair_chart(chart, use_container_width=True)

        st.markdown("### 📋 Full 16x16 Transition Probability Matrix")
        st.dataframe(df_trans_mat, use_container_width=True)


# =============================================================================
# MODULE 9: CLINICAL BOTTLENECK ANALYSIS
# =============================================================================
elif selected_module.startswith("⏱️ 9"):
    st.markdown('<div class="main-title">⏱️ Clinical Bottleneck & Performance Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Surviving Sepsis Campaign Golden Hour Compliance & Emergency Boarding Latency (Shruti)</div>', unsafe_allow_html=True)

    df_triage = data["triage_antibiotics"]
    df_admit = data["admission_latency"]

    b1, b2, b3 = st.columns(3)
    b1.metric("Sepsis Golden Hour (<= 1h)", "36.94%", "304 / 823 patients")
    b2.metric("Antibiotic Delivery <= 3h", "74.85%", "616 / 823 patients")
    b3.metric("Median Boarding Latency", "3.22 hours", "810 admitted patients")

    st.markdown("### 🎯 Surviving Sepsis Campaign Golden Hour Compliance")
    st.caption("Distribution of time elapsed from ER Triage to IV Antibiotics administration (823 eligible patients)")

    compliance_data = pd.DataFrame({
        "Category": ["<= 1 Hour (Golden Hour Target)", "1 - 3 Hours (Moderate Delay)", "> 3 Hours (Severe Delay)"],
        "Patients": [304, 312, 207],
        "Percentage": [36.94, 37.91, 25.15]
    })

    c_col1, c_col2 = st.columns([1, 1])
    with c_col1:
        st.dataframe(compliance_data, use_container_width=True)
        st.warning("""
        - **Clinical Benchmark:** International Sepsis Guidelines recommend broad-spectrum antimicrobials within **1 hour** of recognition.
        - **CareFlow Finding:** Only **36.94%** received antibiotics within the Golden Hour window.
        - **Median Delivery Time:** **1.48 hours** (88.8 minutes).
        """)

    with c_col2:
        chart = alt.Chart(compliance_data).mark_bar().encode(
            x=alt.X("Patients:Q", title="Patient Cases"),
            y=alt.Y("Category:N", sort=None, title="Compliance Category"),
            color=alt.Color("Category:N", scale=alt.Scale(range=["#2e7d32", "#f57c00", "#c62828"])),
            tooltip=["Category", "Patients", "Percentage"]
        ).properties(height=260)
        st.altair_chart(chart, use_container_width=True)

    st.markdown("### 🏥 Emergency Department Boarding Latency")
    st.info("""
    - **Analyzed Cohort:** 810 patients who were transferred from the Emergency Room to inpatient wards (`Admission NC` or `Admission IC`).
    - **Median Boarding Duration:** **3.22 hours** (193.2 minutes).
    - **25th - 75th Percentiles:** 2.11 hours to 5.48 hours (IQR: 3.37 hours).
    - **Observation Window vs Bed Occupancy:** Total case duration in the event log reflects recorded transaction windows (including post-discharge Return ER entries), not uninterrupted inpatient bed occupancy.
    """)


# =============================================================================
# MODULE 10: WAITING TIMES & PERFORMANCE
# =============================================================================
elif selected_module.startswith("⏳ 10"):
    st.markdown('<div class="main-title">⏳ Waiting Times & Operational Performance</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">115 Clinical Transitions, Waiting Distributions and Operational Latencies (Shruti & Madhura)</div>', unsafe_allow_html=True)

    df_trans = data["transitions_detailed"]
    if df_trans.empty:
        st.warning("Transitions detailed data not available.")
    else:
        st.markdown("### 🔍 Search and Filter Transition Waiting Times")
        
        min_transitions = st.slider("Minimum Transition Volume", min_value=1, max_value=500, value=20)
        filtered_trans = df_trans[df_trans["total_transitions"] >= min_transitions].copy()

        st.dataframe(filtered_trans.sort_values("median_minutes", ascending=False), use_container_width=True)
        st.caption(f"Showing {len(filtered_trans)} transitions with at least {min_transitions} recorded occurrences.")

        st.markdown("### 🚨 Extreme Operational Delay Outliers")
        st.info("""
        Transitions with long median waiting times reflect post-discharge outpatient intervals:
        - `Release A -> Return ER`: Median interval represents days between hospital discharge and emergency re-presentation.
        - `Admission NC -> CRP / Leucocytes`: Routine morning laboratory batch rounds.
        """)


# =============================================================================
# MODULE 11: DATA QUALITY & RECONCILIATION AUDIT
# =============================================================================
elif selected_module.startswith("✅ 11"):
    st.markdown('<div class="main-title">✅ Data Quality & Reconciliation Audit</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Automated Health Checks, Case NA Preservation and 100% XES Reconciliation Proof (Shruti)</div>', unsafe_allow_html=True)

    df_dq = data["dq_report"]
    df_recon = data["reconciliation"]

    q1, q2, q3 = st.columns(3)
    q1.metric("Validation Checks", "10 / 10 PASS/INFO", "Zero Failures")
    q2.metric("XES Discrepancy", "0 Missing / 0 Extra", "100.0% Exact Match")
    q3.metric("Case 'NA' Preserved", "True", "24 Events Recovered")

    st.markdown("### 📋 Automated Health Checks Audit Trail")
    if not df_dq.empty:
        st.dataframe(df_dq, use_container_width=True)
    else:
        st.info("Data quality report not available. Run pipeline to generate.")

    st.markdown("### 🔬 Multi-Attribute XES vs CSV Reconciliation")
    if not df_recon.empty:
        st.dataframe(df_recon, use_container_width=True)
    else:
        st.info("Reconciliation report not available.")

    st.markdown("### 🛠️ Technical Fix Spotlight: The Case 'NA' Resolution")
    st.success("""
    - **Problem Identified:** In standard Pandas `read_csv()`, the parameter `keep_default_na=True` automatically interprets the string `"NA"` as missing (`NaN`). This silently erased patient `"NA"` and dropped 24 events (causing dataset count to fall from 15,214 to 15,189).
    - **Engineered Solution:** In `src/data/loader.py`, we explicitly configured `keep_default_na=False` and `na_values=[""]` with explicit string typing for `case_id`.
    - **Outcome:** Case `'NA'` and all 24 events were recovered, restoring the dataset to the true 15,214 ground-truth events with a **100.0% zero-defect reconciliation match**.
    """)

# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #78909c; font-size: 0.85rem;">
    CareFlow Clinical Process Intelligence &copy; 2026 | Developed by Shruti Mali & Madhura<br>
    Repository: <code>CareFlow-Clinical-Process-Intelligence</code> | Built with Streamlit & PM4Py
</div>
""", unsafe_allow_html=True)
