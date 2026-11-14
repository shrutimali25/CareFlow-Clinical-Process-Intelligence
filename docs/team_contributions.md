# CareFlow: Team Roles, Contributions and Code Ownership

> **Project:** CareFlow - Clinical Process Intelligence
> **Team members:** Shruti Mali and Madhura
> **Repository:** CareFlow-Clinical-Process-Intelligence
> **Integrated branch:** `main`

## 1. Contribution and attribution statement

This document records the team's reported areas of responsibility and the current code structure. Responsibility allocation and Git commit authorship are different forms of evidence.

The inspected Git history for the selected data, validation, analysis, process-mining, visualization and dashboard paths shows commits authored under the name Shruti Mali. This metadata does not independently prove that every implementation task was completed by one person, nor does it establish the exact amount of work performed by each team member.

The project therefore does not assign a numerical contribution percentage. Each member should describe only the work they personally performed and can demonstrate.

## 2. Shruti - Data Engineering, Validation and Analytics

Reported areas of responsibility:

- XES conversion and event-data ingestion.
- Data loading and cleaning.
- Preservation of valid case identifier `NA`.
- Timestamp normalization and elapsed-time features.
- Automated data-quality checks.
- XES-to-CSV reconciliation.
- Patient case profiling and activity-frequency analysis.
- Transition analysis and bottleneck metrics.
- Power BI star-schema CSV preparation.

Relevant current modules:

| Module | Responsibility |
|---|---|
| `src/data/convert_xes.py` | XES conversion |
| `src/data/loader.py` | Safe data loading |
| `src/data/cleaner.py` | Data cleaning and identifier handling |
| `src/data/time_features.py` | Chronological and elapsed-time features |
| `src/validation/validator.py` | Data-quality validation |
| `src/validation/reconciliation.py` | Source-to-processed reconciliation |
| `src/analysis/activity_summary.py` | Activity counts and rework analysis |
| `src/analysis/case_profiler.py` | Patient case-level summaries |
| `src/analysis/transitions_analysis.py` | Transition analysis |
| `src/analysis/bottleneck_analysis.py` | Bottleneck timing analysis |
| `src/prepare_powerbi_data.py` | Power BI CSV generation |

## 3. Madhura - Process Mining and Visual Analytics

Reported areas of responsibility:

- PM4Py event-log structuring.
- Inductive Miner process discovery.
- Heuristics Miner process discovery.
- Directly-Follows Graph analysis.
- Process variant discovery.
- Static process maps using NetworkX and Matplotlib.
- Interactive HTML process map.
- Streamlit dashboard development and visualization.

Relevant current modules:

| Module | Responsibility |
|---|---|
| `src/process_mining/log_manager.py` | PM4Py event-log preparation |
| `src/process_mining/inductive_miner.py` | Inductive Miner workflow |
| `src/process_mining/heuristics_miner.py` | Heuristics Miner workflow |
| `src/process_mining/dfg_miner.py` | DFG discovery |
| `src/process_mining/variants_miner.py` | Process variant analysis |
| `src/process_mining/run_process_mining.py` | Process-mining execution workflow |
| `src/visualization/process_map.py` | Static process maps |
| `src/visualization/interactive_map.py` | Interactive process map |
| `src/dashboard/app.py` | Streamlit dashboard |

## 4. Shared integration and project work

The following areas involve integration or team-level review:

- Connecting the cleaned event log to process-mining modules.
- Integrating process-mining outputs with analytical datasets.
- Reviewing the end-to-end pipeline.
- Running and reviewing automated tests.
- Preparing technical documentation and presentation material.
- Preparing for project demonstration and viva.

Relevant shared entry points:

- `run_pipeline.py`
- `tests/run_all_tests.py`
- `tests/`

The latest reported test run completed with 31 passed tests. Test status should be refreshed if code changes are made after that run.

## 5. Verified project outputs

| Output | Verified information |
|---|---|
| Event log | 15,214 events |
| Patient cases | 1,050 |
| Activities | 16 |
| Process variants | 846 |
| DFG transitions | 115 |
| Consecutive event transitions | 14,164 |
| Event reconciliation | 100% match in the verified reconciliation |
| Power BI exports | 10 CSV files |
| Core star schema | 4 dimensions and 3 fact tables |
| Automated tests | 31 passed in the latest reported run |

Power BI exports include the core dimension and fact tables as well as additional analytical summaries. The repository's CSV exports and dashboard guide do not, by themselves, establish that a `.pbix` report file has been completed.

## 6. Data integrity notes

- The literal case identifier `NA` is valid and must not be interpreted as a blank value.
- The event log contains 24 events belonging to the `NA` case.
- The patient-level case table contains one row for that case.
- `Previous_Timestamp` is expected to be empty for the first event of each of the 1,050 cases.
- `Triage_to_Antibiotics_Hours` has 227 unavailable values in the current Power BI export.
- `ER_to_Admission_Hours` has 240 unavailable values in the current Power BI export.
- Missing timing values represent unavailable measurements and must not be interpreted as zero.
- Repeated clinical assays must be preserved when they represent distinct events.

## 7. Git history and code ownership transparency

The integrated project is on `main`. The repository also contains local and remote `shruti` and `madhura` development branches.

The inspected recent file-history output reports Shruti Mali as the author for the selected paths. This is useful repository metadata, but it is not a complete record of informal collaboration, reviews, discussions or work performed outside commits.

For an academic contribution statement, the team should confirm the wording with both members before submission. Do not infer a numerical contribution split from branch names or file ownership alone.

## 8. Viva guidance

Each member should be able to explain their reported modules, demonstrate the relevant outputs, and answer questions about limitations. In particular:

- Explain data reconciliation as event matching, not as a claim that every field is non-null.
- Explain that the literal `NA` case identifier is valid.
- Explain that missing bottleneck measurements are not zero-duration events.
- Treat antibiotic timing thresholds as descriptive analytical cohorts, not universal clinical conclusions.
- Do not claim formal Petri Net soundness unless a separate formal verification has been performed.
