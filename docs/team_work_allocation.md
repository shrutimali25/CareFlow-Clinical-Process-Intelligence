# CareFlow: Team Work Allocation & Engineering Ownership

> **Project:** CareFlow - Clinical Process Intelligence
> **Team size:** 2 members
> **Repository:** CareFlow-Clinical-Process-Intelligence
> **Integrated branch:** `main`
> **Development branches:** `shruti`, `madhura`

## 1. Purpose and attribution approach

This document describes the team's planned and reported areas of responsibility. It does not claim an equal percentage of contribution. The available Git history shows visible commits for the inspected modules under the author name Shruti Mali. Therefore, role allocation below should not be interpreted as independent Git proof of every individual's code authorship.

Both members should present the work they personally implemented, tested, or can confidently explain.

## 2. Responsibility overview

### Shruti - Data Engineering, Validation and Analytics

- XES conversion, data loading and preprocessing.
- Preservation of the valid case identifier `NA`.
- Timestamp ordering and event-level time feature generation.
- Data-quality validation and XES-to-CSV reconciliation.
- Patient case profiling and activity summaries.
- Transition and bottleneck analytics.
- Preparation of Power BI analytical CSV exports.
- Data dictionary and data pipeline verification.

### Madhura - Process Mining and Visual Analytics

- PM4Py event-log preparation and classification.
- Inductive Miner and Heuristics Miner workflows.
- Directly-Follows Graph (DFG) discovery and performance analysis.
- Process variant discovery and pathway analysis.
- Static process maps using NetworkX and Matplotlib.
- Interactive HTML process map.
- Streamlit dashboard development and visualization.

### Joint work

- Integration of data engineering and process mining outputs.
- Review of end-to-end project behavior and test results.
- Dashboard and analytical output review.
- Documentation, presentation preparation and viva discussion.

These are team responsibility areas, not a measured percentage split.

## 3. Current module ownership map

| Workstream | Reported lead | Current path / deliverable |
|---|---|---|
| XES conversion and loading | Shruti | `src/data/convert_xes.py`, `src/data/loader.py` |
| Cleaning and identifier preservation | Shruti | `src/data/cleaner.py` |
| Time feature generation | Shruti | `src/data/time_features.py` |
| Data validation | Shruti | `src/validation/validator.py` |
| XES/CSV reconciliation | Shruti | `src/validation/reconciliation.py` |
| Activity analytics | Shruti | `src/analysis/activity_summary.py` |
| Case profiling | Shruti | `src/analysis/case_profiler.py` |
| Transition analytics | Shruti | `src/analysis/transitions_analysis.py` |
| Bottleneck analytics | Shruti | `src/analysis/bottleneck_analysis.py` |
| Power BI data preparation | Shruti | `src/prepare_powerbi_data.py`, `data/powerbi/` |
| PM4Py event-log management | Madhura | `src/process_mining/log_manager.py` |
| Inductive Miner | Madhura | `src/process_mining/inductive_miner.py` |
| Heuristics Miner | Madhura | `src/process_mining/heuristics_miner.py` |
| DFG discovery | Madhura | `src/process_mining/dfg_miner.py` |
| Variant discovery | Madhura | `src/process_mining/variants_miner.py` |
| Process map visualizations | Madhura | `src/visualization/process_map.py` |
| Interactive process map | Madhura | `src/visualization/interactive_map.py` |
| Streamlit dashboard | Madhura | `src/dashboard/app.py` |
| Pipeline integration | Joint | `run_pipeline.py` |
| Automated tests | Joint | `tests/` |

The table records the team's responsibility allocation. It is not a claim that Git history independently verifies every row's author.

## 4. Verified project facts relevant to the work

- Raw event log: 15,214 events.
- Cases: 1,050.
- Activities: 16.
- Distinct process variants: 846.
- DFG transitions: 115.
- Consecutive within-case event transitions: 14,164.
- Event reconciliation: 100% match, with no missing or extra events in the verified reconciliation.
- Automated test suite: 31 tests passed in the latest reported run.
- Power BI exports: 10 CSV files, including 7 core star-schema tables (4 dimensions and 3 facts) and 3 additional analytical exports.
- Streamlit dashboard: `src/dashboard/app.py`, organized into 11 modules/sections as implemented in the application.

A Power BI `.pbix` report file has not been verified in the repository. The project includes Power BI CSV exports and dashboard documentation/specification; do not claim a completed `.pbix` unless one is actually created and checked.

## 5. Data hand-off and integration

1. The data pipeline converts and prepares the event log.
2. The cleaned event log is consumed by the process-mining workflow.
3. Process-mining outputs include discovered models, DFGs and process variants.
4. Analytical outputs are prepared for dashboard and Power BI consumption.
5. Validation and reconciliation results support data-quality reporting.

Important data-handling rules:

- The case identifier `NA` is a valid identifier and must remain a string.
- Empty fields must not be confused with the literal identifier `NA`.
- Repeated clinical laboratory events must not be removed solely because timestamps match.
- Missing bottleneck time measurements must not be replaced with zero.
- Timing cohorts are descriptive dataset analyses, not proof of clinical compliance or causality.

## 6. Git workflow and current repository state

The repository currently has `main` as the integrated branch. Local and remote development branches named `shruti` and `madhura` also exist.

Recent integration history includes merges of the Shruti and Madhura development branches into `main`. The inspected file-history output shows commits authored as Shruti Mali for the selected module paths. Consequently, Git author metadata alone does not establish the complete individual contribution split.

Use `main` as the current integrated project branch. Do not describe the development branches as deleted.

## 7. Viva preparation

### Shruti should be prepared to explain

- Why Pandas can interpret the literal string `NA` as a missing value.
- How `keep_default_na=False` and `na_values=[""]` preserve valid identifiers while detecting empty cells.
- Why same-timestamp laboratory events may be legitimate separate assays.
- How chronological time features and case-level summaries are produced.
- How reconciliation compares the source XES log with the processed event data.
- How activity, transition and bottleneck metrics are calculated.
- How the Power BI CSV exports are structured.

### Madhura should be prepared to explain

- How the event log is converted into a PM4Py-compatible structure.
- How Inductive Miner and Heuristics Miner differ.
- What a Petri Net, BPMN model and DFG represent.
- How process variants are identified.
- How NetworkX and Matplotlib are used for static process maps.
- How the interactive process map and Streamlit dashboard present analytical outputs.

### Claims to avoid

- Do not claim a measured 50%-50% workload split.
- Do not claim formal Petri Net soundness or deadlock-free behavior unless separately verified.
- Do not describe descriptive antibiotic timing cohorts as universal clinical compliance.
- Do not claim a Power BI `.pbix` file exists unless it is present and tested.
- Do not claim Git authorship for a member when the available commit metadata does not support it.
