# CareFlow: Execution & Setup Guide

> **Project:** CareFlow – Patient Journey Analysis Using Process Mining  
> **Platform Compatibility:** Windows 10/11, macOS, Linux (Optimized for 8 GB RAM laptops)  
> **Primary Authors:** Shruti (Member 1) & Madhura (Member 2)  

---

## 1. Prerequisites & Environment Setup

### System Requirements
- **Operating System:** Windows 10 or 11 (64-bit).
- **RAM:** 8 GB or higher (CareFlow peak memory footprint is $< 35\text{ MB}$).
- **Disk Space:** At least 200 MB free.
- **Python:** Version 3.10, 3.11, 3.12, 3.13, 3.14, or 3.15.

### Step 1: Clone Repository & Switch to Working Branch
Open PowerShell or Command Prompt:
```powershell
# Navigate to projects directory
cd D:\Projects

# Clone repository (if not already local)
git clone https://github.com/shrutimali25/CareFlow.git CareFlow-Clinical-Process-Intelligence
cd CareFlow-Clinical-Process-Intelligence

# Ensure you are on the shruti branch
git checkout shruti
```

### Step 2: Create & Activate Virtual Environment
```powershell
# Create virtual environment
python -m venv .venv

# Activate on Windows PowerShell
.venv\Scripts\Activate.ps1

# (If PowerShell blocks script execution, run: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass)
```

### Step 3: Install Required Dependencies
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 2. Running the Complete Pipeline (One-Click)

To execute the entire clinical pipeline from raw XES decompression to Power BI Star-Schema generation with automated verification and memory benchmarking, run:

```powershell
python run_pipeline.py
```

### Expected Output Summary
```text
======================================================================
  CAREFLOW PIPELINE EXECUTION SUMMARY & RESOURCE BENCHMARK
======================================================================
  Status:                    SUCCESS (100% Verified)
  Total Execution Time:      ~17.2 seconds
  Current Memory In-Use:     10.9 MB
  Peak Memory Consumption:   33.7 MB
  Target RAM Envelope:       < 500 MB (Fully compatible with 8 GB RAM laptop)
  Total Events Processed:    15,214 events
  Total Patient Cases:       1,050 cases (Case 'NA' verified)
  Clinical Activities:       16 activities
  Process Transitions:       14,164 transitions (115 unique pairs)
  Process Variants:          846 unique pathways
  Reconciliation Match:      100.0% (Zero missing or extra records)
======================================================================
```

---

## 3. Running Modules Individually (Step-by-Step)

If you prefer to execute specific modules individually, use the following commands:

### Stage 1: XES to CSV Conversion
```powershell
python src/convert_xes_to_csv.py
```
*Outputs: `data/processed/sepsis_event_log.csv` (15,214 rows)*

### Stage 2: Data Cleaning & Case ID 'NA' Preservation
```powershell
python src/Clean_data.py
```
*Outputs: `data/processed/sepsis_cleaned.csv` (15,214 rows)*

### Stage 3: Time Features & Transition Sequencing
```powershell
python src/calculate_times.py
```
*Outputs: `data/processed/sepsis_with_times.csv` (15,214 rows, 36 columns)*

### Stage 4: Data Quality & Monotonicity Validation
```powershell
python src/validate_data.py
# or
python src/final_validation.py
```
*Outputs: `reports/data_quality_report.csv`, `reports/final_data_validation_report.csv`*

### Stage 5: Full XES vs CSV Reconciliation
```powershell
python src/reconcile_xes_csv.py
```
*Outputs: `reports/reconciliation_summary.csv` (100.0% Match)*

### Stage 6 & 7: PM4Py Process Mining & Visualizations
```powershell
python src/process_mining/run_process_mining.py
```
*Outputs:*
- Models: `outputs/models/inductive_petri_net.pnml`, `inductive_bpmn.bpmn`, `heuristics_petri_net.pnml`
- Maps: `outputs/figures/dfg_frequency_process_map.png`, `dfg_performance_bottleneck_map.png`, `top_variants_distribution.png`, `careflow_interactive_process_map.html`
- Tables: `outputs/tables/dfg_frequency_table.csv`, `dfg_performance_table.csv`, `process_variants_summary.csv`

### Stage 8: Advanced Analytics & Bottleneck Identification
```powershell
python src/activity_analysis.py
python src/case_summary.py
python src/time_difference_analysis.py
python src/analysis/bottleneck_analysis.py
```
*Outputs:*
- `data/processed/patient_case_summary.csv` (1,050 rows)
- `data/processed/activity_frequency.csv` (16 rows)
- `data/processed/activity_time_differences.csv` (115 rows)
- `outputs/tables/triage_to_antibiotics_analysis.csv`
- `outputs/tables/admission_latency_analysis.csv`
- `outputs/tables/clinical_bottlenecks_summary.csv`

### Stage 9: Power BI Star-Schema Datasets
```powershell
python src/prepare_powerbi_data.py
```
*Outputs: 7 Star-Schema CSVs in `data/powerbi/`*

---

## 4. Running the Automated Test Suite

CareFlow includes a comprehensive automated test suite consisting of 31 test cases across 5 test suites.

### Run All 31 Tests:
```powershell
python tests/run_all_tests.py
```

### Run Test Suites Individually:
```powershell
# Data Engineering pipeline tests (5 tests)
python tests/test_data_pipeline.py

# Process Mining discovery tests (6 tests)
python tests/test_process_mining.py

# Advanced Analysis & Bottlenecks tests (7 tests)
python tests/test_advanced_analysis.py

# Power BI schema & key referential tests (7 tests)
python tests/test_powerbi_exports.py

# End-to-end integration & reproducibility tests (6 tests)
python tests/test_end_to_end.py
```

---

## 5. Troubleshooting & FAQ

### Q1: Why does `pm4py.write_bpmn` or graphviz throw an error if called directly?
*Answer:* In standard PM4Py, `write_bpmn` attempts to call the external `dot.exe` (Graphviz binary) to compute diagram layout coordinates. CareFlow solves this by passing `auto_layout=False`, allowing BPMN export without external binaries, and using pure **NetworkX + Matplotlib** for image rendering.

### Q2: Why does pandas lose Case ID "NA"?
*Answer:* By default, `pandas.read_csv()` treats the characters `"NA"` as missing (`NaN`). CareFlow uses `src/data/loader.py` with `keep_default_na=False, na_values=[""]` and explicit string typing to guarantee that patient `"NA"` and its 24 recorded events are preserved.

### Q3: How do I view the interactive process map?
*Answer:* Open `outputs/figures/careflow_interactive_process_map.html` in any web browser (Chrome, Edge, Firefox). It is a standalone, offline HTML5 application with node dragging and dynamic edge filtering.
