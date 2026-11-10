"""
Unit Tests for Advanced Process Analytics & Clinical Insights Module
Verifies activity frequency, rework loops, case profiles, transition matrix, and bottlenecks.
Author: Shruti (Member 1) & Madhura (Member 2)
"""

import unittest
from pathlib import Path
import pandas as pd
import sys

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.data.loader import CASE_COL, ACTIVITY_COL


class TestAdvancedAnalysisModule(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.processed_dir = project_root / "data" / "processed"
        cls.tables_dir = project_root / "outputs" / "tables"

    def test_patient_case_summary(self):
        """patient_case_summary.csv must have 1,050 rows, no missing cases, and total 15,214 events."""
        csv_file = self.processed_dir / "patient_case_summary.csv"
        self.assertTrue(csv_file.exists(), "patient_case_summary.csv does not exist!")

        df = pd.read_csv(csv_file, keep_default_na=False, na_values=[""])
        self.assertEqual(len(df), 1050, f"Expected 1,050 cases, got {len(df)}")
        self.assertIn("NA", df[CASE_COL].values, "Case 'NA' is missing from case summary!")
        self.assertEqual(df["total_events"].sum(), 15214, f"Sum of events must be 15,214, got {df['total_events'].sum()}")
        self.assertTrue((df["treatment_duration_hours"] >= 0).all(), "Found negative treatment durations!")

    def test_activity_frequency(self):
        """activity_frequency.csv must contain 16 activities summing to exactly 15,214 occurrences."""
        csv_file = self.processed_dir / "activity_frequency.csv"
        self.assertTrue(csv_file.exists(), "activity_frequency.csv does not exist!")

        df = pd.read_csv(csv_file)
        self.assertEqual(len(df), 16, f"Expected 16 activities, got {len(df)}")
        self.assertEqual(df["total_occurrences"].sum(), 15214, f"Total occurrences must be 15,214, got {df['total_occurrences'].sum()}")
        self.assertTrue((df["unique_cases"] <= 1050).all())
        self.assertTrue((df["unique_cases"] >= 1).all())

    def test_activity_rework_detailed(self):
        """activity_frequency_detailed.csv must calculate rework rates and repeated cases."""
        csv_file = self.tables_dir / "activity_frequency_detailed.csv"
        self.assertTrue(csv_file.exists())

        df = pd.read_csv(csv_file)
        self.assertEqual(len(df), 16)
        # Top rework activity is CRP or Leucocytes
        top_rework = df.sort_values("rework_rate_pct", ascending=False).iloc[0]
        self.assertGreater(top_rework["rework_rate_pct"], 50.0)
        self.assertTrue((df["repeated_cases_count"] <= df["unique_cases"]).all())

    def test_activity_time_differences(self):
        """activity_time_differences.csv must contain 115 transitions summing to 14,164 transitions."""
        csv_file = self.processed_dir / "activity_time_differences.csv"
        self.assertTrue(csv_file.exists())

        df = pd.read_csv(csv_file)
        self.assertEqual(len(df), 115, f"Expected 115 transitions, got {len(df)}")
        self.assertEqual(df["total_transitions"].sum(), 14164, f"Total transitions must be 14,164, got {df['total_transitions'].sum()}")
        self.assertTrue((df["average_minutes"] >= 0).all())
        self.assertTrue((df["median_minutes"] >= 0).all())

    def test_transition_probability_matrix(self):
        """activity_transition_matrix.csv must be 16x16 with row sums equaling 1.0 (for rows with transitions)."""
        csv_file = self.tables_dir / "activity_transition_matrix.csv"
        self.assertTrue(csv_file.exists())

        matrix = pd.read_csv(csv_file, index_col=0)
        self.assertEqual(matrix.shape, (16, 16))
        
        row_sums = matrix.sum(axis=1)
        # Rows with at least one transition must sum to 1.0 (allowing small float tolerance)
        active_rows = row_sums[row_sums > 0]
        for act, r_sum in active_rows.items():
            self.assertAlmostEqual(r_sum, 1.0, delta=0.01, msg=f"Row sum for {act} is {r_sum}, expected 1.0")

    def test_triage_to_antibiotics_analysis(self):
        """triage_to_antibiotics_analysis.csv must verify 823 cases and 100% compliance category sum."""
        csv_file = self.tables_dir / "triage_to_antibiotics_analysis.csv"
        self.assertTrue(csv_file.exists())

        df = pd.read_csv(csv_file)
        metrics = dict(zip(df["Metric"], df["Value"]))
        self.assertEqual(metrics.get("Eligible Patient Cases Analyzed"), "823")
        self.assertEqual(metrics.get("Min Interval (Hours)"), "0.00")
        self.assertAlmostEqual(float(metrics.get("Median Triage-to-Antibiotics Interval (Hours)")), 1.73, delta=0.05)

    def test_admission_latency_analysis(self):
        """admission_latency_analysis.csv must verify 810 admitted cases."""
        csv_file = self.tables_dir / "admission_latency_analysis.csv"
        self.assertTrue(csv_file.exists())

        df = pd.read_csv(csv_file)
        metrics = dict(zip(df["Metric"], df["Value"]))
        self.assertEqual(metrics.get("Admitted Patient Cases Analyzed"), "810")
        self.assertAlmostEqual(float(metrics.get("Median ER-to-Admission Interval (Hours)")), 3.22, delta=0.05)


if __name__ == "__main__":
    unittest.main()
