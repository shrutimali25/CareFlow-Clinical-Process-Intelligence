# CareFlow: Data Dictionary & Attribute Catalog

> **Dataset:** Sepsis Cases Event Log (TU/e BPI Challenge / Eindhoven Hospital Sepsis Cohort)  
> **Total Events:** 15,214  
> **Total Cases:** 1,050  
> **Unique Activities:** 16  
> **Primary Authors:** Shruti (Member 1 - Data Engineering) & Madhura (Member 2 - Process Analytics)  

---

## 1. Core Event Log Attributes (`sepsis_with_times.csv`)

| Column Name | Data Type | Key Type | Nullable | Description & Clinical Meaning | Example Values |
| :--- | :---: | :---: | :---: | :--- | :--- |
| **`case:concept:name`** | String | Case ID | No | Pseudonymized unique patient encounter identifier. Note: Valid IDs include `"NA"`. | `"A"`, `"NA"`, `"ES"`, `"ZM"` |
| **`concept:name`** | String | Activity | No | Name of the recorded hospital activity or clinical intervention. | `"ER Registration"`, `"CRP"` |
| **`time:timestamp`** | Datetime (UTC) | Timestamp | No | Standardized ISO-8601 UTC timestamp of activity execution. | `2014-10-22 09:15:41+00:00` |
| **`event_sequence_nr`** | Integer | Order | No | Chronological 1-indexed sequence number of the event within the case. | `1`, `2`, `3`, ... |
| **`previous_activity`** | String | Predecessor | Yes | Name of the preceding activity in the patient journey (`NaN` for first event). | `"ER Registration"`, `"ER Triage"` |
| **`previous_event_time`** | Datetime (UTC) | Timestamp | Yes | Timestamp of the preceding event in the patient trace. | `2014-10-22 09:15:41+00:00` |
| **`elapsed_minutes`** | Float | Metric | Yes | Elapsed time in minutes between previous activity and current activity. | `11.3167`, `0.0000`, `149.7833` |
| **`Age`** | Integer | Clinical | Yes | Patient age in years at the time of hospital admission. | `65`, `85`, `45` |
| **`Diagnose`** | String | Clinical | Yes | Primary ICD/hospital diagnostic classification code (`NaN` if unrecorded). | `"C"`, `"B"`, `"E"`, `"H"` |
| **`SIRSCriteria2OrMore`** | Boolean | Clinical | Yes | Flag indicating whether patient met $\ge 2$ Systemic Inflammatory Response Syndrome criteria. | `True`, `False` |
| **`InfectionSuspected`** | Boolean | Clinical | Yes | Flag indicating whether attending physicians suspected clinical infection. | `True`, `False` |
| **`DisfuncOrg`** | Boolean | Clinical | Yes | Flag indicating whether clinical organ dysfunction was documented. | `True`, `False` |
| **`Hypotensie`** | Boolean | Clinical | Yes | Clinical hypotension recorded (systolic BP $< 90\text{ mmHg}$). | `True`, `False` |
| **`Hypoxie`** | Boolean | Clinical | Yes | Clinical hypoxia documented (arterial oxygen saturation $< 90\%$). | `True`, `False` |
| **`Oligurie`** | Boolean | Clinical | Yes | Clinical oliguria documented (acute low urine output $< 0.5\text{ mL/kg/h}$). | `True`, `False` |
| **`Infusion`** | Boolean | Clinical | Yes | Intravenous fluid infusion administered. | `True`, `False` |
| **`DiagnosticBlood`** | Boolean | Clinical | Yes | Blood culture or basic blood laboratory assays requested. | `True`, `False` |
| **`DiagnosticArtAstrup`** | Boolean | Clinical | Yes | Arterial blood gas (Astrup) laboratory diagnostic ordered. | `True`, `False` |
| **`DiagnosticECG`** | Boolean | Clinical | Yes | Electrocardiogram performed. | `True`, `False` |
| **`DiagnosticXthorax`** | Boolean | Clinical | Yes | Chest X-ray (radiography) performed. | `True`, `False` |
| **`DiagnosticUrinaryCulture`**| Boolean | Clinical | Yes | Urine culture microbiology laboratory assay performed. | `True`, `False` |
| **`DiagnosticUrinarySediment`**| Boolean | Clinical | Yes | Microscopic urinary sediment analysis performed. | `True`, `False` |
| **`DiagnosticLacticAcid`** | Boolean | Clinical | Yes | Blood serum lactate laboratory diagnostic ordered. | `True`, `False` |
| **`DiagnosticSputum`** | Boolean | Clinical | Yes | Sputum microbiology culture performed. | `True`, `False` |
| **`DiagnosticLiquor`** | Boolean | Clinical | Yes | Cerebrospinal fluid (lumbar puncture) microbiology performed. | `True`, `False` |
| **`DiagnosticOther`** | Boolean | Clinical | Yes | Other diagnostic assays performed. | `True`, `False` |
| **`DiagnosticIC`** | Boolean | Clinical | Yes | Intensive care consultation diagnostic recorded. | `True`, `False` |
| **`SIRSCritHeartRate`** | Boolean | Clinical | Yes | Heart rate $> 90\text{ bpm}$ (SIRS heart rate criterion). | `True`, `False` |
| **`SIRSCritLeucos`** | Boolean | Clinical | Yes | White blood cell count $> 12,000$ or $< 4,000/\mu\text{L}$ (SIRS leucocyte criterion). | `True`, `False` |
| **`SIRSCritTachypnea`** | Boolean | Clinical | Yes | Respiratory rate $> 20\text{ breaths/min}$ (SIRS respiratory criterion). | `True`, `False` |
| **`SIRSCritTemperature`** | Boolean | Clinical | Yes | Core body temperature $> 38.3^\circ\text{C}$ or $< 36.0^\circ\text{C}$ (SIRS temperature criterion). | `True`, `False` |
| **`CRP`** | Float | Clinical | Yes | C-reactive protein laboratory test value (mg/L). | `15.0`, `120.0`, `250.0` |
| **`Leucocytes`** | Float | Clinical | Yes | Total white blood cell count ($\times 10^9/\text{L}$). | `11.5`, `18.2`, `4.1` |
| **`LacticAcid`** | Float | Clinical | Yes | Serum lactic acid (lactate) value (mmol/L). | `1.2`, `2.8`, `4.5` |
| **`lifecycle:transition`** | String | Process | No | PM4Py standard lifecycle phase (all events recorded as `"complete"`). | `"complete"` |
| **`org:group`** | String | Resource | Yes | Organizational unit or department executing the activity. | `"Group A"`, `"Group B"` |

