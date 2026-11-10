# CareFlow: College Viva & Presentation Guide

> **Project:** CareFlow – Patient Journey Analysis Using Process Mining  
> **Target Audience:** College Evaluators, Project Guides, External Examiners, and Technical Recruiters  
> **Presenters:** Shruti (Member 1 - Data Engineering) & Madhura (Member 2 - Process Mining)  

---

## Presentation Structure (12 Slides)

```mermaid
flowchart LR
    S1[1. Title & Intro] --> S2[2. Problem Statement]
    S2 --> S3[3. Sepsis Dataset]
    S3 --> S4[4. Data Engineering]
    S4 --> S5[5. What is Process Mining?]
    S5 --> S6[6. Discovery Algorithms]
    S6 --> S7[7. Directly-Follows Graph]
    S7 --> S8[8. Process Variants]
    S8 --> S9[9. Bottlenecks & Timing]
    S9 --> S10[10. Power BI Dashboard]
    S10 --> S11[11. Performance & QA]
    S11 --> S12[12. Conclusion & Team]
```

---

## Slide-by-Slide Script & Talking Points

### Slide 1: Title & Executive Introduction
- **Slide Title:** CareFlow – Clinical Pathway Intelligence & Patient Journey Analysis Using Process Mining
- **Presented By:** Shruti (Data Engineering) & Madhura (Process Mining)
- **Key Talking Points (Shruti):**
  > *"Good morning, respected professors and evaluators. Today, we present CareFlow, an end-to-end data engineering and process mining project. CareFlow analyzes real-world emergency and inpatient hospital event logs to discover actual patient treatment pathways, detect clinical bottlenecks, analyze care variations, and provide visual operational intelligence for healthcare providers."*

---

### Slide 2: The Problem – Why Traditional BI Fails in Healthcare
- **Key Talking Points (Shruti):**
  > *"Hospital administrators often track metrics like 'Average Length of Stay: 5 days' or 'Total Admissions: 1,000'. However, standard aggregation dashboards act as a black box. They tell you how long a patient stayed, but cannot reveal the sequence of events that actually happened. In reality, healthcare is not linear—patients get tested, wait for beds, undergo repeated blood draws, get transferred to ICU, and sometimes return to the ER. Process mining allows us to open this black box and reconstruct the exact, step-by-step patient journey directly from timestamped electronic health records."*

---

### Slide 3: The Sepsis Dataset & Data Integrity
- **Key Talking Points (Shruti):**
  > *"We chose the TU/e Sepsis Cases Event Log from a Dutch acute care hospital. Sepsis is an urgent medical condition where timely intervention directly dictates survival. The original dataset contains exactly 15,214 events across 1,050 patient cases and 16 clinical activities.
  During our initial audit, we uncovered a critical data engineering bug common in healthcare projects: previous analyses reported only 15,189 events because patient ID 'NA' was silently dropped by Pandas as a missing NaN value, and an earlier drop-duplicates call discarded a genuine multi-tube blood test. By implementing custom data loaders with strict string typing, we restored all 24 events of patient 'NA' and achieved a 100.0% zero-defect reconciliation with the raw XES file."*

---

### Slide 4: Data Pipeline & Automated Quality Assurance
- **Key Talking Points (Shruti):**
  > *"Our data engineering pipeline executes in four modular steps: First, converting raw compressed XES into CSV. Second, cleaning timestamps to UTC and stably sorting records. Third, computing sequential step numbers and non-negative elapsed minutes. Fourth, running an automated validation framework that tests 10 data quality checks—proving zero missing values, zero negative times, and 1,050 monotonically chronological traces. We also built an automated multi-attribute reconciler to guarantee that no clinical event is ever lost."*

---

### Slide 5: What is Process Mining & How PM4Py Works?
- **Key Talking Points (Madhura):**
  > *"Now, turning to the process mining engine: Process mining is fundamentally different from traditional machine learning. Machine learning typically predicts an outcome or classifies a label. Process mining, implemented via the Python PM4Py library, discovers the underlying behavioral model of the system.
  To perform process mining, an event log requires three fundamental pillars: Case ID (who), Activity Name (what), and Timestamp (when). From these three classifiers, PM4Py builds an event log object that enables formal process discovery."*

---

### Slide 6: Process Discovery – Inductive Miner vs. Heuristics Miner
- **Key Talking Points (Madhura):**
  > *"We implemented two primary discovery algorithms:
  First, the Inductive Miner. In healthcare, classical algorithms like Alpha Miner fail because they create models with deadlocks. The Inductive Miner recursively detects sequence, choice, concurrency, and loop cuts in the graph. It discovered a Petri Net with 39 places and 50 transitions, and a BPMN model with 62 nodes, with a mathematical guarantee of soundness.
  Second, the Heuristics Miner. Because clinical care has rare edge cases, Heuristics Miner calculates a dependency measure based on transition frequencies. It filters out low-frequency noise and produced a 33-place, 74-transition Petri Net alongside a 16x16 activity dependency matrix."*

