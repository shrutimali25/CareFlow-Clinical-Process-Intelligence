"""
Power BI Data Preparation & Star-Schema Generation Module
Exports production-grade, validated Star-Schema CSV datasets for Power BI dashboard.
Author: Shruti (Member 1) & Madhura (Member 2)
"""

from pathlib import Path
from typing import Dict, Any, Union
import sys
import pandas as pd
import numpy as np

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.data.loader import load_event_log, CASE_COL, ACTIVITY_COL, TIMESTAMP_COL


def prepare_powerbi_datasets(
    processed_dir: Union[str, Path],
    tables_dir: Union[str, Path],
    reports_dir: Union[str, Path],
    powerbi_dir: Union[str, Path]
) -> Dict[str, int]:
    """
    Transforms and structures processed event data into a complete Star Schema for Power BI.
    """
    proc_path = Path(processed_dir)
    tbl_path = Path(tables_dir)
    rep_path = Path(reports_dir)
    pbi_path = Path(powerbi_dir)
    pbi_path.mkdir(parents=True, exist_ok=True)

    print("[Power BI Prep] Ingesting verified processed datasets...")
    df_events = load_event_log(proc_path / "sepsis_with_times.csv", parse_timestamps=True)
    sorted_df = df_events.sort_values(by=[CASE_COL, TIMESTAMP_COL], kind="stable").reset_index(drop=True)

    # =========================================================================
    # 1. FACT_EVENT_LOG (15,214 rows)
    # =========================================================================
    print("  - Generating fact_event_log.csv...")
    fact_events = pd.DataFrame({
        "Event_Key": np.arange(1, len(sorted_df) + 1),
        "Case_ID": sorted_df[CASE_COL],
        "Activity": sorted_df[ACTIVITY_COL],
        "Timestamp": sorted_df[TIMESTAMP_COL].dt.strftime("%Y-%m-%d %H:%M:%S"),
        "Date": sorted_df[TIMESTAMP_COL].dt.strftime("%Y-%m-%d"),
        "Event_Sequence_Nr": sorted_df["event_sequence_nr"],
        "Previous_Activity": sorted_df["previous_activity"].fillna("None (Start)"),
        "Previous_Timestamp": pd.to_datetime(sorted_df["previous_event_time"]).dt.strftime("%Y-%m-%d %H:%M:%S").fillna(""),
        "Elapsed_Minutes": sorted_df["elapsed_minutes"].fillna(0.0).round(2),
        "Elapsed_Hours": (sorted_df["elapsed_minutes"].fillna(0.0) / 60.0).round(2),
        "Is_First_Event": sorted_df["previous_event_time"].isna(),
        "Is_Last_Event": sorted_df.groupby(CASE_COL).cumcount(ascending=False) == 0
    })
    fact_events.to_csv(pbi_path / "fact_event_log.csv", index=False)

    # =========================================================================
    # 2. DIM_VARIANTS (846 rows)
    # =========================================================================
    print("  - Generating dim_variants.csv...")
    variants_df = pd.read_csv(tbl_path / "process_variants_summary.csv")
    variants_df.to_csv(pbi_path / "dim_variants.csv", index=False)
    sig_to_var = dict(zip(variants_df["pathway_signature"], variants_df["variant_id"]))

    # =========================================================================
    # 3. DIM_PATIENT_CASES (1,050 rows)
    # =========================================================================
    print("  - Generating dim_patient_cases.csv...")
    case_profiles = pd.read_csv(tbl_path / "patient_case_profiles.csv", keep_default_na=False, na_values=[""])

    # Map trace variant
    case_sigs = sorted_df.groupby(CASE_COL)[ACTIVITY_COL].apply(lambda acts: " -> ".join(acts))
    case_profiles["Variant_ID"] = case_profiles[CASE_COL].map(case_sigs.map(sig_to_var))

    # Age Group cohort
    def categorize_age(age):
        if pd.isna(age):
            return "Unknown"
        if age < 45:
            return "1. Under 45"
        if age < 65:
            return "2. 45 - 64"
        if age < 80:
            return "3. 65 - 79"
        return "4. 80 and Over"

    case_profiles["Age_Cohort"] = case_profiles["Age"].apply(categorize_age)

    # Duration Cohort
    def categorize_duration(hours):
        if hours < 24:
            return "1. < 24 Hours"
        if hours <= 168:
            return "2. 1 - 7 Days"
        if hours <= 672:
            return "3. 1 - 4 Weeks"
        return "4. > 4 Weeks (Includes Return ER)"

    case_profiles["Duration_Cohort"] = case_profiles["treatment_duration_hours"].apply(categorize_duration)

    dim_cases = pd.DataFrame({
        "Case_ID": case_profiles[CASE_COL],
        "Total_Events": case_profiles["total_events"],
        "First_Event_Time": pd.to_datetime(case_profiles["first_event_time"]).dt.strftime("%Y-%m-%d %H:%M:%S"),
        "Last_Event_Time": pd.to_datetime(case_profiles["last_event_time"]).dt.strftime("%Y-%m-%d %H:%M:%S"),
        "Observation_Duration_Hours": case_profiles["treatment_duration_hours"],
        "Observation_Duration_Days": case_profiles["treatment_duration_days"],
        "Duration_Cohort": case_profiles["Duration_Cohort"],
        "Entry_Activity": case_profiles["entry_activity"],
        "Exit_Activity": case_profiles["exit_activity"],
        "Age": case_profiles["Age"],
        "Age_Cohort": case_profiles["Age_Cohort"],
        "Diagnose": case_profiles["Diagnose"],
        "SIRSCriteria2OrMore": case_profiles["SIRSCriteria2OrMore"],
        "InfectionSuspected": case_profiles["InfectionSuspected"],
        "Admitted_Normal_Care": case_profiles["admitted_normal_care"],
        "Admitted_Intensive_Care": case_profiles["admitted_intensive_care"],
        "Received_Antibiotics": case_profiles["received_antibiotics"],
        "Received_IV_Liquid": case_profiles["received_iv_liquid"],
        "Had_Return_ER": case_profiles["had_return_er"],
        "Variant_ID": case_profiles["Variant_ID"]
    })
    dim_cases.to_csv(pbi_path / "dim_patient_cases.csv", index=False)

    # Backward compatible summary file
    compat_case = case_profiles[[CASE_COL, "total_events", "first_event_time", "last_event_time", "treatment_duration_hours"]].copy()
    compat_case.to_csv(pbi_path / "patient_case_summary.csv", index=False)

    # =========================================================================
    # 4. DIM_ACTIVITIES (16 rows)
    # =========================================================================
    print("  - Generating dim_activities.csv...")
    act_detailed = pd.read_csv(tbl_path / "activity_frequency_detailed.csv")

    stage_mapping = {
        "ER Registration": "1. Intake & Triage",
        "ER Triage": "1. Intake & Triage",
        "ER Sepsis Triage": "1. Intake & Triage",
        "CRP": "2. Diagnostic Laboratory",
        "Leucocytes": "2. Diagnostic Laboratory",
        "LacticAcid": "2. Diagnostic Laboratory",
        "IV Liquid": "3. Acute Treatments",
        "IV Antibiotics": "3. Acute Treatments",
        "Admission NC": "4. Inpatient Ward",
        "Admission IC": "4. Inpatient Ward (ICU)",
        "Release A": "5. Hospital Disposition",
        "Release B": "5. Hospital Disposition",
        "Release C": "5. Hospital Disposition",
        "Release D": "5. Hospital Disposition",
        "Release E": "5. Hospital Disposition",
        "Return ER": "5. Hospital Disposition (Follow-up)"
    }

    act_detailed["Clinical_Stage"] = act_detailed["concept:name"].map(stage_mapping)
    dim_activities = pd.DataFrame({
        "Activity": act_detailed["concept:name"],
        "Clinical_Stage": act_detailed["Clinical_Stage"],
        "Total_Occurrences": act_detailed["total_occurrences"],
        "Unique_Cases": act_detailed["unique_cases"],
        "Case_Reach_Pct": act_detailed["case_reach_pct"],
        "Repeated_Cases_Count": act_detailed["repeated_cases_count"],
        "Rework_Rate_Pct": act_detailed["rework_rate_pct"],
        "Max_Repetitions_In_Single_Case": act_detailed["max_repetitions_in_single_case"],
        "Mean_Occurrences_Per_Case": act_detailed["mean_occurrences_per_case"]
    })
    dim_activities.to_csv(pbi_path / "dim_activities.csv", index=False)

    # Backward compatible activity frequency
    compat_act = act_detailed[["concept:name", "total_occurrences", "unique_cases"]].copy()
    compat_act.to_csv(pbi_path / "activity_frequency.csv", index=False)

    # =========================================================================
    # 5. FACT_TRANSITIONS (115 rows)
    # =========================================================================
    print("  - Generating fact_transitions.csv...")
    trans_detailed = pd.read_csv(tbl_path / "activity_transitions_detailed.csv")

    def categorize_latency(hours):
        if hours < 1.0:
            return "1. Immediate (< 1h)"
        if hours < 6.0:
            return "2. Fast (1 - 6h)"
        if hours < 24.0:
            return "3. Moderate (6 - 24h)"
        return "4. Extended (> 24h)"

    trans_detailed["Latency_Category"] = trans_detailed["average_hours"].apply(categorize_latency)
    trans_detailed["Transition_Key"] = [f"T{i:03d}" for i in range(1, len(trans_detailed) + 1)]
    trans_detailed["Transition_Name"] = trans_detailed["previous_activity"] + " -> " + trans_detailed[ACTIVITY_COL]

    fact_transitions = pd.DataFrame({
        "Transition_Key": trans_detailed["Transition_Key"],
        "Source_Activity": trans_detailed["previous_activity"],
        "Target_Activity": trans_detailed[ACTIVITY_COL],
        "Transition_Name": trans_detailed["Transition_Name"],
        "Transition_Count": trans_detailed["total_transitions"],
        "Transition_Probability": trans_detailed["transition_probability"],
        "Transition_Percentage": trans_detailed["transition_percentage"],
        "Average_Minutes": trans_detailed["average_minutes"],
        "Median_Minutes": trans_detailed["median_minutes"],
        "Average_Hours": trans_detailed["average_hours"],
        "Median_Hours": trans_detailed["median_hours"],
        "Std_Minutes": trans_detailed["std_minutes"],
        "IQR_Minutes": trans_detailed["iqr_minutes"],
        "Min_Minutes": trans_detailed["min_minutes"],
        "Max_Minutes": trans_detailed["max_minutes"],
        "Latency_Category": trans_detailed["Latency_Category"]
    })
    fact_transitions.to_csv(pbi_path / "fact_transitions.csv", index=False)

    # Backward compatible activity time differences
    compat_trans = trans_detailed[["previous_activity", ACTIVITY_COL, "total_transitions", "average_minutes", "median_minutes"]].copy()
    compat_trans.to_csv(pbi_path / "activity_time_differences.csv", index=False)

    # =========================================================================
    # 6. FACT_BOTTLENECK_BENCHMARKS
    # =========================================================================
    print("  - Generating fact_bottlenecks.csv...")
    # Calculate patient-level bottleneck timing for each case
    triage_times = sorted_df[sorted_df[ACTIVITY_COL].isin(["ER Triage", "ER Sepsis Triage"])].groupby(CASE_COL)[TIMESTAMP_COL].min()
    ab_times = sorted_df[sorted_df[ACTIVITY_COL] == "IV Antibiotics"].groupby(CASE_COL)[TIMESTAMP_COL].min()
    reg_times = sorted_df[sorted_df[ACTIVITY_COL] == "ER Registration"].groupby(CASE_COL)[TIMESTAMP_COL].min()
    adm_times = sorted_df[sorted_df[ACTIVITY_COL].isin(["Admission NC", "Admission IC"])].groupby(CASE_COL)[TIMESTAMP_COL].min()

    bottleneck_rows = []
    for cid in case_profiles[CASE_COL]:
        t_tri = triage_times.get(cid)
        t_ab = ab_times.get(cid)
        t_reg = reg_times.get(cid)
        t_adm = adm_times.get(cid)

        triage_to_ab_hrs = (t_ab - t_tri).total_seconds() / 3600.0 if (t_tri is not None and t_ab is not None and t_ab >= t_tri) else np.nan
        reg_to_adm_hrs = (t_adm - t_reg).total_seconds() / 3600.0 if (t_reg is not None and t_adm is not None and t_adm >= t_reg) else np.nan

        # Target classification
        ab_compliance = "Not Administered"
        if not np.isnan(triage_to_ab_hrs):
            if triage_to_ab_hrs <= 1.0:
                ab_compliance = "1. Golden Hour (<= 1h)"
            elif triage_to_ab_hrs <= 3.0:
                ab_compliance = "2. Sepsis Bundle (1 - 3h)"
            else:
                ab_compliance = "3. Delayed (> 3h)"

        adm_latency_cohort = "Not Admitted"
        if not np.isnan(reg_to_adm_hrs):
            if reg_to_adm_hrs <= 4.0:
                adm_latency_cohort = "1. Rapid (<= 4h)"
            elif reg_to_adm_hrs <= 8.0:
                adm_latency_cohort = "2. Standard (4 - 8h)"
            else:
                adm_latency_cohort = "3. Prolonged (> 8h)"

        bottleneck_rows.append({
            "Case_ID": cid,
            "Triage_to_Antibiotics_Hours": round(triage_to_ab_hrs, 2) if not np.isnan(triage_to_ab_hrs) else "",
            "Antibiotics_Compliance_Cohort": ab_compliance,
            "ER_to_Admission_Hours": round(reg_to_adm_hrs, 2) if not np.isnan(reg_to_adm_hrs) else "",
            "Admission_Latency_Cohort": adm_latency_cohort
        })

    fact_bottlenecks = pd.DataFrame(bottleneck_rows)
    fact_bottlenecks.to_csv(pbi_path / "fact_bottlenecks.csv", index=False)

    # =========================================================================
    # 7. DIM_DATA_QUALITY
    # =========================================================================
    print("  - Generating dim_data_quality.csv...")
    dq_rep = pd.read_csv(rep_path / "final_data_validation_report.csv")
    dim_dq = pd.DataFrame({
        "Check_ID": [f"DQ{i:02d}" for i in range(1, len(dq_rep) + 1)],
        "Validation_Check": dq_rep["Validation_Check"],
        "Result": dq_rep["Result"],
        "Status": dq_rep["Status"]
    })
    dim_dq.to_csv(pbi_path / "dim_data_quality.csv", index=False)

    summary_counts = {
        "fact_event_log": len(fact_events),
        "dim_patient_cases": len(dim_cases),
        "dim_activities": len(dim_activities),
        "fact_transitions": len(fact_transitions),
        "dim_variants": len(variants_df),
        "fact_bottlenecks": len(fact_bottlenecks),
        "dim_data_quality": len(dim_dq)
    }

    print("[Power BI Prep] Completed successfully! Generated tables:")
    for tbl, cnt in summary_counts.items():
        print(f"  - {tbl}.csv: {cnt:,} rows")

    return summary_counts


if __name__ == "__main__":
    p_root = Path(__file__).resolve().parent.parent
    p_data = p_root / "data" / "processed"
    p_tables = p_root / "outputs" / "tables"
    p_reports = p_root / "reports"
    p_pbi = p_root / "data" / "powerbi"

    prepare_powerbi_datasets(p_data, p_tables, p_reports, p_pbi)
