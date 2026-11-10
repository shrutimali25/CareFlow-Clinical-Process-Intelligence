"""
Master Process Mining Execution Pipeline
Orchestrates PM4Py event log creation, Inductive & Heuristics mining, DFG, variants, and visual maps.
Author: Madhura (Member 2 - Process Mining)
"""

from pathlib import Path
import sys

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.process_mining.log_manager import create_pm4py_event_log
from src.process_mining.inductive_miner import run_inductive_miner
from src.process_mining.heuristics_miner import run_heuristics_miner
from src.process_mining.dfg_miner import run_dfg_discovery
from src.process_mining.variants_miner import run_variants_mining
from src.visualization.process_map import (
    plot_frequency_dfg,
    plot_performance_dfg,
    plot_variants_distribution
)
from src.visualization.interactive_map import generate_interactive_html_map
import pandas as pd


def main():
    print("=" * 65)
    print("CAREFLOW: PROCESS MINING & DISCOVERY PIPELINE (PM4PY)")
    print("Author: Madhura (Member 2 - Process Mining Specialist)")
    print("=" * 65)

    input_file = project_root / "data" / "processed" / "sepsis_cleaned.csv"
    models_dir = project_root / "outputs" / "models"
    tables_dir = project_root / "outputs" / "tables"
    figures_dir = project_root / "outputs" / "figures"

    # Step 1: Prepare Event Log
    print("\n--- STEP 1: EVENT LOG PREPARATION ---")
    log_df, log_stats = create_pm4py_event_log(input_file)

    # Step 2: Inductive Miner (Petri Net & BPMN)
    print("\n--- STEP 2: INDUCTIVE MINER DISCOVERY ---")
    ind_metrics = run_inductive_miner(log_df, models_dir)

    # Step 3: Heuristics Miner (Petri Net & Dependency Matrix)
    print("\n--- STEP 3: HEURISTICS MINER DISCOVERY ---")
    heu_metrics = run_heuristics_miner(log_df, models_dir, tables_dir)

    # Step 4: Directly-Follows Graphs (Frequency & Performance)
    print("\n--- STEP 4: DIRECTLY-FOLLOWS GRAPH (DFG) DISCOVERY ---")
    dfg_metrics = run_dfg_discovery(log_df, tables_dir)

    # Step 5: Process Variants Analytics
    print("\n--- STEP 5: PROCESS VARIANTS MINING ---")
    var_metrics = run_variants_mining(log_df, tables_dir)

    # Step 6: Professional Process Visualizations
    print("\n--- STEP 6: PROCESS VISUALIZATIONS GENERATION ---")
    freq_df = pd.read_csv(tables_dir / "dfg_frequency_table.csv")
    perf_df = pd.read_csv(tables_dir / "dfg_performance_table.csv")
    var_df = pd.read_csv(tables_dir / "process_variants_summary.csv")

    f1 = plot_frequency_dfg(freq_df, figures_dir / "dfg_frequency_process_map.png")
    f2 = plot_performance_dfg(perf_df, figures_dir / "dfg_performance_bottleneck_map.png")
    f3 = plot_variants_distribution(var_df, figures_dir / "top_variants_distribution.png")
    f4 = generate_interactive_html_map(freq_df, perf_df, figures_dir / "careflow_interactive_process_map.html")

    print("\n" + "=" * 65)
    print("PROCESS MINING DISCOVERY SUMMARY RESULTS")
    print("=" * 65)
    print(f"Dataset Analyzed: Sepsis Event Log ({log_stats['total_events']:,} events, {log_stats['unique_cases']:,} cases)")
    print(f"Inductive Petri Net: {ind_metrics['petri_net_places']} places, {ind_metrics['petri_net_transitions']} transitions")
    print(f"Inductive BPMN: {ind_metrics['bpmn_nodes']} nodes, {ind_metrics['bpmn_flows']} flows")
    print(f"Heuristics Petri Net: {heu_metrics['petri_net_places']} places, {heu_metrics['petri_net_transitions']} transitions")
    print(f"Directly-Follows Graph: {dfg_metrics['unique_edges']} transitions ({dfg_metrics['total_transitions']:,} occurrences)")
    print(f"Process Variants Discovered: {var_metrics['unique_variants']:,} unique pathways")
    print(f"Top Variant Share: {var_metrics['most_frequent_coverage_pct']}% | Top 10 Variants Share: {var_metrics['top_10_variants_coverage_pct']}%")
    print(f"Visual Maps Produced: {f1.name}, {f2.name}, {f3.name}, {f4.name}")
    print("=" * 65)


if __name__ == "__main__":
    main()
