"""
Data Quality Validation Script
Generates data quality checks and verification metrics for the CareFlow event log.
Author: Shruti (Member 1 - Data Engineering)
"""

from pathlib import Path
import sys

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.validation.validator import validate_dataset


def main():
    input_file = project_root / "data" / "processed" / "sepsis_with_times.csv"
    reports_folder = project_root / "reports"

    print("Running Data Quality Validation...")
    validate_dataset(input_file, reports_folder)


if __name__ == "__main__":
    main()
