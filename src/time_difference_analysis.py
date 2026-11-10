"""
Time Difference & Activity Transition Analysis Runner
Generates transition counts, waiting times, and transition probability matrix.
Author: Madhura (Member 2 - Process Analytics)
"""

from pathlib import Path
import sys

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.analysis.transitions_analysis import generate_transitions_analysis


def main():
    times_file = project_root / "data" / "processed" / "sepsis_with_times.csv"
    processed_file = project_root / "data" / "processed" / "activity_time_differences.csv"
    tables_folder = project_root / "outputs" / "tables"

    print("Running Activity Transitions & Waiting Time Analysis...")
    generate_transitions_analysis(times_file, processed_file, tables_folder)


if __name__ == "__main__":
    main()
