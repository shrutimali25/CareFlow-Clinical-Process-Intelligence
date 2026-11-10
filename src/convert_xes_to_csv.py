"""
XES to CSV Conversion Script
Converts raw Sepsis XES event log into CSV.
Author: Shruti (Member 1 - Data Engineering)
"""

from pathlib import Path
import sys

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.data.convert_xes import convert_xes_to_csv


def main():
    input_file = project_root / "data" / "raw" / "sepsis.xes.gz"
    output_file = project_root / "data" / "processed" / "sepsis_event_log.csv"

    print("Running XES to CSV Conversion...")
    convert_xes_to_csv(input_file, output_file)


if __name__ == "__main__":
    main()
