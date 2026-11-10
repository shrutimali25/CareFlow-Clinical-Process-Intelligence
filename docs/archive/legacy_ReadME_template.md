# 🏥 CareFlow: Clinical Pathway Process Mining

> **Domain:** Healthcare Operations & Process Analytics  
> **Tech Stack:** Google BigQuery, dbt, Python (PM4Py), Microsoft PowerBI / Looker

---

## 📌 Project Overview
Hospital administrators often face challenges understanding why Emergency Room (ER) wait times are excessively high[cite: 1]. Standard BI dashboards only display average wait times without revealing the chaotic, real-world sequence of events patients actually undergo[cite: 1]. 

**CareFlow** uses **Process Mining** algorithms to ingest raw, timestamped event logs from Electronic Health Records (EHR)[cite: 1]. It generates a visual **"Spaghetti Diagram"** of patient flows, exposing hidden operational bottlenecks and friction points[cite: 1].

---

## 🎯 Key Use Case & Impact
* **Problem Discovered:** 40% of patients were being sent back to Triage after an X-Ray due to a missing intake form[cite: 1].
* **Actionable Result:** Updating the intake form at reception **reduced average wait times by 20 minutes**[cite: 1].

---

## 🏗️ System Architecture & Key Modules

| Module | Technology | Functional Description |
| :--- | :--- | :--- |
| **Data Warehouse** | **Google BigQuery** | Highly performant storage for chronological healthcare event logs[cite: 1]. |
| **Data Transformation** | **dbt (Data Build Tool)** | Pre-processes messy EHR logs into standardized Event Log format (`Case_ID`, `Activity_Name`, `Timestamp`)[cite: 1]. |
| **Process Mining Engine** | **PM4Py (Python)** | Discovers process models (Directed Graphs/Petri Nets) from event data to analyze transition bottlenecks[cite: 1]. |
| **Process Dashboard** | **PowerBI / Looker** | Interactive visual report featuring process flow diagrams, KPIs, and drill-down filters[cite: 1, 2]. |

---

## 📁 Repository Structure

```text
careflow-process-mining/
│
├── data_simulation/       # Python script generating simulated EHR event logs
├── dbt_models/            # dbt transformation SQL models for data normalization
├── process_mining/        # PM4Py scripts for process discovery & bottleneck logic
├── dashboards/            # PowerBI (.pbix) reports and visual configuration assets
└── README.md              # Project documentation
