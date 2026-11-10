"""
Activity Analysis Runner
Generates activity occurrence and case reach summaries with 15,214 verified events.
Author: Shruti (Member 1 - Data Engineering)
"""

from pathlib import Path
import sys

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.analysis.activity_summary import generate_activity_summary


def main():
    times_file = project_root / "data" / "processed" / "sepsis_with_times.csv"
    processed_file = project_root / "data" / "processed" / "activity_frequency.csv"
    tables_folder = project_root / "outputs" / "tables"

    print("Running Activity Frequency Analysis...")
    generate_activity_summary(times_file, processed_file, tables_folder)


if __name__ == "__main__":
    main()
