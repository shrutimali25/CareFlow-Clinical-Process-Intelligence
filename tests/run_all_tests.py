"""
CareFlow - Master Automated Test Runner
Discovers and executes all unit, integration, and end-to-end regression test suites.
Authors: Shruti (Member 1) & Madhura (Member 2)
"""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def run_all_tests():
    print("\n" + "=" * 70)
    print("  CAREFLOW: EXECUTING FULL AUTOMATED TEST SUITE")
    print("=" * 70)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Import test modules
    from tests import (
        test_data_pipeline,
        test_process_mining,
        test_advanced_analysis,
        test_powerbi_exports,
        test_end_to_end
    )

    modules = [
        test_data_pipeline,
        test_process_mining,
        test_advanced_analysis,
        test_powerbi_exports,
        test_end_to_end
    ]

    for mod in modules:
        suite.addTests(loader.loadTestsFromModule(mod))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    print("  TEST SUITE EXECUTION SUMMARY")
    print("=" * 70)
    print(f"  Total Tests Executed: {result.testsRun}")
    print(f"  Tests Passed:         {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  Tests Failed:         {len(result.failures)}")
    print(f"  Tests Errored:        {len(result.errors)}")
    print(f"  Overall Status:       {'SUCCESS (100% PASS)' if result.wasSuccessful() else 'FAILED'}")
    print("=" * 70 + "\n")

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
