"""
Process Variants and Pathway Miner Module
Extracts unique patient journey traces, variant distributions, and cumulative Pareto coverage.
Author: Madhura (Member 2 - Process Mining)
"""

from pathlib import Path
from typing import Dict, Any, Union
import pandas as pd
import pm4py
from src.data.loader import CASE_COL, ACTIVITY_COL, TIMESTAMP_COL


def run_variants_mining(
    event_log_df: pd.DataFrame,
    tables_output_dir: Union[str, Path]
) -> Dict[str, Any]:
    """
    Identifies all unique patient pathway variants, calculating frequencies, lengths,
    and cumulative case coverage.
    
    Generates:
    - outputs/tables/process_variants_summary.csv
    
    Returns:
        Dict of variant analytics metrics.
    """
    output_dir = Path(tables_output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("[Variants Mining] Extracting patient pathway variants...")
    variants_dict = pm4py.get_variants_as_tuples(event_log_df)
    total_cases = event_log_df[CASE_COL].nunique()

    # Sort variants by descending frequency
    sorted_variants = sorted(variants_dict.items(), key=lambda x: x[1], reverse=True)

    rows = []
    cumulative_cases = 0

    for idx, (trace_tuple, freq) in enumerate(sorted_variants, start=1):
        cumulative_cases += freq
        coverage_pct = round(100.0 * freq / total_cases, 2)
        cum_coverage_pct = round(100.0 * cumulative_cases / total_cases, 2)

        rows.append({
            "variant_id": f"V{idx:03d}",
            "case_frequency": freq,
            "case_coverage_pct": coverage_pct,
            "cumulative_coverage_pct": cum_coverage_pct,
            "pathway_length": len(trace_tuple),
            "entry_activity": trace_tuple[0] if trace_tuple else "",
            "exit_activity": trace_tuple[-1] if trace_tuple else "",
            "pathway_signature": " -> ".join(trace_tuple)
        })

    variants_df = pd.DataFrame(rows)
    variants_file = output_dir / "process_variants_summary.csv"
    variants_df.to_csv(variants_file, index=False)

    top_10_coverage = variants_df.iloc[:10]["case_coverage_pct"].sum()
    top_20_coverage = variants_df.iloc[:20]["case_coverage_pct"].sum()

    metrics = {
        "total_cases": total_cases,
        "unique_variants": len(variants_df),
        "most_frequent_variant": variants_df.iloc[0]["variant_id"],
        "most_frequent_frequency": int(variants_df.iloc[0]["case_frequency"]),
        "most_frequent_coverage_pct": float(variants_df.iloc[0]["case_coverage_pct"]),
        "top_10_variants_coverage_pct": round(float(top_10_coverage), 2),
        "top_20_variants_coverage_pct": round(float(top_20_coverage), 2),
        "longest_pathway_length": int(variants_df["pathway_length"].max()),
        "shortest_pathway_length": int(variants_df["pathway_length"].min()),
        "average_pathway_length": round(float(variants_df["pathway_length"].mean()), 2),
        "variants_summary_file": str(variants_file)
    }

    print(f"[Variants Mining] Completed successfully!")
    print(f"  - Total unique variants: {metrics['unique_variants']:,} across {metrics['total_cases']:,} cases")
    print(f"  - Top variant {metrics['most_frequent_variant']}: {metrics['most_frequent_frequency']} cases ({metrics['most_frequent_coverage_pct']}%)")
    print(f"  - Top 10 variants coverage: {metrics['top_10_variants_coverage_pct']}% of all cases")
    print(f"  - Saved variants table to: {variants_file}")

    return metrics


if __name__ == "__main__":
    from src.process_mining.log_manager import create_pm4py_event_log

    project_root = Path(__file__).resolve().parents[2]
    cleaned_csv = project_root / "data" / "processed" / "sepsis_cleaned.csv"
    tables_dir = project_root / "outputs" / "tables"

    log_df, _ = create_pm4py_event_log(cleaned_csv)
    run_variants_mining(log_df, tables_dir)
