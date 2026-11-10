"""
Activity Transitions & Probability Matrix Analytics Module
Calculates transition frequencies, conditional transition probabilities P(B|A),
and waiting-time distributions from chronological event data.
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


def generate_transitions_analysis(
    input_file_path: Union[str, Path],
    processed_output_path: Union[str, Path],
    tables_output_path: Union[str, Path]
) -> pd.DataFrame:
    """
    Computes activity transition counts, probabilities, and elapsed time statistics.
    """
    input_path = Path(input_file_path)
    processed_out = Path(processed_output_path)
    tables_out = Path(tables_output_path)
    processed_out.parent.mkdir(parents=True, exist_ok=True)
    tables_out.parent.mkdir(parents=True, exist_ok=True)

    df = load_event_log(input_path, parse_timestamps=True)

    # Filter to consecutive transitions within cases
    transitions_df = df.dropna(subset=["previous_activity"]).copy()
    total_transitions = len(transitions_df)

    # 1. Group by source and target
    grouped = transitions_df.groupby(["previous_activity", ACTIVITY_COL])

    stats = grouped["elapsed_minutes"].agg(
        total_transitions="count",
        average_minutes="mean",
        median_minutes="median",
        std_minutes="std",
        min_minutes="min",
        max_minutes="max",
        q25_minutes=lambda x: x.quantile(0.25),
        q75_minutes=lambda x: x.quantile(0.75)
    ).reset_index()

    stats["std_minutes"] = stats["std_minutes"].fillna(0.0)
    stats["iqr_minutes"] = (stats["q75_minutes"] - stats["q25_minutes"]).round(4)
    stats["average_hours"] = (stats["average_minutes"] / 60.0).round(2)
    stats["median_hours"] = (stats["median_minutes"] / 60.0).round(2)
    stats["average_minutes"] = stats["average_minutes"].round(2)
    stats["median_minutes"] = stats["median_minutes"].round(2)

    # 2. Compute Conditional Transition Probability P(B | A)
    source_totals = stats.groupby("previous_activity")["total_transitions"].transform("sum")
    stats["transition_probability"] = (stats["total_transitions"] / source_totals).round(4)
    stats["transition_percentage"] = (stats["transition_probability"] * 100.0).round(2)

    # Sort by descending volume
    stats = stats.sort_values("total_transitions", ascending=False).reset_index(drop=True)

    # 3. Build Full 16x16 Transition Probability Matrix
    all_activities = sorted(df[ACTIVITY_COL].unique())
    matrix_df = pd.DataFrame(0.0, index=all_activities, columns=all_activities)

    for _, row in stats.iterrows():
        src = row["previous_activity"]
        tgt = row[ACTIVITY_COL]
        prob = row["transition_probability"]
        if src in matrix_df.index and tgt in matrix_df.columns:
            matrix_df.loc[src, tgt] = prob

    matrix_file = tables_out / "activity_transition_matrix.csv"
    matrix_df.to_csv(matrix_file)

    # 4. Save Detailed Transitions Table
    detailed_file = tables_out / "activity_transitions_detailed.csv"
    stats.to_csv(detailed_file, index=False)

    # 5. Save Backward-Compatible CSV for existing scripts
    compat_df = stats[
        ["previous_activity", ACTIVITY_COL, "total_transitions", "average_minutes", "median_minutes"]
    ].copy()
    compat_df.to_csv(processed_out, index=False)

    print(f"[Transitions Analysis] Completed successfully!")
    print(f"  - Total transitions analyzed: {total_transitions:,} across {len(stats)} unique pairs")
    print(f"  - Verified 16x16 transition matrix saved to: {matrix_file}")
    print(f"  - Detailed transition metrics saved to: {detailed_file}")
    print(f"  - Backward-compatible summary saved to: {processed_out}")

    return stats


if __name__ == "__main__":
    times_file = project_root / "data" / "processed" / "sepsis_with_times.csv"
    processed_file = project_root / "data" / "processed" / "activity_time_differences.csv"
    tables_folder = project_root / "outputs" / "tables"

    generate_transitions_analysis(times_file, processed_file, tables_folder)