---

## 2. Activity Master Catalog (16 Activities)

| Activity Name | Clinical Stage | Occurrences | Unique Cases | Patient Reach | Rework Rate | Clinical Purpose |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **ER Registration** | 1. Intake | 1,050 | 1,050 | 100.0% | 0.0% | Formal patient arrival and electronic health record intake in emergency department |
| **ER Triage** | 1. Intake | 1,053 | 1,050 | 100.0% | 0.3% | Initial clinical nurse triage and Manchester triage score assignment |
| **ER Sepsis Triage** | 1. Intake | 1,049 | 1,049 | 99.9% | 0.0% | Specialized sepsis screening protocol evaluating systemic inflammatory criteria |
| **CRP** | 2. Diagnostics | 3,262 | 1,007 | 95.9% | 68.7% | C-Reactive Protein inflammatory biomarker tracking bacterial infection severity |
| **Leucocytes** | 2. Diagnostics | 3,383 | 1,012 | 96.4% | 66.9% | White blood cell count measuring immune system infection response |
| **LacticAcid** | 2. Diagnostics | 1,466 | 860 | 81.9% | 20.0% | Serum lactate measuring cellular hypoperfusion and septic shock severity |
| **IV Liquid** | 3. Treatment | 753 | 753 | 71.7% | 0.0% | Rapid crystalloid intravenous fluid resuscitation for septic hypoperfusion |
| **IV Antibiotics** | 3. Treatment | 823 | 823 | 78.4% | 0.0% | Broad-spectrum intravenous antimicrobial administration |
| **Admission NC** | 4. Inpatient | 1,182 | 800 | 76.2% | 39.1% | Admission or bed transfer to Normal Care inpatient ward |
| **Admission IC** | 4. Inpatient | 117 | 110 | 10.5% | 6.4% | Admission or urgent transfer to Intensive Care Unit (ICU) |
| **Release A** | 5. Disposition | 671 | 671 | 63.9% | 0.0% | Routine discharge from hospital to patient's home |
| **Release B** | 5. Disposition | 56 | 56 | 5.3% | 0.0% | Discharge to nursing home or external sub-acute healthcare facility |
| **Release C** | 5. Disposition | 25 | 25 | 2.4% | 0.0% | Transfer to another specialized regional hospital |
| **Release D** | 5. Disposition | 24 | 24 | 2.3% | 0.0% | Transfer to outpatient or specialized rehabilitation care |
| **Release E** | 5. Disposition | 6 | 6 | 0.6% | 0.0% | Deceased / in-hospital patient mortality |
| **Return ER** | 5. Disposition | 294 | 294 | 28.0% | 0.0% | Unplanned readmission or subsequent return encounter to the emergency room |

