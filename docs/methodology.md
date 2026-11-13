# CareFlow: Process Mining Methodology & Algorithmic Foundations

> **Authors:** Shruti (Member 1 - Data Engineering) & Madhura (Member 2 - Process Mining Specialist)  
> **Project:** CareFlow – Patient Journey Analysis Using Process Mining  
> **Repository:** `D:\Projects\CareFlow-Clinical-Process-Intelligence`  

---

## 1. What is Process Mining?

Process mining is a specialized discipline situated at the intersection of **data science** and **operations management**. Unlike traditional business intelligence dashboards—which display aggregated snapshots such as average length of stay or overall admissions—process mining discovers, monitors, and improves real processes by extracting empirical event traces directly from timestamped transaction logs stored in enterprise information systems.

In healthcare systems, clinical pathways represent the sequential trajectory of diagnostic, therapeutic, and nursing procedures administered to a patient. Process mining bridges the gap between **prescribed clinical guidelines** (how doctors *intend* care to proceed) and **actual care delivery** (how patients *actually* move through the hospital).

---

## 2. Why the Sepsis Dataset?

Sepsis is a life-threatening organ dysfunction caused by a dysregulated host response to infection. It is a major clinical emergency where timely recognition, assessment, and appropriate treatment are important.

The TU/e Sepsis Cases Event Log (from an acute care hospital in the Netherlands) is a benchmark clinical dataset because:
1. **Clinical Protocol Context:** Current sepsis antibiotic timing recommendations depend on infection likelihood and shock status. See the clinical timing analysis in Section 6; a universal one-hour rule should not be applied to every suspected sepsis case.
2. **High Behavioral Complexity (Spaghetti Effect):** Unlike highly standardized processes, the recorded sepsis event log exhibits substantial variation in patient activity sequences. The event log alone does not establish the clinical or operational causes of this variation.
3. **Multi-Stage Transitions:** Cases span emergency admission, urgent laboratory diagnostics, inpatient bed allocation, intensive care escalations, and post-discharge disposition.

---

## 3. Process Discovery Algorithms Implemented

### A. Inductive Miner (IM)
Traditional discovery algorithms (such as the classic Alpha Miner) frequently fail on complex healthcare logs because they cannot handle short loops, silent transitions, or high behavioral variability, often producing unsound models with deadlocks.

To solve this, CareFlow implements PM4Py's **Inductive Miner** (`pm4py.discover_petri_net_inductive` and `pm4py.discover_bpmn_inductive`):
- **Core Principle:** Inductive Miner operates by recursively finding cuts in the Directly-Follows Graph that split activities into independent sub-processes using fundamental process operators:
  - **Sequence ($\rightarrow$):** Strict chronological ordering.
  - **Exclusive Choice ($\times$):** Alternative pathways (e.g. Normal Care vs ICU).
  - **Concurrency ($\wedge$):** Activity patterns that occur in different orders across traces. This is a discovered control-flow relation, not proof of simultaneous clinical execution.
  - **Loop ($\circlearrowleft$):** Serial repetitions (e.g. repeated daily blood monitoring).
- **Model output and validation:** CareFlow exports the Petri Net and BPMN artifacts discovered by PM4Py. Automated tests verify that these files exist and are non-empty. Formal workflow-net soundness, deadlock-freedom, livelock-freedom, and trace fitness have not been independently validated.

### B. Heuristics Miner (HM)
The Heuristics Miner provides a complementary, noise-tolerant discovery approach. CareFlow calls PM4Py's **Heuristics Miner** (`pm4py.discover_petri_net_heuristics`) with `dependency_threshold=0.5` to discover the model.
- **Custom dependency matrix:** Separately from PM4Py model discovery, CareFlow calculates an analytical dependency matrix from directly-following activity counts. Its pairwise score between activities $A$ and $B$ is:
  $$D(A \Rightarrow B) = \frac{|A > B| - |B > A|}{|A > B| + |B > A| + 1}$$

  The `dependency_threshold=0.5` parameter is passed to PM4Py's Heuristics Petri Net discovery call. It is not applied to this separately calculated dependency matrix.
  Where $|A > B|$ denotes the number of times activity $A$ is directly followed by activity $B$.
  - When $A \rightarrow B$ occurs frequently and $B \rightarrow A$ never occurs, $D(A \Rightarrow B) \to 1.0$ (strong directional dependency signal).
  - When the observed counts for $A \rightarrow B$ and $B \rightarrow A$ are equal, the score is $0.0$ (no directional preference in this measure). This alone does not establish concurrency.
- For self-loops (e.g. repeated lab assays $A \rightarrow A$):
  $$D(A \Rightarrow A) = \frac{|A > A|}{|A > A| + 1}$$

