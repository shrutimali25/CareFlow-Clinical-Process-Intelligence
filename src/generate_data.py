
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

# Find the CareFlow project folder
project_folder = Path(__file__).resolve().parent.parent

# Where the data will be saved
output_file = project_folder / "data" / "raw" / "hospital_event_log.csv"

random.seed(42)

rows = []

# Create data for 200 fictional patient visits
for number in range(1, 201):
    patient_id = f"P{number:03d}"

    current_time = datetime(2026, 10, 1, 8, 0)

    activities = [
        "Registration",
        "Triage",
        "Doctor Consultation",
        "Discharge"
    ]

    for activity in activities:
        current_time += timedelta(minutes=random.randint(5, 30))

        rows.append({
            "Case_ID": patient_id,
            "Activity": activity,
            "Timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S")
        })

# Create the folder if it does not exist
output_file.parent.mkdir(parents=True, exist_ok=True)

# Save all records in a CSV file
with open(output_file, "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=["Case_ID", "Activity", "Timestamp"]
    )
    writer.writeheader()
    writer.writerows(rows)

print("Patient data created successfully!")
print("Total patient visits:", 200)
print("Total event records:", len(rows))
print("Saved file:", output_file)
