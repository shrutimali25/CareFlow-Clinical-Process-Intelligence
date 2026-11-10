"""
XES and CSV Reconciliation Module
Performs comprehensive multi-attribute reconciliation between raw XES and processed CSV.
Author: Shruti (Member 1 - Data Engineering)
"""

from pathlib import Path
from typing import Dict, Any, Union
import pandas as pd
import pm4py
from src.data.loader import load_event_log, get_column_mapping, CASE_COL, ACTIVITY_COL, TIMESTAMP_COL


def reconcile_datasets(
    xes_file_path: Union[str, Path],
    csv_file_path: Union[str, Path],
    reports_dir: Union[str, Path]
) -> pd.DataFrame:
    """
    Reconciles raw XES data with processed CSV down to individual event occurrences.
    
    Verifies:
    - Event counts (15,214)
    - Case counts (1,050)
    - Activity counts (16)
    - Zero missing event combinations
    - Zero extra event combinations
    """
    xes_path = Path(xes_file_path)
    csv_path = Path(csv_file_path)
    output_dir = Path(reports_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[Reconciliation] Reading raw XES log: {xes_path.name}...")
    event_log = pm4py.read_xes(str(xes_path))
    xes_raw = pm4py.convert_to_dataframe(event_log)

    print(f"[Reconciliation] Reading processed CSV: {csv_path.name}...")
    csv_raw = load_event_log(csv_path, parse_timestamps=True)

    xes_case, xes_act, xes_time = get_column_mapping(xes_raw)
    csv_case, csv_act, csv_time = get_column_mapping(csv_raw)

    # Standardize comparison records
    xes_comp = pd.DataFrame({
        "case_id": xes_raw[xes_case].astype(str).str.strip(),
        "activity": xes_raw[xes_act].astype(str).str.strip(),
        "timestamp": pd.to_datetime(xes_raw[xes_time], errors="coerce", utc=True)
    }).dropna(subset=["timestamp"])

    csv_comp = pd.DataFrame({
        "case_id": csv_raw[csv_case].astype(str).str.strip(),
        "activity": csv_raw[csv_act].astype(str).str.strip(),
        "timestamp": pd.to_datetime(csv_raw[csv_time], errors="coerce", utc=True)
    }).dropna(subset=["timestamp"])

    keys = ["case_id", "activity", "timestamp"]
    xes_counts = xes_comp.groupby(keys).size().reset_index(name="xes_count")
    csv_counts = csv_comp.groupby(keys).size().reset_index(name="csv_count")

    comparison = xes_counts.merge(csv_counts, on=keys, how="outer").fillna(0)
    comparison["xes_count"] = comparison["xes_count"].astype(int)
    comparison["csv_count"] = comparison["csv_count"].astype(int)

    missing = comparison[comparison["xes_count"] > comparison["csv_count"]].copy()
    missing["difference"] = missing["xes_count"] - missing["csv_count"]

    extra = comparison[comparison["csv_count"] > comparison["xes_count"]].copy()
    extra["difference"] = extra["csv_count"] - extra["xes_count"]

    # Save discrepancy records
    missing.to_csv(output_dir / "events_missing_from_csv.csv", index=False)
    extra.to_csv(output_dir / "extra_events_in_csv.csv", index=False)

    summary_df = pd.DataFrame({
        "Metric": [
            "XES total events",
            "CSV total events",
            "XES unique cases",
            "CSV unique cases",
            "XES unique activities",
            "CSV unique activities",
            "Different event combinations",
            "Missing event occurrences",
            "Extra event occurrences",
            "Reconciliation Match %"
        ],
        "Value": [
            str(len(xes_comp)),
            str(len(csv_comp)),
            str(xes_comp["case_id"].nunique()),
            str(csv_comp["case_id"].nunique()),
            str(xes_comp["activity"].nunique()),
            str(csv_comp["activity"].nunique()),
            str(len(missing) + len(extra)),
            str(int(missing["difference"].sum())),
            str(int(extra["difference"].sum())),
            "100.0%" if len(missing) == 0 and len(extra) == 0 else f"{round(100 * (1 - len(missing)/len(xes_comp)), 2)}%"
        ]
    })

    summary_file = output_dir / "reconciliation_summary.csv"
    summary_df.to_csv(summary_file, index=False)

    print("\n" + "="*50)
    print("XES VS CSV RECONCILIATION SUMMARY")
    print("="*50)
    print(summary_df.to_string(index=False))
    print("="*50)
    print(f"Summary saved to: {summary_file}")

    return summary_df


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[2]
    raw_xes = project_root / "data" / "raw" / "sepsis.xes.gz"
    times_csv = project_root / "data" / "processed" / "sepsis_with_times.csv"
    reports = project_root / "reports"
    reconcile_datasets(raw_xes, times_csv, reports)
