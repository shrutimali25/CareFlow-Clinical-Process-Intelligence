"""
CareFlow - Master End-to-End Pipeline Runner
Executes the full clinical process mining and analytics pipeline from raw XES to Power BI.
Authors: Shruti (Member 1 - Data Engineering) & Madhura (Member 2 - Process Mining)
"""

import sys
import time
import tracemalloc
from pathlib import Path
import pandas as pd

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Module imports
from src.data.loader import load_event_log, CASE_COL, ACTIVITY_COL, TIMESTAMP_COL
from src.data.convert_xes import convert_xes_to_csv
from src.data.cleaner import clean_event_log
from src.data.time_features import compute_time_features
from src.validation.validator import validate_dataset
from src.validation.reconciliation import reconcile_datasets
from src.process_mining.log_manager import create_pm4py_event_log
from src.process_mining.inductive_miner import run_inductive_miner
from src.process_mining.heuristics_miner import run_heuristics_miner
from src.process_mining.dfg_miner import run_dfg_discovery
from src.process_mining.variants_miner import run_variants_mining
from src.visualization.process_map import (
    plot_frequency_dfg,
    plot_performance_dfg,
    plot_variants_distribution
)
from src.visualization.interactive_map import generate_interactive_html_map
from src.analysis.activity_summary import generate_activity_summary
from src.analysis.case_profiler import generate_case_profiles
from src.analysis.transitions_analysis import generate_transitions_analysis
from src.analysis.bottleneck_analysis import analyze_clinical_bottlenecks
from src.prepare_powerbi_data import prepare_powerbi_datasets


def print_stage_header(stage_nr: int, title: str):
    print("\n" + "=" * 70)
    print(f"  STAGE {stage_nr}: {title.upper()}")
    print("=" * 70)