---

## 3. Power BI Star-Schema Tables (`data/powerbi/`)

### `dim_patient_cases.csv` (1,050 rows)
- `Case_ID` (PK): String. Unique patient case identifier.
- `Total_Events`: Integer. Count of events recorded in the trace.
- `First_Event_Time`: Datetime string (`YYYY-MM-DD HH:MM:SS`).
- `Last_Event_Time`: Datetime string (`YYYY-MM-DD HH:MM:SS`).
- `Observation_Duration_Hours`: Float. Total span between first and last timestamp.
- `Observation_Duration_Days`: Float. Total observation days.
- `Duration_Cohort`: String. Categorical grouping (`< 24 Hours`, `1 - 7 Days`, `1 - 4 Weeks`, `> 4 Weeks`).
- `Entry_Activity`: String. Initial recorded activity.
- `Exit_Activity`: String. Final recorded activity.
- `Age`: Integer. Patient age in years.
- `Age_Cohort`: String. Categorical grouping (`Under 45`, `45 - 64`, `65 - 79`, `80 and Over`).
- `Diagnose`: String. Diagnostic code or `"Unrecorded"`.
- `SIRSCriteria2OrMore`: Boolean. SIRS criteria met.
- `InfectionSuspected`: Boolean. Infection suspected.
- `Admitted_Normal_Care`: Boolean. Inpatient normal care admission.
- `Admitted_Intensive_Care`: Boolean. ICU admission.
- `Received_Antibiotics`: Boolean. IV antibiotics administered.
- `Received_IV_Liquid`: Boolean. IV fluids administered.
- `Had_Return_ER`: Boolean. Patient experienced a subsequent Return ER event.
- `Variant_ID` (FK): String. Foreign key to `dim_variants.csv` (`"V001"` to `"V846"`).

### `fact_transitions.csv` (115 rows)
- `Transition_Key` (PK): String (`"T001"` to `"T115"`).
- `Source_Activity` (FK): String. Predecessor activity.
- `Target_Activity`: String. Successor activity.
- `Transition_Name`: String (`"Source -> Target"`).
- `Transition_Count`: Integer. Occurrences of this transition.
- `Transition_Probability`: Float ($0.0$ to $1.0$). $P(\text{Target} \mid \text{Source})$.
- `Average_Minutes`: Float. Mean elapsed minutes.
- `Median_Minutes`: Float. Median elapsed minutes.
- `Average_Hours`: Float. Mean elapsed hours.
- `Median_Hours`: Float. Median elapsed hours.
- `Transition_Percentage`: Float. Transition probability expressed as a percentage.
- `Std_Minutes`: Float. Standard deviation of transition elapsed time in minutes.
- `IQR_Minutes`: Float. Interquartile range of transition elapsed time in minutes.
- `Min_Minutes`: Float. Minimum observed elapsed time in minutes.
- `Max_Minutes`: Float. Maximum observed elapsed time in minutes.
- `Latency_Category`: String. Descriptive elapsed-time band assigned to the transition.

### `activity_frequency.csv` (16 rows)
- `concept:name`: String. Activity name.
- `total_occurrences`: Integer. Total recorded occurrences of the activity.
- `unique_cases`: Integer. Number of distinct cases containing the activity.

### `activity_time_differences.csv` (115 rows)
- `previous_activity`: String. Source activity in the observed transition.
- `concept:name`: String. Target activity in the observed transition.
- `total_transitions`: Integer. Number of observed source-to-target transitions.
- `average_minutes`: Float. Mean elapsed time for the transition, in minutes.
- `median_minutes`: Float. Median elapsed time for the transition, in minutes.

