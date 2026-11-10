"""
XES to CSV Conversion Module
Converts compressed healthcare event log (.xes.gz) to CSV format.
Author: Shruti (Member 1 - Data Engineering)
"""

from pathlib import Path
from typing import Dict, Any, Union
import pm4py
from src.data.loader import save_event_log, CASE_COL, ACTIVITY_COL, TIMESTAMP_COL


def convert_xes_to_csv(
    xes_path: Union[str, Path],
    csv_output_path: Union[str, Path]
) -> Dict[str, Any]:
    """
    Parses a compressed XES log and exports it as a standardized CSV.
    
    Returns:
        Dict containing event, case, and activity counts.
    """
    input_file = Path(xes_path)
    output_file = Path(csv_output_path)

    if not input_file.exists():
        raise FileNotFoundError(f"Input XES file not found: {input_file}")

    print(f"[XES Conversion] Reading raw log from {input_file.name}...")
    log = pm4py.read_xes(str(input_file))
    df = pm4py.convert_to_dataframe(log)

    save_event_log(df, output_file)

    stats = {
        "total_events": len(df),
        "unique_cases": int(df[CASE_COL].nunique()),
        "unique_activities": int(df[ACTIVITY_COL].nunique()),
        "total_columns": len(df.columns),
        "output_file": str(output_file)
    }

    print(f"[XES Conversion] Completed successfully!")
    print(f"  - Total events: {stats['total_events']:,}")
    print(f"  - Unique cases: {stats['unique_cases']:,}")
    print(f"  - Unique activities: {stats['unique_activities']}")
    print(f"  - Saved to: {output_file}")

    return stats


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[2]
    raw_xes = project_root / "data" / "raw" / "sepsis.xes.gz"
    processed_csv = project_root / "data" / "processed" / "sepsis_event_log.csv"
    convert_xes_to_csv(raw_xes, processed_csv)
