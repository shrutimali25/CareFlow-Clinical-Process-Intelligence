"""
Patient Case Profiling and Duration Analytics Module
Computes case-level metrics, recorded observation durations, and clinical attribute distributions.
Author: Shruti (Member 1 - Data Engineering)
"""

from pathlib import Path
from typing import Dict, Any, Union
import sys
import pandas as pd

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.data.loader import load_event_log, CASE_COL, ACTIVITY_COL, TIMESTAMP_COL


def generate_case_profiles(
    input_file_path: Union[str, Path],
    processed_output_path: Union[str, Path],
    tables_output_path: Union[str, Path]
) -> pd.DataFrame:
    """
    Builds comprehensive patient case profiles across all 1,050 cases.
    
    Distinguishes the recorded EHR event-log observation window from true inpatient stay,
    and captures clinical attributes recorded in the Sepsis dataset.
    """
    input_path = Path(input_file_path)
    processed_out = Path(processed_output_path)
    tables_out = Path(tables_output_path)
    processed_out.parent.mkdir(parents=True, exist_ok=True)
    tables_out.parent.mkdir(parents=True, exist_ok=True)

    df = load_event_log(input_path, parse_timestamps=True)
    sorted_df = df.sort_values(by=[CASE_COL, TIMESTAMP_COL], kind="stable")

    # Group by case
    case_groups = sorted_df.groupby(CASE_COL)

    # 1. Base timestamps and events count
    base_summary = case_groups.agg(
        total_events=(ACTIVITY_COL, "count"),
        first_event_time=(TIMESTAMP_COL, "min"),
        last_event_time=(TIMESTAMP_COL, "max"),
        entry_activity=(ACTIVITY_COL, "first"),
        exit_activity=(ACTIVITY_COL, "last"),
        Age=("Age", "first"),
        Diagnose=("Diagnose", "first"),
        SIRSCriteria2OrMore=("SIRSCriteria2OrMore", "first"),
        InfectionSuspected=("InfectionSuspected", "first")
    ).reset_index()

    # 2. Duration calculations
    base_summary["treatment_duration_hours"] = (
        (base_summary["last_event_time"] - base_summary["first_event_time"]).dt.total_seconds() / 3600.0
    ).round(2)
    base_summary["treatment_duration_days"] = (
        base_summary["treatment_duration_hours"] / 24.0
    ).round(2)

    # 3. Clinical flags derived strictly from recorded activities
    acts_per_case = case_groups[ACTIVITY_COL].apply(set)
    base_summary["admitted_normal_care"] = base_summary[CASE_COL].map(lambda cid: "Admission NC" in acts_per_case.get(cid, set()))
    base_summary["admitted_intensive_care"] = base_summary[CASE_COL].map(lambda cid: "Admission IC" in acts_per_case.get(cid, set()))
    base_summary["received_antibiotics"] = base_summary[CASE_COL].map(lambda cid: "IV Antibiotics" in acts_per_case.get(cid, set()))
    base_summary["received_iv_liquid"] = base_summary[CASE_COL].map(lambda cid: "IV Liquid" in acts_per_case.get(cid, set()))
    base_summary["had_return_er"] = base_summary[CASE_COL].map(lambda cid: "Return ER" in acts_per_case.get(cid, set()))

    # Clean Diagnose display
    base_summary["Diagnose"] = base_summary["Diagnose"].fillna("Unrecorded")

    # Export rich profile table
    base_summary.to_csv(tables_out / "patient_case_profiles.csv", index=False)

    # Export backward-compatible CSV expected by original scripts
    compat_cols = [
        CASE_COL,
        "total_events",
        "first_event_time",
        "last_event_time",
        "treatment_duration_hours"
    ]
    compat_df = base_summary[compat_cols].copy()
    compat_df.to_csv(processed_out, index=False)

    durations = base_summary["treatment_duration_hours"]
    print(f"[Case Profiling] Completed successfully!")
    print(f"  - Total patient cases profiled: {len(base_summary):,}")
    print(f"  - Case 'NA' preserved: {'NA' in base_summary[CASE_COL].values}")
    print(f"  - Average events per case: {round(base_summary['total_events'].mean(), 2)} (median: {int(base_summary['total_events'].median())})")
    print(f"  - Recorded log duration (hours): mean = {round(durations.mean(), 2)}, median = {round(durations.median(), 2)}")
    print(f"  - Cases with ICU stay (Admission IC): {base_summary['admitted_intensive_care'].sum()}")
    print(f"  - Cases with Return ER recorded: {base_summary['had_return_er'].sum()}")
    print(f"  - Saved to: {processed_out}")

    return base_summary


if __name__ == "__main__":
    times_file = project_root / "data" / "processed" / "sepsis_with_times.csv"
    processed_file = project_root / "data" / "processed" / "patient_case_summary.csv"
    tables_folder = project_root / "outputs" / "tables"

    generate_case_profiles(times_file, processed_file, tables_folder)
