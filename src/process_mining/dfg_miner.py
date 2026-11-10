"""
Directly-Follows Graph (DFG) Mining Module
Extracts frequency and performance (duration/bottleneck) transitions between clinical activities.
Author: Madhura (Member 2 - Process Mining)
"""

from pathlib import Path
from typing import Dict, Any, Tuple, Union
import pandas as pd
import numpy as np
import pm4py


def run_dfg_discovery(
    event_log_df: pd.DataFrame,
    tables_output_dir: Union[str, Path]
) -> Dict[str, Any]:
    """
    Extracts frequency-based and duration-based Directly-Follows Graphs.
    
    Generates:
    - outputs/tables/dfg_frequency_table.csv
    - outputs/tables/dfg_performance_table.csv
    
    Returns:
        Dict of DFG graph structure metrics.
    """
    output_dir = Path(tables_output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Frequency DFG
    print("[DFG Discovery] Mining Directly-Follows Graph (Frequency)...")
    dfg, start_activities, end_activities = pm4py.discover_dfg(event_log_df)
    total_transitions = sum(dfg.values())

    freq_rows = []
    for (src, tgt), count in sorted(dfg.items(), key=lambda x: x[1], reverse=True):
        freq_rows.append({
            "source_activity": src,
            "target_activity": tgt,
            "transition_count": count,
            "percentage_of_all_transitions": round(100.0 * count / total_transitions, 2)
        })

    freq_df = pd.DataFrame(freq_rows)
    freq_file = output_dir / "dfg_frequency_table.csv"
    freq_df.to_csv(freq_file, index=False)

    # 2. Performance DFG (Time / Latency)
    print("[DFG Discovery] Mining Performance DFG (Durations & Latencies)...")
    perf_dfg, _, _ = pm4py.discover_performance_dfg(event_log_df)

    perf_rows = []
    for (src, tgt), stats in perf_dfg.items():
        # PM4Py performance DFG stores duration in seconds
        mean_sec = float(stats.get("mean", 0.0))
        median_sec = float(stats.get("median", 0.0))
        max_sec = float(stats.get("max", 0.0))
        min_sec = float(stats.get("min", 0.0))

        count = dfg.get((src, tgt), 0)

        perf_rows.append({
            "source_activity": src,
            "target_activity": tgt,
            "transition_count": count,
            "mean_duration_hours": round(mean_sec / 3600.0, 2),
            "median_duration_hours": round(median_sec / 3600.0, 2),
            "max_duration_hours": round(max_sec / 3600.0, 2),
            "min_duration_hours": round(min_sec / 3600.0, 2),
            "mean_duration_minutes": round(mean_sec / 60.0, 2),
            "median_duration_minutes": round(median_sec / 60.0, 2)
        })

    perf_df = pd.DataFrame(perf_rows).sort_values("mean_duration_hours", ascending=False)
    perf_file = output_dir / "dfg_performance_table.csv"
    perf_df.to_csv(perf_file, index=False)

    metrics = {
        "unique_edges": len(dfg),
        "total_transitions": total_transitions,
        "unique_start_activities": len(start_activities),
        "unique_end_activities": len(end_activities),
        "primary_start_activity": max(start_activities.items(), key=lambda x: x[1])[0],
        "primary_end_activity": max(end_activities.items(), key=lambda x: x[1])[0],
        "top_transition": f"{freq_rows[0]['source_activity']} -> {freq_rows[0]['target_activity']} ({freq_rows[0]['transition_count']})",
        "slowest_transition_mean": f"{perf_df.iloc[0]['source_activity']} -> {perf_df.iloc[0]['target_activity']} ({perf_df.iloc[0]['mean_duration_hours']} hrs)",
        "frequency_table_file": str(freq_file),
        "performance_table_file": str(perf_file)
    }

    print(f"[DFG Discovery] Discovery completed successfully!")
    print(f"  - Total transitions: {metrics['total_transitions']:,} across {metrics['unique_edges']} unique edges")
    print(f"  - Top transition: {metrics['top_transition']}")
    print(f"  - Highest latency transition (mean): {metrics['slowest_transition_mean']}")
    print(f"  - Saved tables to: {output_dir}")

    return metrics


if __name__ == "__main__":
    from src.process_mining.log_manager import create_pm4py_event_log

    project_root = Path(__file__).resolve().parents[2]
    cleaned_csv = project_root / "data" / "processed" / "sepsis_cleaned.csv"
    tables_dir = project_root / "outputs" / "tables"

    log_df, _ = create_pm4py_event_log(cleaned_csv)
    run_dfg_discovery(log_df, tables_dir)
