"""
Unit and Integration Tests for PM4Py Process Mining Module
Verifies Inductive Miner, Heuristics Miner, DFG, Variants, and Model Artifacts.
Author: Madhura (Member 2 - Process Mining)
"""

import unittest
from pathlib import Path
import pandas as pd
import sys

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.process_mining.log_manager import create_pm4py_event_log


class TestProcessMiningModule(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cleaned_csv = project_root / "data" / "processed" / "sepsis_cleaned.csv"
        cls.models_dir = project_root / "outputs" / "models"
        cls.tables_dir = project_root / "outputs" / "tables"
        cls.figures_dir = project_root / "outputs" / "figures"

        cls.log_df, cls.stats = create_pm4py_event_log(cls.cleaned_csv)

    def test_log_preparation_integrity(self):
        """Verifies PM4Py formatted log retains all verified Sepsis statistics."""
        self.assertEqual(self.stats["total_events"], 15214)
        self.assertEqual(self.stats["unique_cases"], 1050)
        self.assertEqual(self.stats["unique_activities"], 16)
        self.assertTrue(self.stats["has_case_NA"])
        self.assertEqual(self.stats["case_NA_events"], 24)

    def test_inductive_models_exported(self):
        """Verifies Inductive Miner Petri Net (.pnml) and BPMN (.bpmn) were exported."""
        pnml = self.models_dir / "inductive_petri_net.pnml"
        bpmn = self.models_dir / "inductive_bpmn.bpmn"

        self.assertTrue(pnml.exists(), "Inductive PNML model does not exist!")
        self.assertGreater(pnml.stat().st_size, 10000)

        self.assertTrue(bpmn.exists(), "Inductive BPMN model does not exist!")
        self.assertGreater(bpmn.stat().st_size, 20000)

    def test_heuristics_models_exported(self):
        """Verifies Heuristics Miner Petri Net and Dependency Matrix were generated."""
        heu_pnml = self.models_dir / "heuristics_petri_net.pnml"
        dep_csv = self.tables_dir / "heuristics_dependency_matrix.csv"

        self.assertTrue(heu_pnml.exists(), "Heuristics PNML model does not exist!")
        self.assertGreater(heu_pnml.stat().st_size, 15000)

        self.assertTrue(dep_csv.exists(), "Heuristics dependency matrix does not exist!")
        dep_df = pd.read_csv(dep_csv, index_col=0)
        self.assertEqual(dep_df.shape, (16, 16), f"Expected 16x16 dependency matrix, got {dep_df.shape}")

    def test_dfg_tables_integrity(self):
        """Verifies DFG frequency and performance tables have 115 transitions matching 14,164 events."""
        freq_csv = self.tables_dir / "dfg_frequency_table.csv"
        perf_csv = self.tables_dir / "dfg_performance_table.csv"

        self.assertTrue(freq_csv.exists())
        self.assertTrue(perf_csv.exists())

        freq_df = pd.read_csv(freq_csv)
        self.assertEqual(len(freq_df), 115, f"Expected 115 DFG edges, got {len(freq_df)}")
        self.assertEqual(freq_df["transition_count"].sum(), 14164, "Total transitions must equal 14,164")

        perf_df = pd.read_csv(perf_csv)
        self.assertEqual(len(perf_df), 115)
        self.assertTrue((perf_df["mean_duration_hours"] >= 0).all(), "Found negative mean duration in DFG!")

    def test_variants_mining_integrity(self):
        """Verifies 846 unique variants covering exactly 1,050 cases with 100% cumulative coverage."""
        var_csv = self.tables_dir / "process_variants_summary.csv"
        self.assertTrue(var_csv.exists())

        var_df = pd.read_csv(var_csv)
        self.assertEqual(len(var_df), 846, f"Expected 846 variants, got {len(var_df)}")
        self.assertEqual(var_df["case_frequency"].sum(), 1050, "Sum of variant frequencies must equal 1,050 cases")
        self.assertAlmostEqual(var_df.iloc[-1]["cumulative_coverage_pct"], 100.0, delta=0.1)

    def test_visual_figures_exported(self):
        """Verifies all PNG diagrams and interactive HTML maps were generated."""
        f1 = self.figures_dir / "dfg_frequency_process_map.png"
        f2 = self.figures_dir / "dfg_performance_bottleneck_map.png"
        f3 = self.figures_dir / "top_variants_distribution.png"
        f4 = self.figures_dir / "careflow_interactive_process_map.html"

        for f in [f1, f2, f3, f4]:
            self.assertTrue(f.exists(), f"Figure does not exist: {f}")
            self.assertGreater(f.stat().st_size, 5000, f"Figure file too small: {f}")


if __name__ == "__main__":
    unittest.main()
