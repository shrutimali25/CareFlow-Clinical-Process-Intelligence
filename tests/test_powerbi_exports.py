"""
Unit Tests for Power BI Star-Schema Datasets
Verifies table row counts, relational keys, schema consistency, and metric integrity.
Author: Shruti (Member 1) & Madhura (Member 2)
"""

import unittest
from pathlib import Path
import pandas as pd
import sys

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestPowerBIDatasets(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pbi_dir = project_root / "data" / "powerbi"

    def test_fact_event_log(self):
        """fact_event_log.csv must contain exactly 15,214 events."""
        csv_file = self.pbi_dir / "fact_event_log.csv"
        self.assertTrue(csv_file.exists())
        df = pd.read_csv(csv_file, keep_default_na=False, na_values=[""])
        self.assertEqual(len(df), 15214, f"Expected 15,214 events, got {len(df)}")
        self.assertIn("Case_ID", df.columns)
        self.assertIn("Activity", df.columns)
        self.assertIn("Elapsed_Minutes", df.columns)
        self.assertEqual(df["Is_First_Event"].sum(), 1050, "Expected 1,050 first events")

    def test_dim_patient_cases(self):
        """dim_patient_cases.csv must contain exactly 1,050 cases with valid Variant_ID."""
        csv_file = self.pbi_dir / "dim_patient_cases.csv"
        self.assertTrue(csv_file.exists())
        df = pd.read_csv(csv_file, keep_default_na=False, na_values=[""])
        self.assertEqual(len(df), 1050, f"Expected 1,050 cases, got {len(df)}")
        self.assertIn("NA", df["Case_ID"].values, "Case 'NA' is missing!")
        self.assertEqual(df["Variant_ID"].isna().sum(), 0, "All cases must map to a Variant_ID")

    def test_dim_activities(self):
        """dim_activities.csv must contain 16 activities summing to 15,214 occurrences."""
        csv_file = self.pbi_dir / "dim_activities.csv"
        self.assertTrue(csv_file.exists())
        df = pd.read_csv(csv_file)
        self.assertEqual(len(df), 16)
        self.assertEqual(df["Total_Occurrences"].sum(), 15214)

    def test_fact_transitions(self):
        """fact_transitions.csv must contain 115 transitions summing to 14,164 transitions."""
        csv_file = self.pbi_dir / "fact_transitions.csv"
        self.assertTrue(csv_file.exists())
        df = pd.read_csv(csv_file)
        self.assertEqual(len(df), 115)
        self.assertEqual(df["Transition_Count"].sum(), 14164)

    def test_dim_variants(self):
        """dim_variants.csv must contain 846 variants summing to 1,050 cases."""
        csv_file = self.pbi_dir / "dim_variants.csv"
        self.assertTrue(csv_file.exists())
        df = pd.read_csv(csv_file)
        self.assertEqual(len(df), 846)
        self.assertEqual(df["case_frequency"].sum(), 1050)

    def test_fact_bottlenecks(self):
        """fact_bottlenecks.csv must contain 1,050 patient rows."""
        csv_file = self.pbi_dir / "fact_bottlenecks.csv"
        self.assertTrue(csv_file.exists())
        df = pd.read_csv(csv_file, keep_default_na=False, na_values=[""])
        self.assertEqual(len(df), 1050)

    def test_dim_data_quality(self):
        """dim_data_quality.csv must contain 10 checks and 0 FAIL status."""
        csv_file = self.pbi_dir / "dim_data_quality.csv"
        self.assertTrue(csv_file.exists())
        df = pd.read_csv(csv_file)
        self.assertEqual(len(df), 10)
        self.assertNotIn("FAIL", df["Status"].values)


if __name__ == "__main__":
    unittest.main()
