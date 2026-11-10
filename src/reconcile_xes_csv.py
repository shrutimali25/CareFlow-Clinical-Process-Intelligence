"""
XES and CSV Reconciliation Runner
Reconciles processed CSV against raw XES file to ensure 100% data integrity.
Author: Shruti (Member 1 - Data Engineering)
"""

from pathlib import Path
import sys

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.validation.reconciliation import reconcile_datasets


def main():
    raw_xes = project_root / "data" / "raw" / "sepsis.xes.gz"
    processed_csv = project_root / "data" / "processed" / "sepsis_with_times.csv"
    reports_folder = project_root / "reports"

    print("Running Dataset Reconciliation (XES vs CSV)...")
    reconcile_datasets(raw_xes, processed_csv, reports_folder)


if __name__ == "__main__":
    main()