### `dim_activities.csv` (16 rows)
- `Activity` (PK): String. Unique activity name.
- `Clinical_Stage`: String. Grouped stage label used for analysis.
- `Total_Occurrences`: Integer. Total event count for the activity.
- `Unique_Cases`: Integer. Number of distinct cases containing the activity.
- `Case_Reach_Pct`: Float. Percentage of all cases containing the activity.
- `Repeated_Cases_Count`: Integer. Number of cases with repeated occurrences of the activity.
- `Rework_Rate_Pct`: Float. Percentage of cases containing the activity that repeat it.
- `Max_Repetitions_In_Single_Case`: Integer. Maximum occurrences in one case.
- `Mean_Occurrences_Per_Case`: Float. Mean occurrences per case containing the activity.

### `dim_data_quality.csv` (10 rows)
- `Check_ID` (PK): String. Identifier for a data-quality check.
- `Validation_Check`: String. Name or description of the validation performed.
- `Result`: String. Recorded validation result.
- `Status`: String. Outcome/status label for the check.

### `dim_variants.csv` (846 rows)
- `variant_id` (PK): String. Identifier for a distinct recorded activity sequence.
- `case_frequency`: Integer. Number of cases following the variant.
- `case_coverage_pct`: Float. Percentage of all cases represented by the variant.
- `cumulative_coverage_pct`: Float. Cumulative case coverage through the ranked variant.
- `pathway_length`: Integer. Number of activities in the recorded sequence.
- `entry_activity`: String. First activity in the variant.
- `exit_activity`: String. Last activity in the variant.
- `pathway_signature`: String. Encoded ordered activity sequence.

### `fact_bottlenecks.csv` (1,050 rows)
- `Case_ID` (PK/FK): String. Case identifier; corresponds to `dim_patient_cases.Case_ID`.
- `Triage_to_Antibiotics_Hours`: Nullable numeric value stored in the CSV as text where blank. Elapsed hours from triage to IV antibiotics when calculable.
- `Antibiotics_Compliance_Cohort`: String. Descriptive cohort for the observed triage-to-antibiotics interval.
- `ER_to_Admission_Hours`: Nullable numeric value stored in the CSV as text where blank. Elapsed hours from ER entry to admission when calculable.
- `Admission_Latency_Cohort`: String. Descriptive cohort for the observed ER-to-admission interval.

### `fact_event_log.csv` (15,214 rows)
- `Event_Key` (PK): Integer. Unique event-row identifier.
- `Case_ID` (FK): String. Case identifier corresponding to `dim_patient_cases.Case_ID`.
- `Activity` (FK): String. Recorded activity corresponding to `dim_activities.Activity`.
- `Timestamp`: Datetime string. Timestamp of the event.
- `Date`: Date string. Calendar date derived from the event timestamp.
- `Event_Sequence_Nr`: Integer. Chronological event position within the case.
- `Previous_Activity`: String. Previous activity in the case sequence, where represented.
- `Previous_Timestamp`: Nullable datetime string. Timestamp of the previous event; blank for the first event in each case (1,050 rows).
- `Elapsed_Minutes`: Float. Elapsed time in minutes from the previous event, as represented in the exported table.
- `Elapsed_Hours`: Float. Elapsed time in hours from the previous event, as represented in the exported table.
- `Is_First_Event`: Boolean. Indicates the first event in the case.
- `Is_Last_Event`: Boolean. Indicates the last event in the case.

### `patient_case_summary.csv` (1,050 rows)
- `case:concept:name` (PK): String. Case identifier.
- `total_events`: Integer. Number of recorded events in the case.
- `first_event_time`: Datetime string. First recorded event timestamp.
- `last_event_time`: Datetime string. Last recorded event timestamp.
- `treatment_duration_hours`: Float. Difference between the last and first recorded event timestamps, in hours.

---

## 4. Data Interpretation & Nullability Notes

- In the event-level `sepsis_with_times.csv`, `Age` is nullable: it is populated on only 1,050 of 15,214 event rows and is blank on 14,164 rows. This reflects the event-log row representation; the case-level Power BI dimension contains an age value or its exported cohort representation.
- In `fact_event_log.csv`, `Previous_Timestamp` is blank for 1,050 first events, where no preceding event exists.
- In `fact_bottlenecks.csv`, `Triage_to_Antibiotics_Hours` is blank for 227 cases and `ER_to_Admission_Hours` is blank for 240 cases in the inspected export. These fields are therefore nullable; a blank must not be interpreted as zero hours.
- The exported CSV data types describe how values are serialized in these files. Some nullable numeric fields (notably the two bottleneck hour fields) are inferred as strings by pandas because blank cells are present; their semantic values are numeric when populated.
- Percentages and time bands are descriptive summaries of this event log, not independently validated clinical compliance or causal conclusions.
