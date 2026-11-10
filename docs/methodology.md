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

Sepsis is a life-threatening organ dysfunction caused by a dysregulated host response to infection. It is a major clinical emergency where **time-to-intervention directly governs survival**.

The TU/e Sepsis Cases Event Log (from an acute care hospital in the Netherlands) is a benchmark clinical dataset because:
1. **Clinical Protocol Rigor:** Clear clinical guidelines (e.g. the Surviving Sepsis Campaign) dictate that blood cultures, lactate measurement, fluid resuscitation, and intravenous antibiotics should occur rapidly within the first "Golden Hour."
2. **High Behavioral Complexity (Spaghetti Effect):** Unlike structured manufacturing lines, sepsis patients exhibit tremendous behavioral variability based on individual physiological responses, comorbidities, and acute deteriorations.
3. **Multi-Stage Transitions:** Cases span emergency admission, urgent laboratory diagnostics, inpatient bed allocation, intensive care escalations, and post-discharge disposition.

---

## 3. Process Discovery Algorithms Implemented

### A. Inductive Miner (IM)
Traditional discovery algorithms (such as the classic Alpha Miner) frequently fail on complex healthcare logs because they cannot handle short loops, silent transitions, or high behavioral variability, often producing unsound models with deadlocks.

To solve this, CareFlow implements PM4Py's **Inductive Miner** (`pm4py.discover_petri_net_inductive` and `pm4py.discover_bpmn_inductive`):
- **Core Principle:** Inductive Miner operates by recursively finding cuts in the Directly-Follows Graph that split activities into independent sub-processes using fundamental process operators:
  - **Sequence ($\rightarrow$):** Strict chronological ordering.
  - **Exclusive Choice ($\times$):** Alternative pathways (e.g. Normal Care vs ICU).
  - **Concurrency ($\wedge$):** Parallel activities (e.g. simultaneous drawing of CRP and Leucocytes blood tubes).
  - **Loop ($\circlearrowleft$):** Serial repetitions (e.g. repeated daily blood monitoring).
- **Guaranteed Soundness:** The resulting Petri Net is mathematically guaranteed to be a **Sound Workflow Net**:
  1. It contains exactly one source place (initial state) and one sink place (final state).
  2. Every transition is on a valid execution path from source to sink.
  3. No deadlock or livelock is possible; any started case can always reach proper termination.

### B. Heuristics Miner (HM)
While Inductive Miner guarantees soundness, it can introduce silent ($\tau$) transitions to account for rare behaviors. To extract the pragmatic "backbone" of clinical care, CareFlow implements the **Heuristics Miner** (`pm4py.discover_petri_net_heuristics`):
- **Dependency Measure Formulation:** Heuristics Miner filters out low-frequency noise by computing a pairwise dependency score between activities $A$ and $B$:
  $$D(A \Rightarrow B) = \frac{|A > B| - |B > A|}{|A > B| + |B > A| + 1}$$
  Where $|A > B|$ denotes the number of times activity $A$ is directly followed by activity $B$.
  - When $A \rightarrow B$ occurs frequently and $B \rightarrow A$ never occurs, $D(A \Rightarrow B) \to 1.0$ (strong causal dependency).
  - When $A$ and $B$ occur in parallel with equal frequency, $D(A \Rightarrow B) \to 0.0$ (concurrent, not sequentially dependent).
- For self-loops (e.g. repeated lab assays $A \rightarrow A$):
  $$D(A \Rightarrow A) = \frac{|A > A|}{|A > A| + 1}$$

### C. Directly-Follows Graph (DFG)
The Directly-Follows Graph is the fundamental graph structure where nodes represent the 16 clinical activities and directed edges represent immediate within-case succession:
- **Frequency DFG:** Edge weights represent absolute transition counts.
- **Performance DFG:** Edge weights represent waiting-time statistics (mean and median elapsed hours between consecutive events).
- In CareFlow, the DFG discovered exactly **115 directed edges** representing **14,164 transitions**.

---

## 4. Transition Probability Matrix Formulation

For each activity $A$ that acts as a transition source, the conditional probability that a patient moves next to activity $B$ is given by:

$$P(B \mid A) = \frac{\text{Count}(A \rightarrow B)}{\sum_{k=1}^{16} \text{Count}(A \rightarrow k)}$$

Subject to the normalization constraint:

$$\sum_{k=1}^{16} P(k \mid A) = 1.0000 \quad (\text{for all active source activities } A)$$

This formulation generates the $16 \times 16$ transition probability matrix (`outputs/tables/activity_transition_matrix.csv`), enabling precise predictive modeling of clinical transitions.

---

## 5. Process Variants & The Pareto Principle

A **process variant** (or trace variant) is a unique, ordered sequence of activities executed from case admission to discharge:

$$\text{Trace}(C_i) = \langle a_1, a_2, a_3, \dots, a_k \rangle$$

- In CareFlow, the 1,050 patient cases yielded **846 unique process variants**.
- **Clinical Implication:** High variant diversity is a natural hallmark of complex sepsis treatment. Individual patient physiology, varying infection sites, and differing severity scores require highly tailored therapeutic interventions.
- The top 10 variants cover **12.98% of all cases**, with the single most frequent pathway (`V001`) accounting for **3.33%** (35 patients).

---

## 6. Clinical Bottleneck Analysis & Governance Rules

### A. The "Golden Hour" Sepsis Bundle
The international Surviving Sepsis Campaign guidelines emphasize rapid administration of intravenous broad-spectrum antimicrobials within the first hour of triage recognition.
- **Triage-to-Antibiotics Interval:** Measured as $(t_{\text{IV Antibiotics}} - \min(t_{\text{ER Triage}}, t_{\text{ER Sepsis Triage}}))$.
- In CareFlow, across **823 eligible patients**:
  - **36.9% (304 patients)** received antibiotics within $\le 1$ hour.
  - **74.8% (616 patients)** received antibiotics within $\le 3$ hours.
  - **25.2% (207 patients)** experienced administration $> 3$ hours (delay investigation cohort).

### B. Emergency Boarding Latency
Measured from $t_{\text{ER Registration}}$ to hospital ward bed allocation ($\min(t_{\text{Admission NC}}, t_{\text{Admission IC}})$):
- Across **810 admitted patients**, median boarding time was **3.22 hours** (73.8% admitted within 4 hours), confirming swift emergency intake in the hospital.

### C. Methodological Caveat: Event-Log Span vs Continuous Hospital Stay
In process mining, measuring case duration blindly as $(t_{\text{last}} - t_{\text{first}})$ aggregates the entire electronic health record observation span.
- For patients *without* `Return ER`, the median observation duration is **3.5 days** (reflecting true acute inpatient stay).
- For patients *with* `Return ER`, the median observation duration is **55.2 days**, because the median gap between hospital discharge (`Release A`) and a subsequent emergency revisit is **47.3 days**.
- **Governance Rule:** Process mining extracts timestamp differences recorded in EHR logs. It does **not** assert medical causation, clinician negligence, or continuous hospital bed occupancy.
