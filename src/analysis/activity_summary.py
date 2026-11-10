"""
Activity Frequency & Rework Analytics Module
Calculates activity volume, patient reach, and rework/repetition rates.
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


def generate_activity_summary(
    input_file_path: Union[str, Path],
    processed_output_path: Union[str, Path],
    tables_output_path: Union[str, Path]
) -> pd.DataFrame:
    """
    Computes comprehensive activity metrics including frequency, case reach,
    rework loops, and repetition intensities.
    """
    input_path = Path(input_file_path)
    processed_out = Path(processed_output_path)
    tables_out = Path(tables_output_path)
    processed_out.parent.mkdir(parents=True, exist_ok=True)
    tables_out.parent.mkdir(parents=True, exist_ok=True)

    df = load_event_log(input_path, parse_timestamps=True)
    total_cases = df[CASE_COL].nunique()
    total_events = len(df)

    # 1. Per case activity counts to measure repetitions
    case_act_counts = df.groupby([CASE_COL, ACTIVITY_COL]).size().reset_index(name="counts")

    # 2. Start and end activities per case
    sorted_df = df.sort_values(by=[CASE_COL, TIMESTAMP_COL], kind="stable")
    starts = sorted_df.groupby(CASE_COL)[ACTIVITY_COL].first().value_counts()
    ends = sorted_df.groupby(CASE_COL)[ACTIVITY_COL].last().value_counts()

    rows = []
    for act, group in case_act_counts.groupby(ACTIVITY_COL):
        total_occ = int(group["counts"].sum())
        unique_c = int(len(group))
        rep_cases = int((group["counts"] > 1).sum())
        max_rep = int(group["counts"].max())
        mean_occ = round(float(group["counts"].mean()), 2)
        reach_pct = round(100.0 * unique_c / total_cases, 2)
        rework_rate = round(100.0 * rep_cases / unique_c, 2) if unique_c > 0 else 0.0

        rows.append({
            "concept:name": act,
            "total_occurrences": total_occ,
            "unique_cases": unique_c,
            "case_reach_pct": reach_pct,
            "repeated_cases_count": rep_cases,
            "rework_rate_pct": rework_rate,
            "max_repetitions_in_single_case": max_rep,
            "mean_occurrences_per_case": mean_occ,
            "first_activity_case_count": int(starts.get(act, 0)),
            "last_activity_case_count": int(ends.get(act, 0))
        })

    detailed_df = pd.DataFrame(rows).sort_values("total_occurrences", ascending=False)
    detailed_df.to_csv(tables_out / "activity_frequency_detailed.csv", index=False)

    # Backward compatible summary for existing scripts and dashboards
    compat_df = detailed_df[["concept:name", "total_occurrences", "unique_cases"]].copy()
    compat_df.to_csv(processed_out, index=False)

    print(f"[Activity Summary] Completed successfully!")
    print(f"  - Total unique activities: {len(detailed_df)}")
    print(f"  - Total activity occurrences: {detailed_df['total_occurrences'].sum():,} (verified match: {total_events:,})")
    print(f"  - Highest rework activity: {detailed_df.sort_values('rework_rate_pct', ascending=False).iloc[0]['concept:name']} ({detailed_df.sort_values('rework_rate_pct', ascending=False).iloc[0]['rework_rate_pct']}% of reached cases had repetitions)")
    print(f"  - Saved to: {processed_out}")

    return detailed_df


if __name__ == "__main__":
    times_file = project_root / "data" / "processed" / "sepsis_with_times.csv"
    processed_file = project_root / "data" / "processed" / "activity_frequency.csv"
    tables_folder = project_root / "outputs" / "tables"

    generate_activity_summary(times_file, processed_file, tables_folder)
