# CareFlow: Quality Assurance & Testing Report

> **Project:** CareFlow – Patient Journey Analysis Using Process Mining
> **Total Test Cases:** 31
> **Passed:** 31 (100%)
> **Failed:** 0
> **Latest Master Test-Run Duration:** 0.401 seconds (one verified run; environment-dependent)
> **Test Framework:** Python `unittest`, executed through `tests/run_all_tests.py`
> **Primary Authors:** Shruti (Member 1 - Data Engineering) & Madhura (Member 2 - Process Mining)

---

## 1. Quality Assurance Strategy

The CareFlow QA architecture enforces strict end-to-end verification across every stage of the data and process intelligence lifecycle:
1. **Schema & Identifier Invariance:** Enforces preservation of alphanumeric case IDs (specifically `"NA"`).
2. **Clinical Assay Preservation:** Prevents silent truncation of legitimate repeated clinical measurements (e.g. repeated laboratory blood tubes drawn at identical timestamps).
3. **Trace Monotonicity:** Verifies non-decreasing chronological event progression ($\Delta t \ge 0$) across all 1,050 patient traces.
4. **Reconciliation Zero-Defect:** Compares raw IEEE 1849 XES XML streams directly against CSV outputs down to the individual event level.
5. **Model Artifact Checks:** Verifies exported Inductive Petri Net and BPMN files and the Heuristics dependency matrix. These checks do not prove Petri Net soundness, deadlock-freedom, or trace fitness.
6. **Referential Integrity:** Automated testing checks event-to-patient case references. A separate manual audit checked 12 key and reference conditions across the seven Power BI CSV tables; all 12 passed.

---

## 2. Master Test Suite Results Summary

```text
======================================================================
  CAREFLOW: EXECUTING FULL AUTOMATED TEST SUITE
======================================================================
Ran 31 tests in 0.401s (latest verified master-runner execution)

OK

======================================================================
  TEST SUITE EXECUTION SUMMARY
======================================================================
  Total Tests Executed: 31
  Tests Passed:         31 (100.0%)
  Tests Failed:         0
  Tests Errored:        0
  Overall Status:       SUCCESS (100% PASS)
======================================================================
```

---

## 3. Test Cases Inventory & Verification Matrix

### Suite 1: Data Engineering Pipeline (`tests/test_data_pipeline.py`)
| Test Identifier | Test Target / Assertion | Result |
| :--- | :--- | :---: |
| `test_cleaned_file_integrity` | Verifies `sepsis_cleaned.csv` contains exactly 15,214 events, 1,050 cases, 16 activities | **PASS** |
| `test_case_na_preservation` | Asserts patient `"NA"` exists as a string identifier with exactly 24 recorded events | **PASS** |
| `test_times_file_integrity` | Verifies `sepsis_with_times.csv` has 15,214 events, 1,050 initial events, and 0 negative elapsed times | **PASS** |
| `test_chronological_ordering` | Asserts that all 1,050 patient traces have non-decreasing timestamps | **PASS** |
| `test_reconciliation_report` | Validates `reconciliation_summary.csv` shows 0 missing and 0 extra events (100.0% match) | **PASS** |

### Suite 2: PM4Py Process Mining Discovery (`tests/test_process_mining.py`)
| Test Identifier | Test Target / Assertion | Result |
| :--- | :--- | :---: |
| `test_log_preparation_integrity` | Validates PM4Py DataFrame formatting classifiers (`case:concept:name`, `concept:name`, `time:timestamp`) | **PASS** |
| `test_inductive_models_exported` | Asserts discovery and non-empty export of `inductive_petri_net.pnml` and `inductive_bpmn.bpmn` | **PASS** |
| `test_heuristics_models_exported`| Asserts discovery of `heuristics_petri_net.pnml` and $16 \times 16$ dependency matrix | **PASS** |
| `test_dfg_tables_integrity` | Asserts Directly-Follows Graph contains exactly 115 transitions summing to 14,164 events | **PASS** |
| `test_variants_mining_integrity`| Verifies 846 unique process variants summing to 1,050 cases with 100% cumulative coverage | **PASS** |
| `test_visual_figures_exported` | Verifies generation and integrity of all PNG maps and standalone HTML interactive viewer | **PASS** |

