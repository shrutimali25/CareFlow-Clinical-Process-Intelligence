"""
Data Quality Validation Module
Performs comprehensive integrity, completeness, and chronological validation checks.
Author: Shruti (Member 1 - Data Engineering)
"""

from pathlib import Path
from typing import Dict, Any, List, Union
import pandas as pd
from src.data.loader import load_event_log, get_column_mapping, CASE_COL, ACTIVITY_COL, TIMESTAMP_COL


def validate_dataset(
    csv_file_path: Union[str, Path],
    reports_dir: Union[str, Path]
) -> pd.DataFrame:
    """
    Executes an extensive suite of data quality validation checks on the processed event log.
    
    Generates:
    - data_quality_report.csv
    - final_data_validation_report.csv
    """
    input_file = Path(csv_file_path)
    output_folder = Path(reports_dir)
    output_folder.mkdir(parents=True, exist_ok=True)

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found for validation: {input_file}")

    df = load_event_log(input_file, parse_timestamps=True)
    case_col, act_col, time_col = get_column_mapping(df)

    # 1. Monotonicity check
    monotonic_increasing = df.groupby(case_col)[time_col].apply(
        lambda s: s.is_monotonic_increasing
    )
    cases_in_order = int(monotonic_increasing.sum())
    cases_out_of_order = int((~monotonic_increasing).sum())

    # 2. Duplicate combinations
    dup_event_combos = int(
        df.duplicated(subset=[case_col, act_col, time_col], keep=False).sum()
    )
    exact_duplicate_rows = int(df.duplicated().sum())

    # 3. Missing values
    missing_cases = int(df[case_col].isna().sum())
    missing_activities = int(df[act_col].isna().sum())
    missing_timestamps = int(df[time_col].isna().sum())

    # 4. Elapsed time checks
    negative_elapsed = 0
    if "elapsed_minutes" in df.columns:
        negative_elapsed = int((df["elapsed_minutes"] < 0).sum())

    # 5. Build Data Quality Metrics
    quality_metrics = [
        ("Total rows", len(df)),
        ("Total columns", len(df.columns)),
        ("Unique patient cases", int(df[case_col].nunique())),
        ("Unique activities", int(df[act_col].nunique())),
        ("Missing case IDs", missing_cases),
        ("Missing activities", missing_activities),
        ("Missing timestamps", missing_timestamps),
        ("Exact duplicate rows", exact_duplicate_rows),
        ("Repeated events at same timestamp", dup_event_combos),
        ("Cases in chronological order", cases_in_order),
        ("Cases out of chronological order", cases_out_of_order),
        ("Negative elapsed times", negative_elapsed),
        ("Case 'NA' verified present", int("NA" in df[case_col].values)),
        ("Case 'NA' event count", int((df[case_col] == "NA").sum()))
    ]

    dq_df = pd.DataFrame(quality_metrics, columns=["Metric", "Value"])
    dq_file = output_folder / "data_quality_report.csv"
    dq_df.to_csv(dq_file, index=False)

    # 6. Build Final Data Validation PASS/FAIL Report
    validation_checks = [
        {
            "Validation_Check": "Total Events",
            "Result": str(len(df)),
            "Status": "PASS" if len(df) == 15214 else "CHECK"
        },
        {
            "Validation_Check": "Unique Cases",
            "Result": str(df[case_col].nunique()),
            "Status": "PASS" if df[case_col].nunique() == 1050 else "FAIL"
        },
        {
            "Validation_Check": "Unique Activities",
            "Result": str(df[act_col].nunique()),
            "Status": "PASS" if df[act_col].nunique() == 16 else "FAIL"
        },
        {
            "Validation_Check": f"Missing values in {case_col}",
            "Result": str(missing_cases),
            "Status": "PASS" if missing_cases == 0 else "FAIL"
        },
        {
            "Validation_Check": f"Missing values in {act_col}",
            "Result": str(missing_activities),
            "Status": "PASS" if missing_activities == 0 else "FAIL"
        },
        {
            "Validation_Check": f"Missing values in {time_col}",
            "Result": str(missing_timestamps),
            "Status": "PASS" if missing_timestamps == 0 else "FAIL"
        },
        {
            "Validation_Check": "Case 'NA' Preserved",
            "Result": f"Preserved (24 events)" if (df[case_col] == "NA").sum() == 24 else "FAIL",
            "Status": "PASS" if (df[case_col] == "NA").sum() == 24 else "FAIL"
        },
        {
            "Validation_Check": "Chronological Ordering",
            "Result": f"{cases_in_order} cases in order",
            "Status": "PASS" if cases_out_of_order == 0 else "FAIL"
        },
        {
            "Validation_Check": "Negative Elapsed Times",
            "Result": str(negative_elapsed),
            "Status": "PASS" if negative_elapsed == 0 else "FAIL"
        },
        {
            "Validation_Check": "Duplicate Event Combinations",
            "Result": f"{dup_event_combos} clinical re-assays",
            "Status": "INFO"
        }
    ]

    val_df = pd.DataFrame(validation_checks)
    val_file = output_folder / "final_data_validation_report.csv"
    val_df.to_csv(val_file, index=False)

    print(f"\n[Validation] Validation completed!")
    print(val_df.to_string(index=False))
    print(f"\nReports saved to:")
    print(f"  - {dq_file}")
    print(f"  - {val_file}")

    return val_df


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[2]
    times_file = project_root / "data" / "processed" / "sepsis_with_times.csv"
    reports_path = project_root / "reports"
    validate_dataset(times_file, reports_path)
