import pandas as pd
import json

# 1. Load dataset exactly with your column names
df = pd.read_csv("Patient_Dataset.csv")

# 2. Rename columns to cleaner internal names (optional but better for blockchain)
df = df.rename(columns={
    "Patient ID": "patient_id",
    "Timestamp": "timestamp",
    "Heart Rate (bpm)": "heart_rate",
    "Temperature (°C)": "temperature",
    "Blood Pressure (mmHg)": "blood_pressure",
    "Device ID": "device_id",
    "IP Address": "ip_address",
    "Access Type": "access_type",
    "Action": "action",
    "Target": "target"
})

# 3. Split blood pressure "116/84" into two numeric values
df[['systolic', 'diastolic']] = df['blood_pressure'].str.split('/', expand=True).astype(int)

# 4. Convert timestamp to ISO format (VERY important for blockchain logs)
df['timestamp'] = pd.to_datetime(df['timestamp'], dayfirst=True).astype(str)

# 5. Drop original blood_pressure column
df = df.drop(columns=['blood_pressure'])

# 6. Convert to JSON records for blockchain/IPFS storage
records = df.to_dict(orient='records')

# 7. Save JSON
with open("processed_dataset.json", "w") as f:
    json.dump(records, f, indent=4)

print("Preprocessing complete. Output saved to processed_dataset.json")