### C. Directly-Follows Graph (DFG)
The Directly-Follows Graph is the fundamental graph structure where nodes represent the 16 clinical activities and directed edges represent immediate within-case succession:
- **Frequency DFG:** Edge weights represent absolute transition counts.
- **Performance DFG:** Edge weights represent waiting-time statistics (mean and median elapsed hours between consecutive events).
- In CareFlow, the DFG contains **115 distinct directed edges** representing **14,164 consecutive within-case event pairs** (the sum of edge frequencies).

---

## 4. Transition Probability Matrix Formulation

For each activity $A$ that acts as a transition source, the conditional probability that a patient moves next to activity $B$ is given by:

$$P(B \mid A) = \frac{\text{Count}(A \rightarrow B)}{\sum_{k=1}^{16} \text{Count}(A \rightarrow k)}$$

Subject to the normalization constraint:

$$\sum_{k=1}^{16} P(k \mid A) = 1.0000 \quad (\text{for all active source activities } A)$$

This formulation generates the $16 \times 16$ transition probability matrix (`outputs/tables/activity_transition_matrix.csv`), supporting descriptive analysis of observed next-activity patterns. Predictive performance has not been established and would require a separately evaluated predictive model.

---

## 5. Process Variants & Pathway Diversity

A **process variant** (or trace variant) is a unique, ordered sequence of recorded activities for a patient case across the available event-log observation period:

$$\text{Trace}(C_i) = \langle a_1, a_2, a_3, \dots, a_k \rangle$$

- In CareFlow, the 1,050 patient cases yielded **846 unique process variants**.
- **Descriptive interpretation:** The 846 variants demonstrate substantial pathway diversity in this event log. The dataset does not establish whether variation is attributable to patient physiology, infection site, severity, or operational factors.
- The top 10 variants cover **12.95% of all cases**, with the single most frequent pathway (`V001`) accounting for **3.33%** (35 patients).

---

## 6. Clinical Bottleneck Analysis & Governance Rules

### A. Observed Triage-to-Antibiotics Timing (Exploratory Analysis)

The 2026 Surviving Sepsis Campaign adult guidelines distinguish antibiotic timing by sepsis likelihood and shock status. They recommend immediate antimicrobial therapy, ideally within one hour, for possible, probable, or definite septic shock and for probable or definite sepsis without shock. For possible sepsis without shock, they suggest rapid investigation and antimicrobial therapy within three hours if concern for infection persists. See the [official 2026 Surviving Sepsis Campaign guidelines](https://www.sccm.org/clinical-resources/guidelines/guidelines/surviving-sepsis-campaign-international-guidelines-for-management-of-sepsis-and-septic-shock-2026).

CareFlow's calculation is an exploratory event-log timing analysis, not a direct guideline-compliance assessment. It identifies cases with both triage and antibiotic timestamps, uses the earliest recorded `ER Triage` or `ER Sepsis Triage` time and the first `IV Antibiotics` time, and excludes negative intervals. The analysis does not stratify patients by shock status or certainty of sepsis diagnosis, and it does not measure completion of the full sepsis bundle.

- **Triage-to-Antibiotics Interval:** First recorded `IV Antibiotics` timestamp minus the earliest recorded `ER Triage` or `ER Sepsis Triage` timestamp.
- In the **823 eligible cases**:
  - **36.9% (304 cases)** had a recorded interval of $\le 1$ hour.
  - **74.8% (616 cases)** had a recorded interval of $\le 3$ hours.
  - **25.2% (207 cases)** had a recorded interval of $> 3$ hours.
  - Median recorded interval: **1.73 hours (103.8 minutes)**.
- These percentages describe observed timing bands; they must not be presented as severity-adjusted clinical guideline compliance.

### B. Emergency Boarding Latency
Measured from $t_{\text{ER Registration}}$ to hospital ward bed allocation ($\min(t_{\text{Admission NC}}, t_{\text{Admission IC}})$):
- Across **810 admitted patients**, median boarding time was **3.22 hours** (73.8% admitted within 4 hours), describing the observed registration-to-first-admission interval; this median alone does not establish whether intake was swift or clinically appropriate.

### C. Methodological Caveat: Event-Log Span vs Continuous Hospital Stay
In process mining, measuring case duration blindly as $(t_{\text{last}} - t_{\text{first}})$ aggregates the entire electronic health record observation span.
- For patients *without* `Return ER`, the median observation duration is **3.5 days** (recorded event-log span; not independently verified as continuous inpatient occupancy).
- For patients *with* `Return ER`, the median observation duration is **55.2 days**, because the median gap between hospital discharge (`Release A`) and a subsequent emergency revisit is **47.3 days**.
- **Governance Rule:** Process mining extracts timestamp differences recorded in EHR logs. It does **not** assert medical causation, clinician negligence, or continuous hospital bed occupancy.
