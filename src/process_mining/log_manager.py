"""
PM4Py Event Log Manager
Handles PM4Py DataFrame formatting and event log object generation with verified classifiers.
Author: Madhura (Member 2 - Process Mining)
"""

from pathlib import Path
from typing import Dict, Any, Tuple, Union
import pandas as pd
import pm4py
from src.data.loader import load_event_log, CASE_COL, ACTIVITY_COL, TIMESTAMP_COL


def create_pm4py_event_log(
    csv_file_path: Union[str, Path]
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Ingests the verified event log CSV and structures it for PM4Py algorithms.
    
    Returns:
        Tuple of (formatted_dataframe, summary_statistics)
    """
    input_file = Path(csv_file_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Input event log not found: {input_file}")

    # Load preserving Case 'NA'
    df = load_event_log(input_file, parse_timestamps=True)

    # Format DataFrame with PM4Py standard column classifiers
    df_formatted = pm4py.format_dataframe(
        df,
        case_id=CASE_COL,
        activity_key=ACTIVITY_COL,
        timestamp_key=TIMESTAMP_COL
    )

    start_activities = pm4py.get_start_activities(df_formatted)
    end_activities = pm4py.get_end_activities(df_formatted)

    stats = {
        "total_events": len(df_formatted),
        "unique_cases": int(df_formatted[CASE_COL].nunique()),
        "unique_activities": int(df_formatted[ACTIVITY_COL].nunique()),
        "start_activities_count": len(start_activities),
        "end_activities_count": len(end_activities),
        "primary_start_activity": max(start_activities.items(), key=lambda x: x[1])[0],
        "primary_end_activity": max(end_activities.items(), key=lambda x: x[1])[0],
        "has_case_NA": bool("NA" in df_formatted[CASE_COL].values),
        "case_NA_events": int((df_formatted[CASE_COL] == "NA").sum())
    }

    print(f"[PM4Py Log Manager] Successfully prepared event log:")
    print(f"  - Total events: {stats['total_events']:,}")
    print(f"  - Unique cases: {stats['unique_cases']:,}")
    print(f"  - Unique activities: {stats['unique_activities']}")
    print(f"  - Primary entry: {stats['primary_start_activity']} ({start_activities[stats['primary_start_activity']]} cases)")
    print(f"  - Primary exit: {stats['primary_end_activity']} ({end_activities[stats['primary_end_activity']]} cases)")
    print(f"  - Case 'NA' verified: {stats['has_case_NA']} ({stats['case_NA_events']} events)")

    return df_formatted, stats


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[2]
    cleaned_path = project_root / "data" / "processed" / "sepsis_cleaned.csv"
    create_pm4py_event_log(cleaned_path)
