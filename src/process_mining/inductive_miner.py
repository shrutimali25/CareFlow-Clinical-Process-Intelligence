"""
Inductive Miner Module
Discovers block-structured Process Trees, Petri Nets, and BPMN models using PM4Py's Inductive Miner.
Author: Madhura (Member 2 - Process Mining)
"""

from pathlib import Path
from typing import Dict, Any, Tuple, Union
import pandas as pd
import pm4py
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.bpmn.obj import BPMN


def run_inductive_miner(
    event_log_df: pd.DataFrame,
    models_output_dir: Union[str, Path]
) -> Dict[str, Any]:
    """
    Executes PM4Py's Inductive Miner algorithm on the prepared event log.
    
    Generates:
    - Inductive Petri Net (outputs/models/inductive_petri_net.pnml)
    - BPMN Model (outputs/models/inductive_bpmn.bpmn)
    
    Returns:
        Dict of model architecture metrics.
    """
    output_dir = Path(models_output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("[Inductive Miner] Discovering Process Tree and Petri Net...")
    net, im, fm = pm4py.discover_petri_net_inductive(event_log_df)

    # 1. Export Petri Net (PNML)
    pnml_path = output_dir / "inductive_petri_net.pnml"
    pm4py.write_pnml(net, im, fm, str(pnml_path))

    # 2. Discover & Export BPMN (disable auto_layout to run without Graphviz dot.exe)
    print("[Inductive Miner] Discovering BPMN model...")
    bpmn_model = pm4py.discover_bpmn_inductive(event_log_df)
    bpmn_path = output_dir / "inductive_bpmn.bpmn"
    pm4py.write_bpmn(bpmn_model, str(bpmn_path), auto_layout=False)

    # 3. Model Architecture Metrics
    visible_transitions = [t for t in net.transitions if t.label is not None]
    silent_transitions = [t for t in net.transitions if t.label is None]

    metrics = {
        "algorithm": "Inductive Miner",
        "petri_net_places": len(net.places),
        "petri_net_transitions": len(net.transitions),
        "petri_net_arcs": len(net.arcs),
        "visible_transitions": len(visible_transitions),
        "silent_transitions": len(silent_transitions),
        "bpmn_nodes": len(bpmn_model.get_nodes()),
        "bpmn_flows": len(bpmn_model.get_flows()),
        "pnml_file": str(pnml_path),
        "bpmn_file": str(bpmn_path)
    }

    print(f"[Inductive Miner] Discovery completed successfully!")
    print(f"  - Petri Net: {metrics['petri_net_places']} places, {metrics['petri_net_transitions']} transitions ({metrics['visible_transitions']} labeled, {metrics['silent_transitions']} tau)")
    print(f"  - BPMN: {metrics['bpmn_nodes']} nodes, {metrics['bpmn_flows']} sequence flows")
    print(f"  - Exported PNML: {pnml_path.name} ({pnml_path.stat().st_size:,} bytes)")
    print(f"  - Exported BPMN: {bpmn_path.name} ({bpmn_path.stat().st_size:,} bytes)")

    return metrics


if __name__ == "__main__":
    from src.process_mining.log_manager import create_pm4py_event_log

    project_root = Path(__file__).resolve().parents[2]
    cleaned_csv = project_root / "data" / "processed" / "sepsis_cleaned.csv"
    models_dir = project_root / "outputs" / "models"

    log_df, _ = create_pm4py_event_log(cleaned_csv)
    run_inductive_miner(log_df, models_dir)