---

### Slide 7: Directly-Follows Graph (DFG) & Visual Process Maps
- **Key Talking Points (Madhura):**
  > *"The Directly-Follows Graph is the core operational map of the hospital. In CareFlow, we discovered 115 unique directed transitions across 14,164 event connections.
  Importantly, many process mining libraries fail on standard student laptops because they require external Graphviz system binaries. We engineered our visualizer using pure Python NetworkX and Matplotlib to produce publication-quality 300 DPI process maps with semantic clinical color-coding (Intake, Diagnostics, Treatments, Inpatient, Disposition). We also developed a standalone interactive HTML5 canvas map where users can drag nodes, click to inspect in/outflow volumes, and dynamically slide an edge-frequency filter."*

---

### Slide 8: Process Variants & Clinical Variability
- **Key Talking Points (Madhura):**
  > *"A process variant is a unique, start-to-finish sequence of activities. Across 1,050 patients, CareFlow discovered 846 unique process variants!
  This enormous diversity illustrates the reality of clinical care—sepsis care is individualized. The single most common pathway, Variant V001 (Intake -> Triage -> Sepsis Triage -> IV Liquid -> IV Antibiotics -> Normal Care -> Release A), accounts for 35 patients (3.33%). The top 10 variants cover 12.98% of all cases. Our variant Pareto analysis proves that hospital administrators cannot impose a single rigid pathway without understanding clinical branching."*

---

### Slide 9: Clinical Bottlenecks & Governance Rules
- **Key Talking Points (Madhura & Shruti):**
  > *"We investigated clinical timing against international Surviving Sepsis Campaign guidelines:
  1. Triage-to-Antibiotics: For the 823 patients receiving antibiotics, median time from triage was 1.73 hours. 36.9% met the strict 'Golden Hour' guideline (<= 1h), and 74.8% met the 3-hour bundle target. 207 cases experienced delays over 3 hours.
  2. ER Boarding: Median time from ER intake to hospital ward bed was 3.22 hours, with 73.8% admitted in under 4 hours.
  3. Critical Governance Clarification: 294 patients recorded a 'Return ER' event. The median gap between hospital release and Return ER was 47.3 days. In healthcare process mining, measuring case duration blindly as last timestamp minus first timestamp aggregates out-of-hospital periods (median 55 days), whereas continuous inpatient stay has a median of 3.5 days. Process mining reveals operational time intervals—it does not claim medical fault or causation."*

---

### Slide 10: Power BI Star-Schema Dashboard
- **Key Talking Points (Shruti):**
  > *"To empower hospital leadership, we transformed our processed data into an enterprise Star Schema in data/powerbi/. It consists of two Fact tables (Fact_Event_Log with 15,214 rows and Fact_Transitions with 115 rows) connected via 1-to-many relationships to Dimension tables (Dim_Patient_Cases, Dim_Activities, Dim_Variants, Fact_Bottlenecks, and Dim_Data_Quality).
  We designed a 5-page dashboard: Page 1 for Overall Patient Journey, Page 2 for Activity Workload & Rework, Page 3 for Process Flow & Variants, Page 4 for Waiting Times & Bottlenecks, and Page 5 for Data Quality Audit, powered by 25+ DAX measures."*

---

### Slide 11: System Performance & Automated Quality Assurance
- **Key Talking Points (Shruti):**
  > *"CareFlow was built with engineering rigor:
  - Total pipeline execution time: Just 17.2 seconds from raw XES to complete Power BI models.
  - Peak memory footprint: Only 33.7 MB RAM, making it 100% lightweight and compatible with standard 8 GB RAM laptops.
  - Test Suite: 31 automated unit, integration, and end-to-end tests spanning data engineering, PM4Py discovery, analytics, and Power BI schema integrity. All 31 tests pass with 100% success rate."*

---

### Slide 12: Conclusion & Team Contributions
- **Key Talking Points (Shruti & Madhura):**
  > *"In conclusion, CareFlow delivers an end-to-end, scientifically grounded, reproducible process mining platform.
  - Shruti led Data Engineering: Raw ingestion, fixing Case 'NA', repeat assay preservation, chronological time features, quality validation, reconciliation, and Power BI datasets.
  - Madhura led Process Mining: PM4Py setup, Inductive & Heuristics modeling, DFG mining, 846 variants discovery, NetworkX visualizations, interactive HTML map, and bottleneck analysis.
  Thank you, and we welcome your questions!"*
