"""
Unit Tests for CareFlow Data Engineering Pipeline
Verifies data loading, cleaning, time features, and reconciliation.
Author: Shruti (Member 1 - Data Engineering)
"""

import unittest
from pathlib import Path
import pandas as pd
import sys

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.data.loader import load_event_log, CASE_COL, ACTIVITY_COL, TIMESTAMP_COL


class TestDataEngineeringPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cleaned_file = project_root / "data" / "processed" / "sepsis_cleaned.csv"
        cls.times_file = project_root / "data" / "processed" / "sepsis_with_times.csv"
        cls.reports_dir = project_root / "reports"

    def test_cleaned_file_integrity(self):
        """Cleaned CSV must contain exactly 15,214 events, 1,050 cases, 16 activities."""
        df = load_event_log(self.cleaned_file, parse_timestamps=True)
        self.assertEqual(len(df), 15214, f"Expected 15,214 events, got {len(df)}")
        self.assertEqual(df[CASE_COL].nunique(), 1050, f"Expected 1,050 cases, got {df[CASE_COL].nunique()}")
        self.assertEqual(df[ACTIVITY_COL].nunique(), 16, f"Expected 16 activities, got {df[ACTIVITY_COL].nunique()}")

    def test_case_na_preservation(self):
        """Case ID 'NA' must be preserved and contain exactly 24 events."""
        df = load_event_log(self.times_file, parse_timestamps=True)
        self.assertIn("NA", df[CASE_COL].values, "Case 'NA' was lost or parsed as NaN!")
        na_count = (df[CASE_COL] == "NA").sum()
        self.assertEqual(na_count, 24, f"Case 'NA' expected 24 events, got {na_count}")

    def test_times_file_integrity(self):
        """Enriched CSV must have 15,214 events, 1,050 cases, and 0 negative elapsed times."""
        df = load_event_log(self.times_file, parse_timestamps=True)
        self.assertEqual(len(df), 15214, f"Expected 15,214 events, got {len(df)}")
        self.assertEqual(df[CASE_COL].nunique(), 1050, f"Expected 1,050 cases, got {df[CASE_COL].nunique()}")
        
        # Verify no negative elapsed times
        negative_times = (df["elapsed_minutes"] < 0).sum()
        self.assertEqual(negative_times, 0, f"Found {negative_times} negative elapsed times!")

        # Verify initial case events count equals unique cases (1,050)
        first_events = df["previous_event_time"].isna().sum()
        self.assertEqual(first_events, 1050, f"Expected 1,050 first events, got {first_events}")

    def test_chronological_ordering(self):
        """All 1,050 patient traces must be monotonically increasing in time."""
        df = load_event_log(self.times_file, parse_timestamps=True)
        order_check = df.groupby(CASE_COL)[TIMESTAMP_COL].apply(
            lambda s: s.is_monotonic_increasing
        )
        self.assertTrue(order_check.all(), "Found cases with non-chronological events!")

    def test_reconciliation_report(self):
        """Reconciliation report must confirm 0 missing and 0 extra event occurrences."""
        reconcile_file = self.reports_dir / "reconciliation_summary.csv"
        self.assertTrue(reconcile_file.exists(), "Reconciliation summary file does not exist!")
        summary = pd.read_csv(reconcile_file)
        metric_dict = dict(zip(summary["Metric"], summary["Value"]))
        
        self.assertEqual(metric_dict.get("XES total events"), "15214")
        self.assertEqual(metric_dict.get("CSV total events"), "15214")
        self.assertEqual(metric_dict.get("Missing event occurrences"), "0")
        self.assertEqual(metric_dict.get("Extra event occurrences"), "0")
        self.assertEqual(metric_dict.get("Reconciliation Match %"), "100.0%")


if __name__ == "__main__":
    unittest.main()