def run_complete_pipeline():
    total_start = time.perf_counter()
    tracemalloc.start()

    print("\n" + "#" * 70)
    print("#  CAREFLOW: PATIENT JOURNEY ANALYSIS USING PROCESS MINING")
    print("#  End-to-End Reproducibility & Execution Pipeline")
    print("#" * 70)

    # File paths
    raw_xes = PROJECT_ROOT / "data" / "raw" / "sepsis.xes.gz"
    raw_csv = PROJECT_ROOT / "data" / "processed" / "sepsis_event_log.csv"
    cleaned_csv = PROJECT_ROOT / "data" / "processed" / "sepsis_cleaned.csv"
    times_csv = PROJECT_ROOT / "data" / "processed" / "sepsis_with_times.csv"
    reports_dir = PROJECT_ROOT / "reports"
    models_dir = PROJECT_ROOT / "outputs" / "models"
    tables_dir = PROJECT_ROOT / "outputs" / "tables"
    figures_dir = PROJECT_ROOT / "outputs" / "figures"
    pbi_dir = PROJECT_ROOT / "data" / "powerbi"

    # -------------------------------------------------------------------------
    # STAGE 1: Dataset Verification & XES to CSV Conversion
    # -------------------------------------------------------------------------
    print_stage_header(1, "Dataset Ingestion & XES-to-CSV Conversion")
    t0 = time.perf_counter()
    if not raw_csv.exists():
        print("CSV event log not found. Converting from raw XES...")
        convert_xes_to_csv(raw_xes, raw_csv)
    else:
        print(f"Verified raw CSV exists: {raw_csv.name} ({raw_csv.stat().st_size:,} bytes)")
    print(f"Stage 1 Duration: {time.perf_counter() - t0:.2f}s")

    # -------------------------------------------------------------------------
    # STAGE 2: Data Cleaning & Case ID 'NA' Preservation
    # -------------------------------------------------------------------------
    print_stage_header(2, "Data Cleaning & Timestamp Standardization")
    t0 = time.perf_counter()
    clean_metrics = clean_event_log(raw_csv, cleaned_csv)
    assert clean_metrics["cleaned_rows"] == 15214, f"Expected 15,214 events, got {clean_metrics['cleaned_rows']}"
    assert clean_metrics["unique_cases"] == 1050, f"Expected 1,050 cases, got {clean_metrics['unique_cases']}"
    assert clean_metrics["unique_activities"] == 16, f"Expected 16 activities, got {clean_metrics['unique_activities']}"
    assert clean_metrics["has_case_NA"], "Case 'NA' was lost during cleaning!"
    assert clean_metrics["case_NA_event_count"] == 24, "Case 'NA' event count mismatch!"
    print(f"Stage 2 Duration: {time.perf_counter() - t0:.2f}s | Verified: 15,214 events, 1,050 cases, Case 'NA' preserved")

    # -------------------------------------------------------------------------
    # STAGE 3: Time Features & Transition Sequencing
    # -------------------------------------------------------------------------
    print_stage_header(3, "Time Features & Sequential Transition Sequencing")
    t0 = time.perf_counter()
    time_metrics = compute_time_features(cleaned_csv, times_csv)
    assert time_metrics["total_events"] == 15214
    assert time_metrics["unique_cases"] == 1050
    assert time_metrics["first_events_count"] == 1050, "Expected exactly 1,050 initial events"
    assert time_metrics["negative_elapsed_times"] == 0, "Found negative elapsed times!"
    assert time_metrics["cases_in_chronological_order"] == 1050, "Trace monotonicity violated!"
    print(f"Stage 3 Duration: {time.perf_counter() - t0:.2f}s | Verified: 14,164 transitions (15,214 - 1,050), 0 negative times")

    # -------------------------------------------------------------------------
    # STAGE 4: Data Quality Validation Checks
    # -------------------------------------------------------------------------
    print_stage_header(4, "Data Quality & Integrity Auditing")
    t0 = time.perf_counter()
    val_df = validate_dataset(times_csv, reports_dir)
    assert "FAIL" not in val_df["Status"].values, "Data quality check failed!"
    print(f"Stage 4 Duration: {time.perf_counter() - t0:.2f}s | All validation checks: PASS / INFO")

    # -------------------------------------------------------------------------
    # STAGE 5: Multi-Attribute Reconciliation (XES vs CSV)
    # -------------------------------------------------------------------------
    print_stage_header(5, "XES vs CSV Full Reconciliation")
    t0 = time.perf_counter()
    reconcile_df = reconcile_datasets(raw_xes, times_csv, reports_dir)
    metric_map = dict(zip(reconcile_df["Metric"], reconcile_df["Value"]))
    assert metric_map.get("Missing event occurrences") == "0", "Discrepancy: Missing events detected!"
    assert metric_map.get("Extra event occurrences") == "0", "Discrepancy: Extra events detected!"
    assert metric_map.get("Reconciliation Match %") == "100.0%", "Reconciliation match is not 100%!"
    print(f"Stage 5 Duration: {time.perf_counter() - t0:.2f}s | Reconciliation Match: 100.0% (Zero discrepancies)")

    # -------------------------------------------------------------------------
    # STAGE 6: PM4Py Process Mining Discovery
    # -------------------------------------------------------------------------
    print_stage_header(6, "PM4Py Process Mining Models & Discovery")
    t0 = time.perf_counter()
    log_df, log_stats = create_pm4py_event_log(cleaned_csv)
    ind_metrics = run_inductive_miner(log_df, models_dir)
    heu_metrics = run_heuristics_miner(log_df, models_dir, tables_dir)
    dfg_metrics = run_dfg_discovery(log_df, tables_dir)
    var_metrics = run_variants_mining(log_df, tables_dir)

    assert ind_metrics["petri_net_places"] == 39
    assert ind_metrics["petri_net_transitions"] == 50
    assert ind_metrics["bpmn_nodes"] == 62
    assert heu_metrics["petri_net_places"] == 33
    assert dfg_metrics["total_transitions"] == 14164
    assert dfg_metrics["unique_edges"] == 115
    assert var_metrics["unique_variants"] == 846
    assert var_metrics["total_cases"] == 1050
    print(f"Stage 6 Duration: {time.perf_counter() - t0:.2f}s | Discovered: Inductive Petri Net, BPMN, Heuristics Net, DFG (115 edges), 846 variants")

    # -------------------------------------------------------------------------
    # STAGE 7: Process Visualizations Generation
    # -------------------------------------------------------------------------
    print_stage_header(7, "Process Visualizations (Static & Interactive)")
    t0 = time.perf_counter()
    freq_df = pd.read_csv(tables_dir / "dfg_frequency_table.csv")
    perf_df = pd.read_csv(tables_dir / "dfg_performance_table.csv")
    var_df = pd.read_csv(tables_dir / "process_variants_summary.csv")

    f1 = plot_frequency_dfg(freq_df, figures_dir / "dfg_frequency_process_map.png")
    f2 = plot_performance_dfg(perf_df, figures_dir / "dfg_performance_bottleneck_map.png")
    f3 = plot_variants_distribution(var_df, figures_dir / "top_variants_distribution.png")
    f4 = generate_interactive_html_map(freq_df, perf_df, figures_dir / "careflow_interactive_process_map.html")
    assert f1.exists() and f2.exists() and f3.exists() and f4.exists()
    print(f"Stage 7 Duration: {time.perf_counter() - t0:.2f}s | Visual maps exported to {figures_dir.name}/")

    # -------------------------------------------------------------------------
    # STAGE 8: Advanced Process Analytics & Clinical Insights
    # -------------------------------------------------------------------------
    print_stage_header(8, "Advanced Process Analytics & Clinical Insights")
    t0 = time.perf_counter()
    act_summary = generate_activity_summary(times_csv, PROJECT_ROOT / "data" / "processed" / "activity_frequency.csv", tables_dir)
    case_summary = generate_case_profiles(times_csv, PROJECT_ROOT / "data" / "processed" / "patient_case_summary.csv", tables_dir)
    trans_summary = generate_transitions_analysis(times_csv, PROJECT_ROOT / "data" / "processed" / "activity_time_differences.csv", tables_dir)
    bot_summary = analyze_clinical_bottlenecks(times_csv, tables_dir)

    assert len(act_summary) == 16
    assert act_summary["total_occurrences"].sum() == 15214
    assert len(case_summary) == 1050
    assert len(trans_summary) == 115
    assert trans_summary["total_transitions"].sum() == 14164
    assert bot_summary["triage_to_antibiotics_cases"] == 823
    assert bot_summary["admission_cases"] == 810
    print(f"Stage 8 Duration: {time.perf_counter() - t0:.2f}s | Computed: Rework rates, Case profiles, Transition matrix, Sepsis bottlenecks")

    # -------------------------------------------------------------------------
    # STAGE 9: Power BI Star-Schema Datasets Preparation
    # -------------------------------------------------------------------------
    print_stage_header(9, "Power BI Star-Schema Data Model Preparation")
    t0 = time.perf_counter()
    pbi_counts = prepare_powerbi_datasets(
        PROJECT_ROOT / "data" / "processed",
        tables_dir,
        reports_dir,
        pbi_dir
    )
    assert pbi_counts["fact_event_log"] == 15214
    assert pbi_counts["dim_patient_cases"] == 1050
    assert pbi_counts["dim_activities"] == 16
    assert pbi_counts["fact_transitions"] == 115
    assert pbi_counts["dim_variants"] == 846
    assert pbi_counts["fact_bottlenecks"] == 1050
    assert pbi_counts["dim_data_quality"] == 10
    print(f"Stage 9 Duration: {time.perf_counter() - t0:.2f}s | Exported 7 Star-Schema tables to {pbi_dir.name}/")

    # -------------------------------------------------------------------------
    # PIPELINE EXECUTION SUMMARY & BENCHMARKS
    # -------------------------------------------------------------------------
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    total_elapsed = time.perf_counter() - total_start

    print("\n" + "=" * 70)
    print("  CAREFLOW PIPELINE EXECUTION SUMMARY & RESOURCE BENCHMARK")
    print("=" * 70)
    print(f"  Status:                    SUCCESS (100% Verified)")
    print(f"  Total Execution Time:      {total_elapsed:.2f} seconds ({total_elapsed/60:.2f} minutes)")
    print(f"  Current Memory In-Use:     {current_mem / (1024 * 1024):.2f} MB")
    print(f"  Peak Memory Consumption:   {peak_mem / (1024 * 1024):.2f} MB")
    print(f"  Target RAM Envelope:       < 500 MB (Fully compatible with 8 GB RAM laptop)")
    print(f"  Total Events Processed:    15,214 events")
    print(f"  Total Patient Cases:       1,050 cases (Case 'NA' verified)")
    print(f"  Clinical Activities:       16 activities")
    print(f"  Process Transitions:       14,164 transitions (115 unique pairs)")
    print(f"  Process Variants:          846 unique pathways")
    print(f"  Reconciliation Match:      100.0% (Zero missing or extra records)")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_complete_pipeline()
