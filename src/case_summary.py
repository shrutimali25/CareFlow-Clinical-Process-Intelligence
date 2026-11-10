"""
Patient Case Summary Runner
Generates patient-level case summaries with 1,050 verified cases.
Author: Shruti (Member 1 - Data Engineering)
"""

from pathlib import Path
import sys

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.analysis.case_profiler import generate_case_profiles


def main():
    times_file = project_root / "data" / "processed" / "sepsis_with_times.csv"
    processed_file = project_root / "data" / "processed" / "patient_case_summary.csv"
    tables_folder = project_root / "outputs" / "tables"

    print("Running Patient Case Profiling...")
    generate_case_profiles(times_file, processed_file, tables_folder)


if __name__ == "__main__":
    main()
