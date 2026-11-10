"""
Data Cleaning Script for Sepsis Event Log
Standardizes timestamps, handles duplicate clinical measurements, and preserves valid Case ID 'NA'.
Author: Shruti (Member 1 - Data Engineering)
"""

from pathlib import Path
import sys

# Add project root to sys.path for direct script execution
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.data.cleaner import clean_event_log


def main():
    input_file = project_root / "data" / "processed" / "sepsis_event_log.csv"
    output_file = project_root / "data" / "processed" / "sepsis_cleaned.csv"

    print("Running Data Cleaning...")
    clean_event_log(input_file, output_file)


if __name__ == "__main__":
    main()
