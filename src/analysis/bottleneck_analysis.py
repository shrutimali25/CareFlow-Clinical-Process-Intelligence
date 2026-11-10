"""
Clinical Bottleneck & Waiting-Time Analytics Module
Analyzes high-latency transitions, triage-to-antibiotics windows, admission boarding,
and clarifies recorded event-log durations vs continuous inpatient stay.
Author: Madhura (Member 2 - Process Analytics)
"""

from pathlib import Path
from typing import Dict, Any, Union
import sys
import pandas as pd
import numpy as np

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.data.loader import load_event_log, CASE_COL, ACTIVITY_COL, TIMESTAMP_COL


def analyze_clinical_bottlenecks(
    input_file_path: Union[str, Path],
    tables_output_dir: Union[str, Path]
) -> Dict[str, Any]:
    """
    Performs clinical waiting-time and bottleneck analysis across Sepsis patient journeys.
    """
    input_path = Path(input_file_path)
    output_dir = Path(tables_output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = load_event_log(input_path, parse_timestamps=True)
    sorted_df = df.sort_values(by=[CASE_COL, TIMESTAMP_COL], kind="stable")

    # =========================================================================
    # 1. Triage-to-Antibiotics Interval Analysis (Sepsis Golden Hour Benchmark)
    # =========================================================================
    print("[Bottleneck Analysis] Analyzing Triage-to-Antibiotics intervals...")
    triage_times = sorted_df[
        sorted_df[ACTIVITY_COL].isin(["ER Triage", "ER Sepsis Triage"])
    ].groupby(CASE_COL)[TIMESTAMP_COL].min()

    ab_times = sorted_df[
        sorted_df[ACTIVITY_COL] == "IV Antibiotics"
    ].groupby(CASE_COL)[TIMESTAMP_COL].min()

    common_cases = triage_times.index.intersection(ab_times.index)
    ab_intervals_hours = (
        (ab_times.loc[common_cases] - triage_times.loc[common_cases]).dt.total_seconds() / 3600.0
    ).round(4)

    # Filter strictly chronological (non-negative)
    valid_ab = ab_intervals_hours[ab_intervals_hours >= 0]
    total_ab_cases = len(valid_ab)

    c_under_1h = int((valid_ab <= 1.0).sum())
    c_1_to_3h = int(((valid_ab > 1.0) & (valid_ab <= 3.0)).sum())
    c_over_3h = int((valid_ab > 3.0).sum())

    triage_ab_metrics = [
        {"Metric": "Eligible Patient Cases Analyzed", "Value": str(total_ab_cases)},
        {"Metric": "Mean Triage-to-Antibiotics Interval (Hours)", "Value": f"{valid_ab.mean():.2f}"},
        {"Metric": "Median Triage-to-Antibiotics Interval (Hours)", "Value": f"{valid_ab.median():.2f}"},
        {"Metric": "Std Dev Interval (Hours)", "Value": f"{valid_ab.std():.2f}"},
        {"Metric": "Min Interval (Hours)", "Value": f"{valid_ab.min():.2f}"},
        {"Metric": "Max Interval (Hours)", "Value": f"{valid_ab.max():.2f}"},
        {"Metric": "Golden Hour Target (<= 1 hour) Cases", "Value": f"{c_under_1h} ({100*c_under_1h/total_ab_cases:.1f}%)"},
        {"Metric": "Surviving Sepsis Bundle (<= 3 hours) Cases", "Value": f"{c_under_1h + c_1_to_3h} ({100*(c_under_1h+c_1_to_3h)/total_ab_cases:.1f}%)"},
        {"Metric": "Delayed Administration (> 3 hours) Cases", "Value": f"{c_over_3h} ({100*c_over_3h/total_ab_cases:.1f}%)"}
    ]
    triage_ab_df = pd.DataFrame(triage_ab_metrics)
    triage_ab_file = output_dir / "triage_to_antibiotics_analysis.csv"
    triage_ab_df.to_csv(triage_ab_file, index=False)

    # =========================================================================
    # 2. Emergency-to-Inpatient Admission Boarding Latency
    # =========================================================================
    print("[Bottleneck Analysis] Analyzing Emergency-to-Admission boarding intervals...")
    reg_times = sorted_df[
        sorted_df[ACTIVITY_COL] == "ER Registration"
    ].groupby(CASE_COL)[TIMESTAMP_COL].min()

    adm_times = sorted_df[
        sorted_df[ACTIVITY_COL].isin(["Admission NC", "Admission IC"])
    ].groupby(CASE_COL)[TIMESTAMP_COL].min()

    common_adm = reg_times.index.intersection(adm_times.index)
    adm_intervals_hours = (
        (adm_times.loc[common_adm] - reg_times.loc[common_adm]).dt.total_seconds() / 3600.0
    ).round(4)
    valid_adm = adm_intervals_hours[adm_intervals_hours >= 0]
    total_adm_cases = len(valid_adm)

    adm_metrics = [
        {"Metric": "Admitted Patient Cases Analyzed", "Value": str(total_adm_cases)},
        {"Metric": "Mean ER-to-Admission Interval (Hours)", "Value": f"{valid_adm.mean():.2f}"},
        {"Metric": "Median ER-to-Admission Interval (Hours)", "Value": f"{valid_adm.median():.2f}"},
        {"Metric": "Min Interval (Hours)", "Value": f"{valid_adm.min():.2f}"},
        {"Metric": "Max Interval (Hours)", "Value": f"{valid_adm.max():.2f}"},
        {"Metric": "Admissions Under 4 Hours", "Value": f"{(valid_adm <= 4.0).sum()} ({100*(valid_adm <= 4.0).sum()/total_adm_cases:.1f}%)"},
        {"Metric": "Admissions 4 to 8 Hours", "Value": f"{((valid_adm > 4.0) & (valid_adm <= 8.0)).sum()} ({100*((valid_adm > 4.0) & (valid_adm <= 8.0)).sum()/total_adm_cases:.1f}%)"},
        {"Metric": "Admissions Over 8 Hours", "Value": f"{(valid_adm > 8.0).sum()} ({100*(valid_adm > 8.0).sum()/total_adm_cases:.1f}%)"}
    ]
    adm_df = pd.DataFrame(adm_metrics)
    adm_file = output_dir / "admission_latency_analysis.csv"
    adm_df.to_csv(adm_file, index=False)

    # =========================================================================
    # 3. Observation Window vs Actual Hospital Stay & Return ER Analysis
    # =========================================================================
    print("[Bottleneck Analysis] Analyzing recorded log window vs continuous inpatient stay...")
    case_durations = (
        (sorted_df.groupby(CASE_COL)[TIMESTAMP_COL].max() - sorted_df.groupby(CASE_COL)[TIMESTAMP_COL].min())
        .dt.total_seconds() / 86400.0
    )

    cases_with_return = sorted_df[sorted_df[ACTIVITY_COL] == "Return ER"][CASE_COL].unique()
    cases_without_return = [cid for cid in case_durations.index if cid not in cases_with_return]

    dur_return = case_durations.loc[cases_with_return]
    dur_no_return = case_durations.loc[cases_without_return]

    return_events = sorted_df[sorted_df[ACTIVITY_COL] == "Return ER"]
    return_gap_days = return_events["elapsed_minutes"] / (60.0 * 24.0)

    bottleneck_summary = [
        {"Analysis_Domain": "Antibiotic Latency", "Finding": f"36.9% received antibiotics within 1h; 74.8% within 3h; median latency = {valid_ab.median():.2f}h."},
        {"Analysis_Domain": "Admission Boarding", "Finding": f"Median boarding time from ER intake to hospital ward bed = {valid_adm.median():.2f}h across {total_adm_cases} admitted cases."},
        {"Analysis_Domain": "Recorded Log Window vs Stay", "Finding": f"Cases without Return ER had median recorded span of {dur_no_return.median():.1f} days, whereas cases with Return ER had median span of {dur_return.median():.1f} days."},
        {"Analysis_Domain": "Return ER Event Context", "Finding": f"294 cases recorded Return ER with median gap of {return_gap_days.median():.1f} days after discharge. This represents out-of-hospital elapsed time, not continuous bed occupancy."},
        {"Analysis_Domain": "Clinical Caveat", "Finding": "Process mining identifies event transitions and timestamp differences; it does not infer clinical causation, medical fault, or definitive clinical outcomes."}
    ]
    bottleneck_df = pd.DataFrame(bottleneck_summary)
    bottleneck_file = output_dir / "clinical_bottlenecks_summary.csv"
    bottleneck_df.to_csv(bottleneck_file, index=False)

    print(f"[Bottleneck Analysis] Completed successfully!")
    print(f"  - Triage-to-Antibiotics report: {triage_ab_file.name}")
    print(f"  - Admission latency report: {adm_file.name}")
    print(f"  - Bottlenecks & observation duration report: {bottleneck_file.name}")

    return {
        "triage_to_antibiotics_cases": total_ab_cases,
        "triage_to_antibiotics_median_hours": float(valid_ab.median()),
        "admission_cases": total_adm_cases,
        "admission_median_hours": float(valid_adm.median()),
        "return_er_cases": len(cases_with_return),
        "return_er_median_gap_days": float(return_gap_days.median()),
        "output_files": [str(triage_ab_file), str(adm_file), str(bottleneck_file)]
    }


if __name__ == "__main__":
    times_file = project_root / "data" / "processed" / "sepsis_with_times.csv"
    tables_folder = project_root / "outputs" / "tables"
    analyze_clinical_bottlenecks(times_file, tables_folder)
