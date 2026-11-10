"""
Heuristics Miner Module
Discovers robust, noise-tolerant process models using Heuristics Miner.
Author: Madhura (Member 2 - Process Mining)
"""

from pathlib import Path
from typing import Dict, Any, Union
import pandas as pd
import numpy as np
import pm4py
from src.data.loader import ACTIVITY_COL, CASE_COL


def run_heuristics_miner(
    event_log_df: pd.DataFrame,
    models_output_dir: Union[str, Path],
    tables_output_dir: Union[str, Path],
    dependency_threshold: float = 0.5
) -> Dict[str, Any]:
    """
    Executes PM4Py's Heuristics Miner to extract the primary flow structure and dependency relations.
    
    Generates:
    - Heuristics Petri Net (outputs/models/heuristics_petri_net.pnml)
    - Heuristics Dependency Matrix (outputs/tables/heuristics_dependency_matrix.csv)
    
    Returns:
        Dict of model architecture metrics.
    """
    models_dir = Path(models_output_dir)
    tables_dir = Path(tables_output_dir)
    models_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    print("[Heuristics Miner] Discovering Heuristics Petri Net...")
    heu_net, heu_im, heu_fm = pm4py.discover_petri_net_heuristics(
        event_log_df,
        dependency_threshold=dependency_threshold
    )

    # 1. Export Petri Net
    pnml_path = models_dir / "heuristics_petri_net.pnml"
    pm4py.write_pnml(heu_net, heu_im, heu_fm, str(pnml_path))

    # 2. Compute Activity Dependency Matrix
    print("[Heuristics Miner] Computing Activity Dependency Matrix...")
    dfg, sa, ea = pm4py.discover_dfg(event_log_df)
    activities = sorted(event_log_df[ACTIVITY_COL].unique())
    n = len(activities)
    act_to_idx = {act: i for i, act in enumerate(activities)}

    # Direct follower counts matrix
    df_matrix = np.zeros((n, n), dtype=int)
    for (src, tgt), count in dfg.items():
        if src in act_to_idx and tgt in act_to_idx:
            df_matrix[act_to_idx[src], act_to_idx[tgt]] = count

    # Heuristic dependency measure: (a=>b - b=>a) / (a=>b + b=>a + 1)
    dep_matrix = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(n):
            a_to_b = df_matrix[i, j]
            b_to_a = df_matrix[j, i]
            if i == j:
                # Self-loop heuristic: a=>a / (a=>a + 1)
                dep_matrix[i, j] = a_to_b / (a_to_b + 1)
            else:
                dep_matrix[i, j] = (a_to_b - b_to_a) / (a_to_b + b_to_a + 1)

    dep_df = pd.DataFrame(
        np.round(dep_matrix, 4),
        index=activities,
        columns=activities
    )
    dep_file = tables_dir / "heuristics_dependency_matrix.csv"
    dep_df.to_csv(dep_file)

    visible_transitions = [t for t in heu_net.transitions if t.label is not None]
    silent_transitions = [t for t in heu_net.transitions if t.label is None]

    metrics = {
        "algorithm": "Heuristics Miner",
        "dependency_threshold": dependency_threshold,
        "petri_net_places": len(heu_net.places),
        "petri_net_transitions": len(heu_net.transitions),
        "petri_net_arcs": len(heu_net.arcs),
        "visible_transitions": len(visible_transitions),
        "silent_transitions": len(silent_transitions),
        "dependency_matrix_activities": n,
        "pnml_file": str(pnml_path),
        "dependency_matrix_file": str(dep_file)
    }

    print(f"[Heuristics Miner] Discovery completed successfully!")
    print(f"  - Petri Net: {metrics['petri_net_places']} places, {metrics['petri_net_transitions']} transitions ({metrics['visible_transitions']} labeled, {metrics['silent_transitions']} tau)")
    print(f"  - Exported PNML: {pnml_path.name} ({pnml_path.stat().st_size:,} bytes)")
    print(f"  - Exported Dependency Matrix: {dep_file.name}")

    return metrics


if __name__ == "__main__":
    from src.process_mining.log_manager import create_pm4py_event_log

    project_root = Path(__file__).resolve().parents[2]
    cleaned_csv = project_root / "data" / "processed" / "sepsis_cleaned.csv"
    models_dir = project_root / "outputs" / "models"
    tables_dir = project_root / "outputs" / "tables"

    log_df, _ = create_pm4py_event_log(cleaned_csv)
    run_heuristics_miner(log_df, models_dir, tables_dir)
