"""
End-to-End System Integration Tests for CareFlow
Validates reproducibility, file system outputs, model formats, and data integrity across all phases.
Authors: Shruti (Member 1) & Madhura (Member 2)
"""

import unittest
from pathlib import Path
import pandas as pd
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class TestEndToEndCareFlow(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.root = PROJECT_ROOT
        cls.data_dir = cls.root / "data"
        cls.outputs_dir = cls.root / "outputs"
        cls.reports_dir = cls.root / "reports"
        cls.pbi_dir = cls.data_dir / "powerbi"

    def test_pipeline_artifact_inventory(self):
        """Verifies that all 19 essential output artifacts exist across directories."""
        required_files = [
            # Processed CSVs
            self.data_dir / "processed" / "sepsis_event_log.csv",
            self.data_dir / "processed" / "sepsis_cleaned.csv",
            self.data_dir / "processed" / "sepsis_with_times.csv",
            self.data_dir / "processed" / "patient_case_summary.csv",
            self.data_dir / "processed" / "activity_frequency.csv",
            self.data_dir / "processed" / "activity_time_differences.csv",
            # Reports
            self.reports_dir / "data_quality_report.csv",
            self.reports_dir / "final_data_validation_report.csv",
            self.reports_dir / "reconciliation_summary.csv",
            self.reports_dir / "powerbi_dashboard_guide.md",
            # Process Mining Models
            self.outputs_dir / "models" / "inductive_petri_net.pnml",
            self.outputs_dir / "models" / "inductive_bpmn.bpmn",
            self.outputs_dir / "models" / "heuristics_petri_net.pnml",
            # Visual Figures
            self.outputs_dir / "figures" / "dfg_frequency_process_map.png",
            self.outputs_dir / "figures" / "dfg_performance_bottleneck_map.png",
            self.outputs_dir / "figures" / "top_variants_distribution.png",
            self.outputs_dir / "figures" / "careflow_interactive_process_map.html",
            # Power BI Star Schema
            self.pbi_dir / "fact_event_log.csv",
            self.pbi_dir / "dim_patient_cases.csv"
        ]
        for f in required_files:
            self.assertTrue(f.exists(), f"Missing required pipeline artifact: {f}")
            self.assertGreater(f.stat().st_size, 0, f"Artifact is empty: {f}")

    def test_core_numerical_identities(self):
        """Verifies the core mathematical identities of the Sepsis dataset."""
        df_events = pd.read_csv(self.data_dir / "processed" / "sepsis_with_times.csv", keep_default_na=False, na_values=[""])
        self.assertEqual(len(df_events), 15214, "Total events must be 15,214")
        self.assertEqual(df_events["case:concept:name"].nunique(), 1050, "Total cases must be 1,050")
        self.assertEqual(df_events["concept:name"].nunique(), 16, "Total activities must be 16")

        # Identity: within-case transitions = total events - unique cases
        transitions_count = df_events["previous_activity"].notna().sum()
        self.assertEqual(transitions_count, 14164, "Within-case transitions must be 14,164")

        # Initial events count must equal unique cases
        initial_events_count = df_events["previous_activity"].isna().sum()
        self.assertEqual(initial_events_count, 1050, "Initial events must equal 1,050")

    def test_case_na_integrity(self):
        """Verifies patient 'NA' has exactly 24 events and is preserved across all tables."""
        df_events = pd.read_csv(self.data_dir / "processed" / "sepsis_with_times.csv", keep_default_na=False, na_values=[""])
        na_events = df_events[df_events["case:concept:name"] == "NA"]
        self.assertEqual(len(na_events), 24, "Patient 'NA' must have 24 events")

        df_cases = pd.read_csv(self.pbi_dir / "dim_patient_cases.csv", keep_default_na=False, na_values=[""])
        self.assertIn("NA", df_cases["Case_ID"].values, "Patient 'NA' missing from dim_patient_cases!")

    def test_reconciliation_zero_defect(self):
        """Verifies zero missing and zero extra events in reconciliation summary."""
        recon_df = pd.read_csv(self.reports_dir / "reconciliation_summary.csv")
        metrics = dict(zip(recon_df["Metric"], recon_df["Value"]))
        self.assertEqual(metrics.get("Missing event occurrences"), "0")
        self.assertEqual(metrics.get("Extra event occurrences"), "0")
        self.assertEqual(metrics.get("Reconciliation Match %"), "100.0%")

    def test_process_mining_variants_sum(self):
        """Verifies 846 variants sum to 1,050 cases."""
        var_df = pd.read_csv(self.outputs_dir / "tables" / "process_variants_summary.csv")
        self.assertEqual(len(var_df), 846)
        self.assertEqual(var_df["case_frequency"].sum(), 1050)

    def test_powerbi_star_schema_keys(self):
        """Verifies foreign key referential integrity between fact_event_log and dim_patient_cases."""
        df_events = pd.read_csv(self.pbi_dir / "fact_event_log.csv", keep_default_na=False, na_values=[""])
        df_cases = pd.read_csv(self.pbi_dir / "dim_patient_cases.csv", keep_default_na=False, na_values=[""])

        event_cases = set(df_events["Case_ID"].unique())
        dim_cases = set(df_cases["Case_ID"].unique())

        self.assertEqual(event_cases, dim_cases, "Foreign key mismatch between events and patient dimension!")


if __name__ == "__main__":
    unittest.main()
