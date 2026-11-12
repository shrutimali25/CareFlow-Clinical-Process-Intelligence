
"""
Activity Transitions & Probability Matrix Analytics Module.

Calculates transition frequencies, conditional transition probabilities,
and inter-event waiting-time statistics.

Author: Shruti (Member 1 - Data Engineering & Clinical Analytics)
Co-Author: Madhura (Process Mining Integration)
"""

from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd

from src.data.loader import load_event_log, ACTIVITY_COL


def generate_transitions_analysis(
    input_file_path: Union[str, Path],
    processed_output_path: Union[str, Path],
    tables_output_path: Union[str, Path],
) -> pd.DataFrame:
    """
    Generate transition counts, waiting-time statistics,
    conditional probabilities, and a full activity transition matrix.
    """

    input_path = Path(input_file_path)
    processed_out = Path(processed_output_path)
    tables_out = Path(tables_output_path)

    processed_out.parent.mkdir(parents=True, exist_ok=True)
    tables_out.mkdir(parents=True, exist_ok=True)

    # Load the prepared event log.
    df = load_event_log(input_path, parse_timestamps=True)

    required_columns = [
        ACTIVITY_COL,
        "previous_activity",
        "elapsed_minutes",
    ]

    missing_columns = [
        col for col in required_columns if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Keep all valid consecutive activity transitions,
    # including transitions whose elapsed time is missing.
    transitions_df = df.dropna(
        subset=["previous_activity", ACTIVITY_COL]
    ).copy()

    total_transitions = len(transitions_df)

    grouped = transitions_df.groupby(
        ["previous_activity", ACTIVITY_COL],
        sort=True,
    )

    # Count transitions independently of elapsed-time availability.
    counts = (
        grouped.size()
        .rename("total_transitions")
        .reset_index()
    )

    # Calculate waiting-time statistics separately.
    waiting_stats = (
        grouped["elapsed_minutes"]
        .agg(
            average_minutes="mean",
            median_minutes="median",
            std_minutes="std",
            min_minutes="min",
            max_minutes="max",
            q25_minutes=lambda x: x.quantile(0.25),
            q75_minutes=lambda x: x.quantile(0.75),
        )
        .reset_index()
    )

    # Merge counts and waiting statistics.
    stats = counts.merge(
        waiting_stats,
        on=["previous_activity", ACTIVITY_COL],
        how="left",
        validate="one_to_one",
    )

    # Calculate additional time metrics.
    stats["iqr_minutes"] = (
        stats["q75_minutes"] - stats["q25_minutes"]
    )

    stats["average_hours"] = stats["average_minutes"] / 60.0
    stats["median_hours"] = stats["median_minutes"] / 60.0

    # Calculate conditional transition probabilities.
    source_totals = stats.groupby(
        "previous_activity"
    )["total_transitions"].transform("sum")

    stats["transition_probability"] = (
        stats["total_transitions"] / source_totals
    )

    stats["transition_percentage"] = (
        stats["transition_probability"] * 100.0
    ).round(2)

    # Round time statistics for readable output.
    time_columns = [
        "average_minutes",
        "median_minutes",
        "std_minutes",
        "min_minutes",
        "max_minutes",
        "q25_minutes",
        "q75_minutes",
        "iqr_minutes",
        "average_hours",
        "median_hours",
    ]

    stats[time_columns] = stats[time_columns].round(4)

    stats = stats.sort_values(
        "total_transitions",
        ascending=False,
    ).reset_index(drop=True)

    # Build the full activity transition probability matrix.
    all_activities = sorted(
        df[ACTIVITY_COL].dropna().unique()
    )

    if len(all_activities) != 16:
        raise ValueError(
            f"Expected 16 activities, found {len(all_activities)}"
        )

    matrix_df = pd.DataFrame(
        0.0,
        index=all_activities,
        columns=all_activities,
    )

    for _, row in stats.iterrows():
        source = row["previous_activity"]
        target = row[ACTIVITY_COL]

        matrix_df.loc[source, target] = (
            row["transition_probability"]
        )

    if matrix_df.shape != (16, 16):
        raise ValueError(
            f"Expected a 16x16 matrix, got {matrix_df.shape}"
        )

    # Validate all non-empty probability rows.
    for source in all_activities:
        outgoing_total = stats.loc[
            stats["previous_activity"] == source,
            "total_transitions",
        ].sum()

        if outgoing_total > 0:
            actual_sum = matrix_df.loc[source].sum()

            if not np.isclose(
                actual_sum,
                1.0,
                rtol=1e-9,
                atol=1e-12,
            ):
                raise ValueError(
                    f"Probability row for {source!r} sums to "
                    f"{actual_sum}, expected 1.0"
                )

    # Save the probability matrix.
    matrix_file = (
        tables_out / "activity_transition_matrix.csv"
    )

    matrix_df.to_csv(
        matrix_file,
        float_format="%.15g",
    )

    # Save detailed transition statistics.
    detailed_file = (
        tables_out / "activity_transitions_detailed.csv"
    )

    stats.to_csv(
        detailed_file,
        index=False,
        float_format="%.15g",
    )

    # Preserve the original backward-compatible five-column output.
    compat_df = stats[
        [
            "previous_activity",
            ACTIVITY_COL,
            "total_transitions",
            "average_minutes",
            "median_minutes",
        ]
    ].copy()

    compat_df.to_csv(
        processed_out,
        index=False,
    )

    print("[Transitions Analysis] Completed successfully!")
    print(f"Total transitions: {total_transitions:,}")
    print(f"Unique transition pairs: {len(stats):,}")
    print(f"Activities: {len(all_activities)}")
    print(f"Matrix saved: {matrix_file}")
    print(f"Detailed output saved: {detailed_file}")
    print(f"Compatibility output saved: {processed_out}")

    return stats


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[2]

    times_file = (
        project_root
        / "data"
        / "processed"
        / "sepsis_with_times.csv"
    )

    processed_file = (
        project_root
        / "data"
        / "processed"
        / "activity_time_differences.csv"
    )

    tables_folder = project_root / "outputs" / "tables"

    generate_transitions_analysis(
        times_file,
        processed_file,
        tables_folder,
    )