### Suite 3: Advanced Analysis & Clinical Insights (`tests/test_advanced_analysis.py`)
| Test Identifier | Test Target / Assertion | Result |
| :--- | :--- | :---: |
| `test_patient_case_summary` | Verifies `patient_case_summary.csv` has 1,050 rows, preserves Case `"NA"`, and events sum to 15,214 | **PASS** |
| `test_activity_frequency` | Verifies `activity_frequency.csv` contains 16 activities summing to 15,214 occurrences | **PASS** |
| `test_activity_rework_detailed` | Asserts calculation of rework rates, identifying CRP (68.7%) and Leucocytes (66.9%) as top re-assays | **PASS** |
| `test_activity_time_differences`| Verifies 115 transition pairs summing to 14,164 transitions with non-negative waiting times | **PASS** |
| `test_transition_probability_matrix`| Asserts $16 \times 16$ transition probability matrix row sums equal 1.0000 | **PASS** |
| `test_triage_to_antibiotics_analysis`| Validates Golden Hour cohort (823 cases, median latency = 1.73h, 0 negative intervals) | **PASS** |
| `test_admission_latency_analysis`| Validates ER boarding cohort (810 admitted cases, median latency = 3.22h) | **PASS** |

### Suite 4: Power BI Star-Schema Integration (`tests/test_powerbi_exports.py`)
| Test Identifier | Test Target / Assertion | Result |
| :--- | :--- | :---: |
| `test_fact_event_log` | Validates `fact_event_log.csv` has 15,214 rows and 1,050 first events | **PASS** |
| `test_dim_patient_cases` | Validates `dim_patient_cases.csv` has 1,050 rows, preserves Case `"NA"`, and has 0 unmapped Variant_IDs | **PASS** |
| `test_dim_activities` | Validates `dim_activities.csv` has 16 activities summing to 15,214 occurrences | **PASS** |
| `test_fact_transitions` | Validates `fact_transitions.csv` has 115 transitions summing to 14,164 transitions | **PASS** |
| `test_dim_variants` | Validates `dim_variants.csv` has 846 variants summing to 1,050 cases | **PASS** |
| `test_fact_bottlenecks` | Validates `fact_bottlenecks.csv` has 1,050 patient rows with Golden Hour compliance cohorts | **PASS** |
| `test_dim_data_quality` | Asserts that all 10 automated data quality checks have status PASS or INFO | **PASS** |

### Suite 5: System Integration & Reproducibility (`tests/test_end_to_end.py`)
| Test Identifier | Test Target / Assertion | Result |
| :--- | :--- | :---: |
| `test_pipeline_artifact_inventory` | Verifies existence and non-zero byte size of all 19 pipeline output artifacts | **PASS** |
| `test_core_numerical_identities` | Mathematical proof: $\sum(N_i - 1) = 15,214 - 1,050 = 14,164$ transitions | **PASS** |
| `test_case_na_integrity` | Verifies Case `"NA"` has 24 events across all normalized tables | **PASS** |
| `test_reconciliation_zero_defect`| Confirms 0 missing and 0 extra events in reconciliation report | **PASS** |
| `test_process_mining_variants_sum`| Confirms 846 variants sum to 1,050 cases | **PASS** |
| `test_powerbi_star_schema_keys` | Verifies 100% referential integrity between `Fact_Event_Log[Case_ID]` and `Dim_Patient_Cases[Case_ID]` | **PASS** |

---

## 4. Test Execution & Historical Resource Notes

### Latest Verified Master Test Run

- **Runner:** `tests/run_all_tests.py`, using Python `unittest`.
- **Result:** 31 tests executed, 31 passed, 0 failed, 0 errors.
- **Observed test duration:** 0.401 seconds in the latest verified run.
- This is test-suite runtime, not full pipeline runtime. Execution time varies by environment.

### Previously Recorded Pipeline and Resource Measurements

- **Earlier recorded pipeline runs:** 17.36 seconds and 17.17 seconds. These are pipeline timings, not test-suite timings.
- **Previously reported peak memory:** 33.66 MB. The measurement method has not been independently verified in this audit.
- **Variance:** No 0.00% deterministic variance claim is made.
- **RAM budget:** Less than 500 MB remains a stated project target, not a newly verified benchmark.
